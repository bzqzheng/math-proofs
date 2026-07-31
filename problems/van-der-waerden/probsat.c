/* probsat.c — probSAT stochastic local search for SAT (DIMACS in/out).
 *
 * Generic finding engine for SAT-encoded witnesses (van der Waerden colorings,
 * Erdos-Gyarfas balanced colorings, ...). Pure probSAT: pick a random unsat
 * clause, flip one of its vars with probability ~ (1+break)^-CB (break =
 * #clauses that flipping the var would newly falsify). No walk noise needed.
 *
 * Usage: probsat INSTANCE.cnf [assignment.out]
 * Env:   SEED (default 1), MAX_TRIES (default 100), MAX_FLIPS (default 1e7
 *        per try), CB (default 2.3), QUIET=1.
 * Exit:  0 = SAT (assignment written, verified by full clause scan first),
 *        1 = UNKNOWN (budget exhausted). Local search cannot prove UNSAT.
 *
 * Build: clang -O3 -o probsat probsat.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* ---- xorshift128+ PRNG (deterministic per SEED) ---- */
static unsigned long long rng_s[2];
static unsigned long long rng_next(void) {
    unsigned long long x = rng_s[0], y = rng_s[1];
    rng_s[0] = y;
    x ^= x << 23;
    rng_s[1] = x ^ y ^ (x >> 17) ^ (y >> 26);
    return rng_s[1] + y;
}
static double rng_dbl(void) { return (rng_next() >> 11) * (1.0 / 9007199254740992.0); }
static unsigned rng_below(unsigned n) { return (unsigned)(rng_next() % n); }

static int nvars, nclauses;
static int *lits;          /* flattened clause literals (0-terminated in file) */
static int *coff;          /* clause start offsets, length nclauses+1 */
static int *occ_buf, **occ; /* occurrence lists: per signed literal -> clause ids */
static int *occ_n;
static unsigned char *val; /* assignment, 1..nvars */
static int *numtrue;       /* per clause */
static int *breakc;        /* per var: clauses falsified by flipping var */
static int *unsat, *upos, unsat_n;

static double CB = 2.3;
static long MAX_FLIPS = 10000000L;
static int MAX_TRIES = 100;

#define LIT_TRUE(l) (((l) > 0) == (val[abs(l)] != 0))
#define LID(l) ((l) > 0 ? 2 * (l) - 1 : 2 * (-(l)) - 2) /* pos odd, neg even */

static void die(const char *msg) { fprintf(stderr, "probsat: %s\n", msg); exit(2); }

static void read_dimacs(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) die("cannot open input");
    char line[1 << 16];
    long decl_c = 0;
    int cap = 1 << 20, nl = 0;
    lits = malloc(cap * sizeof(int));
    coff = malloc(sizeof(int));
    int cc = 0;
    while (fgets(line, sizeof line, f)) {
        if (line[0] == 'c' || line[0] == '\n') continue;
        if (line[0] == 'p') {
            if (sscanf(line, "p cnf %d %ld", &nvars, &decl_c) != 2) die("bad p line");
            continue;
        }
        coff = realloc(coff, (cc + 2) * sizeof(int));
        coff[cc] = nl;
        char *p = line, *end;
        long v;
        while ((v = strtol(p, &end, 10)) != 0 || end != p) {
            p = end;
            if (v == 0) break;
            if (nl >= cap) { cap *= 2; lits = realloc(lits, cap * sizeof(int)); }
            lits[nl++] = (int)v;
        }
        cc++;
    }
    fclose(f);
    coff[cc] = nl;
    nclauses = cc;
    if (decl_c && decl_c != cc)
        fprintf(stderr, "probsat: warning: declared %ld clauses, read %d\n", decl_c, cc);
}

static void build_occ(void) {
    occ_n = calloc(2 * nvars + 2, sizeof(int));
    for (int c = 0; c < nclauses; c++)
        for (int i = coff[c]; i < coff[c + 1]; i++)
            occ_n[LID(lits[i])]++;
    occ_buf = malloc((size_t)(coff[nclauses]) * sizeof(int));
    occ = malloc((2 * nvars + 2) * sizeof(int *));
    int *cursor = calloc(2 * nvars + 2, sizeof(int));
    long base = 0;
    for (int s = 0; s <= 2 * nvars + 1; s++) { occ[s] = occ_buf + base; base += occ_n[s]; }
    for (int c = 0; c < nclauses; c++)
        for (int i = coff[c]; i < coff[c + 1]; i++) {
            int s = LID(lits[i]);
            occ[s][cursor[s]++] = c;
        }
    free(cursor);
}

static void unsat_add(int c) { upos[c] = unsat_n; unsat[unsat_n++] = c; }
static void unsat_del(int c) {
    int p = upos[c], last = unsat[--unsat_n];
    unsat[p] = last; upos[last] = p; upos[c] = -1;
}

static void init_state(void) {
    for (int v = 1; v <= nvars; v++) val[v] = rng_below(2);
    memset(breakc, 0, (nvars + 1) * sizeof(int));
    unsat_n = 0;
    for (int c = 0; c < nclauses; c++) {
        int t = 0, truevar = 0;
        for (int i = coff[c]; i < coff[c + 1]; i++)
            if (LIT_TRUE(lits[i])) { t++; truevar = abs(lits[i]); }
        numtrue[c] = t;
        upos[c] = -1;
        if (t == 0) unsat_add(c);
        else if (t == 1) breakc[truevar]++;
    }
}

static void flip(int v) {
    int was = val[v];
    val[v] ^= 1;
    /* occurrences where v's literal WAS true (now false) */
    int sA = was ? 2 * v - 1 : 2 * v - 2;
    for (int j = 0; j < occ_n[sA]; j++) {
        int c = occ[sA][j];
        int t = --numtrue[c];
        if (t == 0) { unsat_add(c); breakc[v]--; }
        else if (t == 1) { /* find the now-sole true literal's var */
            for (int i = coff[c]; i < coff[c + 1]; i++)
                if (LIT_TRUE(lits[i])) { breakc[abs(lits[i])]++; break; }
        }
    }
    /* occurrences where v's literal was false (now true) */
    int sB = was ? 2 * v - 2 : 2 * v - 1;
    for (int j = 0; j < occ_n[sB]; j++) {
        int c = occ[sB][j];
        int t = ++numtrue[c];
        if (t == 1) { unsat_del(c); breakc[v]++; }
        else if (t == 2) { /* find the OTHER true literal's var */
            for (int i = coff[c]; i < coff[c + 1]; i++) {
                int w = abs(lits[i]);
                if (w != v && LIT_TRUE(lits[i])) { breakc[w]--; break; }
            }
        }
    }
}

static int pick_var(int c) {
    /* roulette over literals: weight (1+break)^-CB */
    double total = 0;
    for (int i = coff[c]; i < coff[c + 1]; i++)
        total += pow(1.0 + breakc[abs(lits[i])], -CB);
    double r = rng_dbl() * total, acc = 0;
    for (int i = coff[c]; i < coff[c + 1]; i++) {
        acc += pow(1.0 + breakc[abs(lits[i])], -CB);
        if (acc >= r) return abs(lits[i]);
    }
    return abs(lits[coff[c]]);
}

static long verify(void) {
    long bad = 0;
    for (int c = 0; c < nclauses; c++) {
        int t = 0;
        for (int i = coff[c]; i < coff[c + 1]; i++) t += LIT_TRUE(lits[i]);
        if (!t) bad++;
    }
    return bad;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: probsat INSTANCE.cnf [assignment.out]\n"); return 2; }
    unsigned long long seed = 1;
    if (getenv("SEED")) seed = strtoull(getenv("SEED"), 0, 10);
    if (getenv("MAX_TRIES")) MAX_TRIES = atoi(getenv("MAX_TRIES"));
    if (getenv("MAX_FLIPS")) MAX_FLIPS = atol(getenv("MAX_FLIPS"));
    if (getenv("CB")) CB = atof(getenv("CB"));
    rng_s[0] = seed * 2862933555777941757ULL + 3037000493ULL;
    rng_s[1] = seed * 3202034522624059733ULL + 1442695040888963407ULL;
    for (int i = 0; i < 16; i++) rng_next();

    read_dimacs(argv[1]);
    build_occ();
    val = malloc(nvars + 1);
    numtrue = malloc(nclauses * sizeof(int));
    breakc = malloc((nvars + 1) * sizeof(int));
    unsat = malloc(nclauses * sizeof(int));
    upos = malloc(nclauses * sizeof(int));
    if (!getenv("QUIET"))
        fprintf(stderr, "probsat: %d vars, %d clauses, seed=%llu CB=%.2f\n",
                nvars, nclauses, seed, CB);

    long total_flips = 0;
    for (int t = 1; t <= MAX_TRIES; t++) {
        init_state();
        for (long fl = 0; fl < MAX_FLIPS; fl++) {
            if (unsat_n == 0) {
                long bad = verify(); /* full scan: trust nothing */
                if (bad == 0) {
                    printf("s SATISFIABLE\n");
                    FILE *o = argc > 2 ? fopen(argv[2], "w") : stdout;
                    if (!o) die("cannot open output");
                    for (int v = 1; v <= nvars; v++)
                        fprintf(o, "%s%d", val[v] ? "" : "-", v), fprintf(o, " ");
                    fprintf(o, "0\n");
                    if (o != stdout) fclose(o);
                    fprintf(stderr, "probsat: SAT try=%d flips=%ld (total %ld, verified)\n",
                            t, fl, total_flips + fl);
                    return 0;
                }
                fprintf(stderr, "probsat: BUG: unsat_n=0 but verify found %ld bad\n", bad);
                return 2;
            }
            int c = unsat[rng_below(unsat_n)];
            flip(pick_var(c));
        }
        total_flips += MAX_FLIPS;
        if (!getenv("QUIET"))
            fprintf(stderr, "probsat: try %d done, unsat=%d\n", t, unsat_n);
    }
    printf("s UNKNOWN\n");
    fprintf(stderr, "probsat: budget exhausted (%ld flips)\n", total_flips);
    return 1;
}
