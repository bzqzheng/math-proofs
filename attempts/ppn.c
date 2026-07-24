/* ppn.c -- exhaustive search for primary pseudoperfect numbers with exactly k prime factors.
 *
 * State: primes p_1<...<p_j chosen, N = prod p_i, A = N*(1 - sum 1/p_i)  (integer, gcd(A,N)=1).
 * With t = k-j primes still to choose we need
 *      sum_{i=1..t} 1/q_i + 1/(N*Q) = A/N,     p_j < q_1 < ... < q_t,  Q = prod q_i,
 * equivalently the "port" equation  A*Q - N*d(Q) = 1  (d = arithmetic derivative).
 * Step: A' = A*q - N, N' = N*q.
 *
 *  t=1: q = (N+1)/A must be an integer prime > p_j.
 *  t=2: A*q1*q2 - N*(q1+q2) = 1.  With s=q1+q2, p=q1*q2:  A*p = 1 + N*s, so
 *       s = s0 + A*i  and  p = p0 + N*i.  Need D = s^2-4p to be a perfect square.
 *       (equivalent divisor form: (A*q1-N)(A*q2-N) = N^2+A)
 *  t>=3: loop q over primes in ( max(p_j, N/A), t*N/A ).
 *
 * Build: cc -O3 -march=native -o ppn ppn.c -lgmp
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <gmp.h>
#include <math.h>

#define MAXK 24
#define BLK  (1u<<18)

/* ---------------- base primes for the segmented sieve ---------------- */
static uint32_t *bp; static int nbp; static uint64_t bp_lim;

static void init_base(uint64_t lim) {
    bp_lim = lim;
    uint8_t *s = calloc(lim + 1, 1);
    for (uint64_t i = 2; i * i <= lim; i++) if (!s[i]) for (uint64_t j = i * i; j <= lim; j += i) s[j] = 1;
    nbp = 0; for (uint64_t i = 2; i <= lim; i++) if (!s[i]) nbp++;
    bp = malloc(sizeof(uint32_t) * nbp);
    int c = 0; for (uint64_t i = 2; i <= lim; i++) if (!s[i]) bp[c++] = (uint32_t)i;
    free(s);
}

/* segmented prime generator over [lo,hi] */
typedef struct { uint64_t lo, hi, blo, bhi; uint8_t *buf; uint32_t idx; } psieve;

static void ps_init(psieve *g, uint8_t *buf, uint64_t lo, uint64_t hi) {
    g->lo = lo < 2 ? 2 : lo; g->hi = hi; g->buf = buf; g->blo = 1; g->bhi = 0; g->idx = 0;
}
static int ps_fill(psieve *g) {
    if (g->bhi >= g->hi) return 0;
    g->blo = (g->bhi < g->lo) ? g->lo : g->bhi + 1;
    if (g->blo > g->hi) return 0;
    g->bhi = g->blo + BLK - 1; if (g->bhi > g->hi) g->bhi = g->hi;
    uint32_t n = (uint32_t)(g->bhi - g->blo + 1);
    memset(g->buf, 1, n);
    for (int i = 0; i < nbp; i++) {
        uint64_t p = bp[i]; if (p * p > g->bhi) break;
        uint64_t st = (g->blo + p - 1) / p * p; if (st < p * p) st = p * p;
        for (uint64_t j = st; j <= g->bhi; j += p) g->buf[j - g->blo] = 0;
    }
    g->idx = 0; return 1;
}
static int ps_next(psieve *g, uint64_t *out) {
    for (;;) {
        if (g->blo > g->bhi || g->idx > (uint32_t)(g->bhi - g->blo)) { if (!ps_fill(g)) return 0; continue; }
        uint32_t i = g->idx++;
        if (g->buf[i]) { *out = g->blo + i; return 1; }
    }
}

/* ---------------- perfect-square prefilter ---------------- */
static uint8_t sq64[64], sq63[63], sq65[65], sq11[11];
static void init_sq(void) {
    for (int i = 0; i < 64; i++) sq64[i * i % 64] = 1;
    for (int i = 0; i < 63; i++) sq63[i * i % 63] = 1;
    for (int i = 0; i < 65; i++) sq65[i * i % 65] = 1;
    for (int i = 0; i < 11; i++) sq11[i * i % 11] = 1;
}

/* ---------------- search ---------------- */
static int K;
static unsigned long long nodes[MAXK], t2nodes, nsol, ndefer, t2_disc, t2_iter;
static unsigned long long work_t = 0, work_q = 0;
static uint64_t LIMIT = 3000000ULL;   /* per-node budget before deferring */
static uint64_t P[MAXK];
static uint8_t *sbuf[MAXK];
static FILE *deferf;
static int HMODE = 0;   /* 1 = t=2 level, 2 = t=3 level (double integral) */            /* 1 = heuristic accumulation only, no solving */
static double Hsum = 0.0, Hsmall = 0.0, Hmax = 0.0;
static double Wdepth[MAXK];
static double lamP(int j) { double r = 1.0; for (int i = 0; i < j; i++) r *= 1.0/(1.0 - 1.0/(double)P[i]); return r; }
/* Simpson integral over the t=1 children of a t=2 state (see ppn_heuristic.py) */
static double hinner(mpz_t N, mpz_t A, uint64_t m, double lamN) {
    mpz_t a, t1; mpz_inits(a, t1, NULL);
    mpz_fdiv_q(a, N, A);
    if (mpz_cmp_ui(a, m) < 0) mpz_set_ui(a, m);
    mpz_add_ui(a, a, 1);
    mpz_mul(t1, A, a); mpz_sub(t1, t1, N);
    double xa = mpz_get_d(t1); if (xa < 1.0) xa = 1.0;
    double xb = mpz_get_d(N);
    mpz_clears(a, t1, NULL);
    if (xb <= xa) return 0.0;
    double fN = mpz_get_d(N), fA = mpz_get_d(A);
    const int NQ = 24;
    double y0 = log(xa), y1 = log(xb), h = (y1-y0)/NQ, tot = 0.0;
    for (int i = 0; i <= NQ; i++) {
        double x = exp(y0 + i*h);
        double q = (x+fN)/fA;        double l1 = q > 2.5 ? log(q) : 1.0;
        double z = fN*(x+fN)/(fA*x); double l2 = z > 2.5 ? log(z) : 1.0;
        double w = (i == 0 || i == NQ) ? 1 : (i % 2 ? 4 : 2);
        tot += w/(l1*l2);
    }
    return lamN/fA * tot*h/3.0;
}

/* t=3 level: integrate over q1 as well.  x = A*q1 - N = A1, y = log x. */
static void hcontrib3(int j, mpz_t N, mpz_t A) {
    mpz_t a, t1, N1, A1; mpz_inits(a, t1, N1, A1, NULL);
    uint64_t m = (j > 0) ? P[j-1] : 1;
    mpz_fdiv_q(a, N, A);
    if (mpz_cmp_ui(a, m) < 0) mpz_set_ui(a, m);
    mpz_add_ui(a, a, 1);
    mpz_mul(t1, A, a); mpz_sub(t1, t1, N);
    double xa = mpz_get_d(t1); if (xa < 1.0) xa = 1.0;
    double xb = 2.0*mpz_get_d(N);
    double fN = mpz_get_d(N), fA = mpz_get_d(A), lamN = lamP(j);
    if (xb > xa) {
        const int NQ = 32;
        double y0 = log(xa), y1 = log(xb), h = (y1-y0)/NQ, tot = 0.0;
        for (int i = 0; i <= NQ; i++) {
            double x = exp(y0 + i*h);
            double q = (x+fN)/fA;
            if (q < 2.0) continue;
            uint64_t qi = (uint64_t)q;
            mpz_set_d(A1, x);
            mpz_mul_ui(N1, N, qi ? qi : 1);
            double lam1 = lamN * (1.0/(1.0 - 1.0/q));
            double E = hinner(N1, A1, qi, lam1);
            double w = (i == 0 || i == NQ) ? 1 : (i % 2 ? 4 : 2);
            tot += w * E / log(q);
        }
        Hsum += tot*h/3.0;
    }
    mpz_clears(a, t1, N1, A1, NULL);
}

static void hcontrib(int j, mpz_t N, mpz_t A) {
    double e = hinner(N, A, (j > 0) ? P[j-1] : 1, lamP(j));
    Hsum += e;
    if (mpz_cmp_ui(A, 100) <= 0) Hsmall += e;
    if (e > Hmax) Hmax = e;
}

static void emit(int j) {
    mpz_t n; mpz_init_set_ui(n, 1);
    printf("SOLUTION k=%d:", K);
    for (int i = 0; i < j; i++) { printf(" %llu", (unsigned long long)P[i]); mpz_mul_ui(n, n, P[i]); }
    gmp_printf("  n=%Zd\n", n); fflush(stdout);
    mpz_clear(n); nsol++;
}
static void emit_big(int j, mpz_t q1, mpz_t q2) {
    mpz_t n; mpz_init_set_ui(n, 1);
    printf("SOLUTION k=%d:", K);
    for (int i = 0; i < j; i++) { printf(" %llu", (unsigned long long)P[i]); mpz_mul_ui(n, n, P[i]); }
    gmp_printf(" %Zd %Zd", q1, q2); mpz_mul(n, n, q1); mpz_mul(n, n, q2);
    gmp_printf("  n=%Zd\n", n); fflush(stdout);
    mpz_clear(n); nsol++;
}
static void defer(int j, mpz_t N, mpz_t A, int t, const char *why) {
    ndefer++;
    if (deferf) {
        fprintf(deferf, "%s t=%d P=", why, t);
        for (int i = 0; i < j; i++) fprintf(deferf, "%llu,", (unsigned long long)P[i]);
        gmp_fprintf(deferf, " N=%Zd A=%Zd\n", N, A); fflush(deferf);
    }
}

/* t == 2 */
static void solve2(int j, mpz_t N, mpz_t A) {
    mpz_t q1min, smin, smax, s, p, D, w, tmp, tmp2, q1, q2, inv, span;
    mpz_inits(q1min, smin, smax, s, p, D, w, tmp, tmp2, q1, q2, inv, span, NULL);
    uint64_t m = (j > 0) ? P[j - 1] : 1;
    /* q1min = max(m, floor(N/A)) + 1 */
    mpz_fdiv_q(q1min, N, A);
    if (mpz_cmp_ui(q1min, m) < 0) mpz_set_ui(q1min, m);
    mpz_add_ui(q1min, q1min, 1);
    /* denom = A*q1min - N  must be > 0 */
    mpz_mul(tmp, A, q1min); mpz_sub(tmp, tmp, N);
    if (mpz_sgn(tmp) <= 0) { mpz_add_ui(q1min, q1min, 1); mpz_mul(tmp, A, q1min); mpz_sub(tmp, tmp, N); }
    if (mpz_sgn(tmp) <= 0) goto done;
    /* smax = q1min + (N*q1min+1)/denom */
    mpz_mul(tmp2, N, q1min); mpz_add_ui(tmp2, tmp2, 1);
    mpz_fdiv_q(smax, tmp2, tmp); mpz_add(smax, smax, q1min);
    /* smin = ceil( (2N + 2*sqrt(N^2+A)) / A ) */
    mpz_mul(tmp, N, N); mpz_add(tmp, tmp, A); mpz_sqrt(w, tmp);
    mpz_mul_ui(w, w, 2); mpz_mul_ui(tmp, N, 2); mpz_add(w, w, tmp);
    mpz_cdiv_q(smin, w, A);
    if (mpz_cmp(smin, smax) > 0) goto done;
    /* s ≡ -N^{-1} (mod A) */
    if (mpz_cmp_ui(A, 1) == 0) mpz_set_ui(inv, 0);
    else { if (!mpz_invert(inv, N, A)) goto done; mpz_neg(inv, inv); mpz_mod(inv, inv, A); }
    /* s0 = smallest s >= smin with s ≡ inv (mod A) */
    mpz_sub(tmp, inv, smin); mpz_mod(tmp, tmp, A); mpz_add(s, smin, tmp);
    if (mpz_cmp(s, smax) > 0) goto done;
    mpz_sub(span, smax, s); mpz_fdiv_q(span, span, A);       /* number of steps - 1 */

    /* alternative cost: iterate q1 over primes in (q1min-1, 2N/A] */
    mpz_mul_ui(tmp, N, 2); mpz_fdiv_q(tmp, tmp, A); mpz_sub(tmp, tmp, q1min);
    int use_iter = (mpz_cmp(tmp, span) < 0) && mpz_fits_ulong_p(tmp) && mpz_fits_ulong_p(q1min);

    if (!use_iter) {
        if (!mpz_fits_ulong_p(span) || mpz_get_ui(span) > LIMIT) { defer(j, N, A, 2, "T2SPAN"); goto done; }
        unsigned long steps = mpz_get_ui(span) + 1;
        work_t += steps; t2_disc++;
        /* p = (1+N*s)/A ; D = s^2-4p ; increments */
        mpz_mul(p, N, s); mpz_add_ui(p, p, 1); mpz_fdiv_q(p, p, A);
        mpz_mul(D, s, s); mpz_submul_ui(D, p, 4);
        /* dD = 2*A*s + A^2 - 4N ; ddD = 2A^2 */
        mpz_t dD, ddD; mpz_inits(dD, ddD, NULL);
        mpz_mul(dD, A, s); mpz_mul_ui(dD, dD, 2); mpz_mul(tmp, A, A); mpz_add(dD, dD, tmp);
        mpz_mul_ui(tmp2, N, 4); mpz_sub(dD, dD, tmp2);
        mpz_mul_ui(ddD, tmp, 2);
        /* residue trackers */
        unsigned r64 = mpz_fdiv_ui(D, 64), d64 = mpz_fdiv_ui(dD, 64), e64 = mpz_fdiv_ui(ddD, 64);
        unsigned r63 = mpz_fdiv_ui(D, 63), d63 = mpz_fdiv_ui(dD, 63), e63 = mpz_fdiv_ui(ddD, 63);
        unsigned r65 = mpz_fdiv_ui(D, 65), d65 = mpz_fdiv_ui(dD, 65), e65 = mpz_fdiv_ui(ddD, 65);
        unsigned r11 = mpz_fdiv_ui(D, 11), d11 = mpz_fdiv_ui(dD, 11), e11 = mpz_fdiv_ui(ddD, 11);
        for (unsigned long i = 0; i < steps; i++) {
            if (sq64[r64] && sq63[r63] && sq65[r65] && sq11[r11]) {
                mpz_sqrt(w, D);
                mpz_mul(tmp, w, w);
                if (mpz_cmp(tmp, D) == 0) {
                    mpz_sub(q1, s, w); mpz_sub(q2, s, w);
                    if (mpz_even_p(q1)) {
                        mpz_fdiv_q_2exp(q1, q1, 1); mpz_add(q2, s, w); mpz_fdiv_q_2exp(q2, q2, 1);
                        if (mpz_cmp_ui(q1, m) > 0 && mpz_cmp(q1, q2) < 0 &&
                            mpz_probab_prime_p(q1, 30) && mpz_probab_prime_p(q2, 30))
                            emit_big(j, q1, q2);
                    }
                }
            }
            mpz_add(D, D, dD); mpz_add(dD, dD, ddD); mpz_add(s, s, A);
            r64 = (r64 + d64) & 63; d64 = (d64 + e64) & 63;
            r63 = (r63 + d63) % 63; d63 = (d63 + e63) % 63;
            r65 = (r65 + d65) % 65; d65 = (d65 + e65) % 65;
            r11 = (r11 + d11) % 11; d11 = (d11 + e11) % 11;
        }
        mpz_clears(dD, ddD, NULL);
    } else {
        unsigned long width = mpz_get_ui(tmp);
        if (width > LIMIT) { defer(j, N, A, 2, "T2ITER"); goto done; }
        work_q += width; t2_iter++;
        uint64_t lo = mpz_get_ui(q1min), hi = lo + width;
        psieve g; ps_init(&g, sbuf[j], lo, hi);
        uint64_t q; mpz_t M; mpz_init(M);
        mpz_mul(M, N, N); mpz_add(M, M, A);      /* (A q1 - N) | N^2 + A */
        while (ps_next(&g, &q)) {
            mpz_mul_ui(tmp, A, q); mpz_sub(tmp, tmp, N);      /* d = A q - N > 0 */
            if (mpz_sgn(tmp) <= 0) continue;
            if (!mpz_divisible_p(M, tmp)) continue;
            mpz_divexact(tmp2, M, tmp);                        /* = A q2 - N */
            mpz_add(tmp2, tmp2, N);
            if (!mpz_divisible_p(tmp2, A)) continue;
            mpz_divexact(q2, tmp2, A);
            mpz_set_ui(q1, q);
            if (mpz_cmp(q2, q1) > 0 && mpz_probab_prime_p(q1, 30) && mpz_probab_prime_p(q2, 30))
                emit_big(j, q1, q2);
        }
        mpz_clear(M);
    }
done:
    mpz_clears(q1min, smin, smax, s, p, D, w, tmp, tmp2, q1, q2, inv, span, NULL);
}

static void dfs(int j, mpz_t N, mpz_t A, int t);

static void step(int j, mpz_t N, mpz_t A, int t, uint64_t q) {
    mpz_t N2, A2; mpz_inits(N2, A2, NULL);
    mpz_mul_ui(A2, A, q); mpz_sub(A2, A2, N);
    if (mpz_sgn(A2) > 0) {
        mpz_mul_ui(N2, N, q);
        /* prune: need A2/N2 <= (t-1)/nextprime(q); q+1 is a safe lower bound for nextprime(q) */
        mpz_t l, r; mpz_inits(l, r, NULL);
        mpz_mul_ui(l, A2, q + 1); mpz_mul_ui(r, N2, t - 1);
        if (mpz_cmp(l, r) <= 0) { P[j] = q; dfs(j + 1, N2, A2, t - 1); }
        mpz_clears(l, r, NULL);
    }
    mpz_clears(N2, A2, NULL);
}

static void dfs(int j, mpz_t N, mpz_t A, int t) {
    nodes[j]++;
    if (HMODE == 3 && j > 0) {
        double R = mpz_get_d(N)/mpz_get_d(A);
        if (R > 2.5) Wdepth[j] += lamP(j)/mpz_get_d(A)/log(R);
    }
    if (t == 1) {
        mpz_t q; mpz_init(q); mpz_add_ui(q, N, 1);
        if (mpz_divisible_p(q, A)) {
            mpz_divexact(q, q, A);
            if (mpz_cmp_ui(q, (j > 0) ? P[j - 1] : 1) > 0 && mpz_probab_prime_p(q, 30)) {
                mpz_t one; mpz_init_set_ui(one, 1); emit_big(j, q, one); mpz_clear(one);
            }
        }
        mpz_clear(q); return;
    }
    if (t == 3 && HMODE == 2 && 0) { hcontrib3(j, N, A); return; }
    if (t == 2) {
        t2nodes++;
        if ((t2nodes & 0xFFFFFF) == 0) {
            fprintf(stderr, "[t2=%lluM defer=%llu sols=%llu] P=", t2nodes >> 20, ndefer, nsol);
            for (int i = 0; i < j; i++) fprintf(stderr, "%llu,", (unsigned long long)P[i]);
            fprintf(stderr, "\n"); fflush(stderr);
        }
        if (HMODE) hcontrib(j, N, A); else solve2(j, N, A);
        return;
    }
    mpz_t lo, hi; mpz_inits(lo, hi, NULL);
    mpz_fdiv_q(lo, N, A);
    if (j > 0 && mpz_cmp_ui(lo, P[j - 1]) < 0) mpz_set_ui(lo, P[j - 1]);
    mpz_mul_ui(hi, N, t); mpz_sub_ui(hi, hi, 1); mpz_fdiv_q(hi, hi, A);
    if (mpz_cmp(hi, lo) > 0 && mpz_fits_ulong_p(hi)) {
        uint64_t l = mpz_get_ui(lo), h = mpz_get_ui(hi);
        if (h - l > LIMIT) defer(j, N, A, t, "LOOP");
        else {
            psieve g; ps_init(&g, sbuf[j], l + 1, h);
            uint64_t q;
            while (ps_next(&g, &q)) step(j, N, A, t, q);
        }
    } else if (mpz_cmp(hi, lo) > 0) defer(j, N, A, t, "BIGLOOP");
    mpz_clears(lo, hi, NULL);
}

/* re-run states listed in a defer file, with the (large) budget given on the command line */
static void run_deferfile(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "cannot open %s\n", path); exit(1); }
    char line[8192];
    mpz_t N, A; mpz_inits(N, A, NULL);
    unsigned long long done = 0;
    while (fgets(line, sizeof line, f)) {
        char *tp = strstr(line, "t="), *pp = strstr(line, "P="),
             *np = strstr(line, "N="), *ap = strstr(line, "A=");
        if (!tp || !pp || !np || !ap) continue;
        int t = atoi(tp + 2);
        int j = 0;
        for (char *c = pp + 2; *c && *c != ' '; ) {
            P[j++] = strtoull(c, &c, 10);
            if (*c == ',') c++;
        }
        if (j && P[j-1] == 0) j--;                 /* trailing comma */
        char *e;
        for (e = np + 2; *e && *e != ' '; e++) ;
        char save = *e; *e = 0; mpz_set_str(N, np + 2, 10); *e = save;
        for (e = ap + 2; *e && *e != ' ' && *e != '\n'; e++) ;
        save = *e; *e = 0; mpz_set_str(A, ap + 2, 10); *e = save;
        dfs(j, N, A, t);
        if ((++done % 2000) == 0) { fprintf(stderr, "  [resolved %llu, deferred %llu]\n", done, ndefer); fflush(stderr); }
    }
    mpz_clears(N, A, NULL); fclose(f);
    fprintf(stderr, "processed %llu states\n", done);
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s k [prefix,comma,sep] [deferfile] [limit]\n", argv[0]); return 1; }
    K = atoi(argv[1]);
    init_base(10000000ULL); init_sq();
    for (int i = 0; i < MAXK; i++) sbuf[i] = malloc(BLK);
    if (argc > 3 && argv[3][0]) deferf = fopen(argv[3], "w");
    if (argc > 4) LIMIT = strtoull(argv[4], NULL, 10);
    if (getenv("HMODE")) HMODE = atoi(getenv("HMODE"));
    mpz_t N, A; mpz_init_set_ui(N, 1); mpz_init_set_ui(A, 1);
    int j = 0;
    if (argc > 2 && argv[2][0] && argv[2][0] != '@') {
        char *s = strdup(argv[2]), *tok = strtok(s, ",");
        while (tok) {
            uint64_t q = strtoull(tok, NULL, 10);
            mpz_t A2; mpz_init(A2); mpz_mul_ui(A2, A, q); mpz_sub(A2, A2, N);
            mpz_set(A, A2); mpz_clear(A2); mpz_mul_ui(N, N, q);
            P[j++] = q; tok = strtok(NULL, ",");
        }
    }
    if (argc > 2 && argv[2][0] == '@') run_deferfile(argv[2] + 1);
    else dfs(j, N, A, K - j);
    printf("k=%d done nodes=", K);
    for (int i = 0; i <= K; i++) printf("%llu%s", nodes[i], i == K ? "" : ",");
    printf(" t2nodes=%llu t2_disc=%llu t2_iter=%llu work_disc=%llu work_iter=%llu sols=%llu deferred=%llu\n",
           t2nodes, t2_disc, t2_iter, work_t, work_q, nsol, ndefer);
    if (HMODE == 3) {
        printf("W by depth:");
        for (int i = 1; i < K; i++) printf(" %.5g", Wdepth[i]);
        printf("\nratios:");
        for (int i = 2; i < K; i++) printf(" %.4f", Wdepth[i-1] > 0 ? Wdepth[i]/Wdepth[i-1] : 0);
        printf("\n");
    }
    if (HMODE) printf("HEURISTIC Sigma = %.6f  small-A(<=100) = %.6f  max-node = %.6f\n", Hsum, Hsmall, Hmax);
    return 0;
}
