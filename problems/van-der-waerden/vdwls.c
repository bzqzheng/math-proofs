/* vdwls.c — native local search for van der Waerden colorings.
 *
 * Searches r-colorings of [n] with NO monochromatic k-term AP, using the
 * problem-native move set (recolor one integer), not a CNF encoding — the
 * approach behind the published records (Rabung–Lotts, Heule). Score =
 * #monochromatic k-APs, maintained incrementally; move = pick a random mono
 * AP, pick a member, recolor it to the color minimizing new mono APs
 * (min-conflicts with NOISE randomization).
 *
 * Usage: vdwls r k n [coloring.out]
 * Env:   SEED (1), MAX_TRIES (100), MAX_STEPS (1e7 per try), NOISE (0.1),
 *        QUIET=1.
 * Exit:  0 = coloring found (verified by full rescan before printing),
 *        1 = budget exhausted. Local search cannot prove nonexistence.
 *
 * Build: clang -O3 -o vdwls vdwls.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* ---- xorshift128+ ---- */
static unsigned long long rng_s[2];
static unsigned long long rng_next(void) {
    unsigned long long x = rng_s[0], y = rng_s[1];
    rng_s[0] = y;
    x ^= x << 23;
    rng_s[1] = x ^ y ^ (x >> 17) ^ (y >> 26);
    return rng_s[1] + y;
}
static unsigned rng_below(unsigned n) { return (unsigned)(rng_next() % n); }

static int R, K, N;
static int naps;            /* number of k-APs */
static int *ap_a, *ap_d;    /* AP j: terms a, a+d, ..., a+(k-1)d */
static unsigned char *cnt;  /* cnt[j*R + c]: how many terms of AP j have color c */
static int *inc_off, *inc_list; /* CSR: APs containing integer i */
static unsigned char *col;  /* col[i] in [0,R), i in [1..N] */
static unsigned *wt;        /* SAPS-style per-AP weights (persist across tries) */
static long mono_w;         /* weighted #mono APs (the move objective) */
static long mono_raw;       /* unweighted #mono APs (the true objective) */

static double NOISE = 0.1;
static double CBW = 3.0;       /* probSAT weight exponent for color choice */
static long PLATEAU = 200000;  /* steps without improvement -> perturb */
static long WUP = 0;             /* weight-update period; 0 = SAPS off (default:
                                    the unweighted dynamics solve more instances;
                                    enable for hard records, e.g. WUP=10000) */
static int TABU = 10;          /* base tabu tenure (steps) */
static int MAKEMODE = 1;       /* 1: score break-make; 0: break-only (some
                                  instances prefer each — tune per target) */
static long MAX_STEPS = 10000000L;
static int MAX_TRIES = 100;
static int *tabu;              /* tabu[i] = step until integer i is frozen */

static void build(void) {
    naps = 0;
    for (int d = 1; d <= (N - 1) / (K - 1); d++)
        naps += N - (K - 1) * d;
    ap_a = malloc(naps * sizeof(int));
    ap_d = malloc(naps * sizeof(int));
    int j = 0;
    for (int d = 1; d <= (N - 1) / (K - 1); d++)
        for (int a = 1; a + (K - 1) * d <= N; a++) { ap_a[j] = a; ap_d[j] = d; j++; }
    /* CSR incidence: counts first, then shift right, then prefix-sum so that
       inc_off[v] = start offset of integer v's AP list = sum_{u<v} cnt[u] */
    inc_off = calloc(N + 2, sizeof(int));
    for (j = 0; j < naps; j++)
        for (int t = 0; t < K; t++)
            inc_off[ap_a[j] + t * ap_d[j]]++;
    for (int v = N + 1; v >= 2; v--) inc_off[v] = inc_off[v - 1];
    inc_off[1] = 0;
    for (int v = 2; v <= N + 1; v++) inc_off[v] += inc_off[v - 1];
    inc_list = malloc((size_t)inc_off[N + 1] * sizeof(int));
    int *cur = malloc((N + 2) * sizeof(int));
    memcpy(cur, inc_off, (N + 2) * sizeof(int));
    for (j = 0; j < naps; j++)
        for (int t = 0; t < K; t++)
            inc_list[cur[ap_a[j] + t * ap_d[j]]++] = j;
    free(cur);
    cnt = calloc((size_t)naps * R, 1);
    col = malloc(N + 1);
    tabu = calloc(N + 1, sizeof(int));
    wt = malloc((size_t)naps * sizeof(unsigned));
    for (int j = 0; j < naps; j++) wt[j] = 1;
    if (inc_off[N + 1] != K * naps) {
        fprintf(stderr, "vdwls: FATAL: CSR build broken (%d != %d)\n",
                inc_off[N + 1], K * naps);
        return;
    }
}

static long full_score(void) { /* from scratch — also the verification pass */
    memset(cnt, 0, (size_t)naps * R);
    for (int j = 0; j < naps; j++)
        for (int t = 0; t < K; t++)
            cnt[(size_t)j * R + col[ap_a[j] + t * ap_d[j]]]++;
    long m = 0;
    for (int j = 0; j < naps; j++)
        for (int c = 0; c < R; c++)
            if (cnt[j * R + c] == K) { m++; break; }
    return m;
}

static void init_random(void) {
    for (int i = 1; i <= N; i++) col[i] = rng_below(R);
    mono_raw = full_score();
    mono_w = 0;
    for (int j = 0; j < naps; j++)
        for (int c = 0; c < R; c++)
            if (cnt[j * R + c] == K) { mono_w += wt[j]; break; }
}

/* recolor integer i from a=col[i] to b; caller computed this is the move */
static void apply_move(int i, int b) {
    int a = col[i];
    for (int p = inc_off[i]; p < inc_off[i + 1]; p++) {
        int j = inc_list[p];
        unsigned char *cj = &cnt[(size_t)j * R];
        if (cj[a] == K) { mono_w -= wt[j]; mono_raw--; }
        cj[a]--;
        cj[b]++;
        if (cj[b] == K) { mono_w += wt[j]; mono_raw++; }
    }
    col[i] = b;
}

static int step(long st) {
    if (mono_raw == 0) return 0;
    /* pick a random mono AP (rejection: mono fraction is high early) */
    int j = -1;
    for (int tries = 0; tries < 64; tries++) {
        int cand = rng_below(naps);
        unsigned char *cj = &cnt[(size_t)cand * R];
        int is_mono = 0;
        for (int c = 0; c < R; c++) if (cj[c] == K) { is_mono = 1; break; }
        if (is_mono) { j = cand; break; }
    }
    if (j < 0) { /* mono APs too rare for rejection: scan and collect one */
        long seen = 0, pick = rng_below(mono_raw);
        for (int c2 = 0; c2 < naps; c2++) {
            unsigned char *cj = &cnt[(size_t)c2 * R];
            int is_mono = 0;
            for (int c = 0; c < R; c++) if (cj[c] == K) { is_mono = 1; break; }
            if (is_mono) { if (seen++ == pick) { j = c2; break; } }
        }
    }
    if (j < 0) return 0;
    /* choose the (member, new color) move jointly, probSAT-weighted on cost
       (cost = #APs through the member that would become mono). At R=2 this
       is classic WalkSAT variable scoring; at R>=3 it picks member+color. */
    int mi = -1, mc = -1;
    if (rng_below(1000) < (unsigned)(NOISE * 1000)) {
        int t = rng_below(K);
        mi = ap_a[j] + t * ap_d[j];
        do { mc = rng_below(R); } while (mc == col[mi]);
    } else {
        double wtot = 0;
        double w[K][15];
        for (int t = 0; t < K; t++) {
            int i = ap_a[j] + t * ap_d[j], a = col[i];
            if (tabu[i] > st && mono_raw > 1) { for (int c = 0; c < R; c++) w[t][c] = 0; continue; }
            long make = 0;
            if (MAKEMODE)
                for (int p = inc_off[i]; p < inc_off[i + 1]; p++) {
                    unsigned char *cj = &cnt[(size_t)inc_list[p] * R];
                    if (cj[a] == K) make += wt[inc_list[p]];
                }
            for (int c = 0; c < R; c++) {
                if (c == a) { w[t][c] = 0; continue; }
                long brk = 0;
                for (int p = inc_off[i]; p < inc_off[i + 1]; p++) {
                    unsigned char *cj = &cnt[(size_t)inc_list[p] * R];
                    if (cj[c] == K - 1) brk += wt[inc_list[p]];
                }
                long net = brk - make;          /* net new weighted mono */
                w[t][c] = pow(1.0 + (net > 0 ? (double)net : 0.0), -CBW);
                wtot += w[t][c];
            }
        }
        double r = (rng_next() >> 11) * (1.0 / 9007199254740992.0) * wtot, acc = 0;
        for (int t = 0; t < K && mi < 0; t++)
            for (int c = 0; c < R; c++) {
                acc += w[t][c];
                if (acc >= r) { mi = ap_a[j] + t * ap_d[j]; mc = c; break; }
            }
        if (mi < 0) { int t = rng_below(K); mi = ap_a[j] + t * ap_d[j];
                      do { mc = rng_below(R); } while (mc == col[mi]); }
    }
    apply_move(mi, mc);
    tabu[mi] = (int)(st + TABU + rng_below(TABU > 1 ? TABU : 1));
    return 1;
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: vdwls r k n [coloring.out]\n"); return 2; }
    R = atoi(argv[1]); K = atoi(argv[2]); N = atoi(argv[3]);
    unsigned long long seed = 1;
    if (getenv("SEED")) seed = strtoull(getenv("SEED"), 0, 10);
    if (getenv("MAX_TRIES")) MAX_TRIES = atoi(getenv("MAX_TRIES"));
    if (getenv("MAX_STEPS")) MAX_STEPS = atol(getenv("MAX_STEPS"));
    if (getenv("NOISE")) NOISE = atof(getenv("NOISE"));
    if (getenv("CBW")) CBW = atof(getenv("CBW"));
    if (getenv("PLATEAU")) PLATEAU = atol(getenv("PLATEAU"));
    if (getenv("TABU")) TABU = atoi(getenv("TABU"));
    if (getenv("WUP")) WUP = atol(getenv("WUP"));
    if (getenv("MAKEMODE")) MAKEMODE = atoi(getenv("MAKEMODE"));
    rng_s[0] = seed * 2862933555777941757ULL + 3037000493ULL;
    rng_s[1] = seed * 3202034522624059733ULL + 1442695040888963407ULL;
    for (int i = 0; i < 16; i++) rng_next();
    if (R < 2 || R > 15 || K < 2 || N < K) { fprintf(stderr, "bad params\n"); return 2; }
    build();
    if (!getenv("QUIET"))
        fprintf(stderr, "vdwls: W(%d,%d) > %d — %d APs, seed=%llu NOISE=%.3f\n",
                R, K, N, naps, seed, NOISE);

    for (int tr = 1; tr <= MAX_TRIES; tr++) {
        init_random();
        long best = mono_raw, since_improve = 0;
        for (long st = 0; st < MAX_STEPS; st++) {
            if (mono_raw == 0) {
                long check = full_score(); /* trust nothing: full rescan */
                if (check == 0) {
                    printf("s COLORING-FOUND W(%d,%d) > %d\n", R, K, N);
                    FILE *o = argc > 4 ? fopen(argv[4], "w") : stdout;
                    if (!o) { fprintf(stderr, "cannot open output\n"); return 2; }
                    for (int i = 1; i <= N; i++) fprintf(o, "%d\n", col[i]);
                    if (o != stdout) fclose(o);
                    fprintf(stderr, "vdwls: FOUND try=%d step=%ld (verified)\n", tr, st);
                    return 0;
                }
                fprintf(stderr, "vdwls: BUG: incremental 0 but rescan %ld\n", check);
                return 2;
            }
            if (mono_raw < best) {
                best = mono_raw;
                since_improve = 0;
                if (!getenv("QUIET") && best <= 20)
                    fprintf(stderr, "vdwls: try=%d step=%ld mono=%ld\n", tr, st, best);
            } else if (++since_improve >= PLATEAU) {
                /* iterated local search: perturb ~2% of integers */
                int np = 1 + (int)(0.02 * N);
                for (int q = 0; q < np; q++) {
                    int i = 1 + rng_below(N), b2 = rng_below(R);
                    if (b2 != col[i]) apply_move(i, b2);
                }
                since_improve = 0;
            }
            if (WUP > 0 && st % WUP == WUP - 1) {
                /* SAPS-style weight bump on currently-mono APs */
                for (int j2 = 0; j2 < naps; j2++) {
                    unsigned char *cj = &cnt[(size_t)j2 * R];
                    int is_mono = 0;
                    for (int c = 0; c < R; c++) if (cj[c] == K) { is_mono = 1; break; }
                    if (is_mono) { wt[j2]++; mono_w++; }
                }
            }
            if (getenv("DEBUG") && st % 100000 == 99999) {
                long fs = full_score();
                fprintf(stderr, "DEBUG try=%d step=%ld incr=%ld full=%ld %s\n",
                        tr, st, mono_raw, fs, fs == mono_raw ? "sync" : "DRIFT!");
                mono_raw = fs; /* resync to keep the run meaningful */
                mono_w = 0;
                for (int j2 = 0; j2 < naps; j2++)
                    for (int c = 0; c < R; c++)
                        if (cnt[j2 * R + c] == K) { mono_w += wt[j2]; break; }
            }
            step(st);
        }
        if (!getenv("QUIET"))
            fprintf(stderr, "vdwls: try %d done, best=%ld final=%ld\n", tr, best, mono_raw);
    }
    printf("s UNKNOWN\n");
    return 1;
}
