/*
 * search_odd_weird.c — C port of search_odd_weird.py (v2 — bounded branching).
 *
 * Faithful port of the Python DFS semantics. n is weird iff
 * delta = sigma(n) - 2n > 0 AND delta is not a sum of distinct proper
 * divisors of n. See the Python file / README.md for the math.
 *
 * Port fidelity notes (differences from Python are documented here):
 *
 * - Integers: n, sigma, and all intermediate products use unsigned __int128.
 *   Every quantity the DFS materializes is exactly sigma(m) or m for some
 *   m <= N_CAP, or a product bounded by N_CAP, so 128 bits is far more than
 *   enough for N_CAP <= 1e36 (refused above that; sigma(m) < ~10*m must fit).
 *   Overflow is avoided structurally: every Python comparison `a*b <= N_CAP`
 *   is evaluated as `a <= N_CAP / b` (exact integer equivalence), and
 *   sigma(p^a) = (p^(a+1)-1)/(p-1) is accumulated as 1 + p + ... + p^a,
 *   which is the identical integer but never forms the overshooting product.
 *
 * - Primes: odd-only bit sieve below 2^26 (covers all primes that actually
 *   appear in realistic runs; the DFS prunes p to small values). Above the
 *   sieve, next_prime() uses trial division by small primes + Miller-Rabin:
 *     * n < 2^64: deterministic Miller-Rabin with the 7 bases
 *       {2, 325, 9375, 28178, 450775, 9780504, 1795265022} — exact primality,
 *       identical decisions to sympy.nextprime.
 *     * n >= 2^64: PROBABLE-prime test with the first 16 prime bases
 *       (2..53). No known composite passes 16+ MR bases; should one slip
 *       through it would only make the DFS treat a composite as prime,
 *       slightly altering search coverage — witnesses are re-verified
 *       exactly in Python afterwards (see task spec). sympy itself uses
 *       Baillie-PSW for large arguments, also a probable-prime test.
 *
 * - abund = sigma/n as double: for sig, n < 2^53 this is one IEEE double
 *   division — bit-identical to Python's int/int. Above 2^53 we compute
 *   q + r/n via 128-bit divmod, within ~1ulp of Python's correctly-rounded
 *   result; this only feeds the `> 2` heuristic prune, never correctness.
 *
 * - The `(p/(p-1))^(km+1)` prune uses C pow() on doubles, matching CPython
 *   float.__pow__ (both call the system libm pow on the same doubles).
 *
 * - Deadline is checked every 4096 nodes instead of Python's every 1000
 *   (cheap bitmask vs. Python's modulo) — only affects WHERE a time-limited
 *   run stops, never an un-throttled run. Progress prints every 10M nodes
 *   (Python: 1M). All other counts are node-for-node identical.
 *
 * Env vars (same interface as Python): N_CAP, DELTA_MAX, ALLOW_EVEN, TIME_BUDGET.
 * N_CAP/DELTA_MAX are parsed as int(float(env)) like Python — note the
 * Python default N_CAP=10**24 is the exact integer, while N_CAP=1e24 in the
 * environment parses to int(float("1e24")) = 999999999999999983222784. Same
 * here (strtod + truncation).
 *
 * Build: clang -O3 -o search_odd_weird search_odd_weird.c -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <time.h>

typedef unsigned __int128 u128;

/* ----------------------------- parameters ------------------------------- */

#define SIEVE_MAX (1u << 26) /* 67,108,864: primes below this come from the sieve */
#define MAXDEPTH 64          /* > omega(m) for any m <= 1e36 */

/* Safety clamps: keep every materialized value far inside u128 range.
 * sigma(m) < ~10*m for m in our range, and 10*1e36 << 2^128 (~3.4e38). */
#define N_CAP_CLAMP     ((u128)1000000000 * 1000000000 * 1000000000 * 1000000000) /* 1e36 */
#define DELTA_MAX_CLAMP (((u128)1) << 40) /* bitset would need DELTA_MAX/8 bytes */

static u128 N_CAP;      /* default: exact 10**24, as in Python */
static u128 DELTA_MAX;  /* default: exact 10**7, as in Python */
static int ALLOW_EVEN;
static long TIME_BUDGET;
static long MIN_DEPTH;  /* 0 = off; weird-eligibility requires depth >= MIN_DEPTH
                         * (Liddy–Riedl: odd weird => >= 6 distinct primes) */

/* ------------------------------ state ----------------------------------- */

static double t0;
static uint64_t nodes = 0, tested = 0;
static int deadline_hit = 0;

typedef struct { u128 p; int a; } fac_t;
static fac_t fac[MAXDEPTH];

typedef struct { u128 n, delta; int depth; fac_t f[MAXDEPTH]; } found_t;
static found_t *found = NULL;
static size_t nfound = 0, found_cap = 0;

/* divisor scratch buffers (grown on demand) */
static uint64_t *ds = NULL, *ext = NULL; /* divisors kept are <= delta < 2^64 */
static size_t ds_cap = 0, ext_cap = 0;
static uint64_t *bits = NULL; /* subset-sum bitset, DELTA_MAX bits */

/* --------------------------- small helpers ------------------------------ */

static double now(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

static void u128_str(char *buf, u128 v) {
    char tmp[64];
    int i = 0, j = 0;
    if (v == 0) { buf[0] = '0'; buf[1] = 0; return; }
    while (v) { tmp[i++] = (char)('0' + (int)(v % 10)); v /= 10; }
    while (i) buf[j++] = tmp[--i];
    buf[j] = 0;
}

/* Python-style thousands separators: 239115 -> "239,115" */
static void u64_commas(char *buf, uint64_t v) {
    char tmp[32];
    int len = snprintf(tmp, sizeof tmp, "%llu", (unsigned long long)v);
    int j = 0;
    for (int i = 0; i < len; i++) {
        if (i && (len - i) % 3 == 0) buf[j++] = ',';
        buf[j++] = tmp[i];
    }
    buf[j] = 0;
}

static void fprint_fac(FILE *out, const fac_t *f, int depth) {
    char b[64];
    fputc('[', out);
    for (int i = 0; i < depth; i++) {
        u128_str(b, f[i].p);
        fprintf(out, "%s(%s, %d)", i ? ", " : "", b, f[i].a);
    }
    fputc(']', out);
}

/* sig/n as double. Bit-identical to Python int/int below 2^53; above that
 * within ~1ulp (feeds only the heuristic prune, never the weird test). */
static double ratio(u128 sig, u128 n) {
    if (sig < ((u128)1 << 53) && n < ((u128)1 << 53))
        return (double)(uint64_t)sig / (double)(uint64_t)n;
    u128 q = sig / n, r = sig % n;
    return (double)q + (double)r / (double)n;
}

/* ------------------------------- sieve ---------------------------------- */
/* bit i (i >= 0) set <=> 2i+1 is prime; covers odd n < SIEVE_MAX */

static uint64_t sieve_bits[SIEVE_MAX / 2 / 64];

static void sieve_init(void) {
    memset(sieve_bits, 0xFF, sizeof sieve_bits);
    sieve_bits[0] &= ~1ULL; /* 1 is not prime */
    for (uint64_t p = 3; p * p < SIEVE_MAX; p += 2)
        if ((sieve_bits[p >> 7] >> ((p >> 1) & 63)) & 1)
            for (uint64_t m = p * p; m < SIEVE_MAX; m += 2 * p)
                sieve_bits[m >> 7] &= ~(1ULL << ((m >> 1) & 63));
}

/* --------------------------- Miller-Rabin ------------------------------- */

static uint64_t powmod64(uint64_t a, uint64_t e, uint64_t m) {
    uint64_t r = 1 % m;
    a %= m;
    while (e) {
        if (e & 1) r = (uint64_t)(((u128)r * a) % m);
        a = (uint64_t)(((u128)a * a) % m);
        e >>= 1;
    }
    return r;
}

static int mr64(uint64_t n, uint64_t a) {
    if (a % n == 0) return 1;
    uint64_t d = n - 1;
    int s = 0;
    while (!(d & 1)) { d >>= 1; s++; }
    uint64_t x = powmod64(a, d, n);
    if (x == 1 || x == n - 1) return 1;
    for (int i = 1; i < s; i++) {
        x = (uint64_t)(((u128)x * x) % n);
        if (x == n - 1) return 1;
    }
    return 0;
}

/* 128-bit modular arithmetic via overflow-safe add-and-double.
 * Only used for probable-prime testing above 2^64, hence rare. */
static inline u128 addmod(u128 a, u128 b, u128 m) {
    u128 s = a + b;                       /* a, b < m */
    if (s >= a) return (s >= m) ? s - m : s;  /* no wrap: a+b < 2m */
    return s - m;                         /* wrapped: wraps again to a+b-m */
}

static u128 mulmod128(u128 a, u128 b, u128 m) {
    u128 r = 0;
    a %= m;
    while (b) {
        if (b & 1) r = addmod(r, a, m);
        a = addmod(a, a, m);
        b >>= 1;
    }
    return r;
}

static u128 powmod128(u128 a, u128 e, u128 m) {
    u128 r = 1 % m;
    a %= m;
    while (e) {
        if (e & 1) r = mulmod128(r, a, m);
        a = mulmod128(a, a, m);
        e >>= 1;
    }
    return r;
}

static int mr128(u128 n, u128 a) {
    if (a % n == 0) return 1;
    u128 d = n - 1;
    int s = 0;
    while (!(d & 1)) { d >>= 1; s++; }
    u128 x = powmod128(a, d, n);
    if (x == 1 || x == n - 1) return 1;
    for (int i = 1; i < s; i++) {
        x = mulmod128(x, x, n);
        if (x == n - 1) return 1;
    }
    return 0;
}

/* Matches sympy.isprime decisions for all n < 2^64 (deterministic MR);
 * probable-prime with 16 bases above that (see header comment). */
static int is_prime(u128 n) {
    static const uint8_t smallp[] = { 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37,
                                      41, 43, 47, 53, 59, 61, 67, 71, 73, 79,
                                      83, 89, 97 };
    static const uint64_t det7[7] = { 2, 325, 9375, 28178, 450775,
                                      9780504, 1795265022 };
    if (n < 2) return 0;
    if (n == 2) return 1;
    if (!(n & 1)) return 0;
    if (n < SIEVE_MAX) return (int)((sieve_bits[n >> 7] >> ((n >> 1) & 63)) & 1);
    for (unsigned i = 0; i < sizeof smallp; i++)
        if (n % smallp[i] == 0) return 0; /* n >= SIEVE_MAX > 97, so n != p */
    if (n < ((u128)1 << 64)) {
        uint64_t m = (uint64_t)n;
        for (int i = 0; i < 7; i++)
            if (!mr64(m, det7[i])) return 0;
        return 1;
    }
    /* n >= 2^64: probable-prime, 25 bases (2 plus the 24 odd primes < 100);
     * >= 16 bases per spec. See header comment for why this is acceptable. */
    for (unsigned i = 0; i < sizeof smallp; i++)
        if (!mr128(n, smallp[i])) return 0;
    return mr128(n, 2);
}

/* next prime strictly greater than p (sympy.nextprime semantics) */
static u128 next_prime(u128 p) {
    if (p < 2) return 2;
    if (p == 2) return 3;
    u128 c = (p & 1) ? p + 2 : p + 1; /* smallest odd candidate > p */
    if (c < SIEVE_MAX) {
        uint64_t i = (uint64_t)(c >> 1);
        while (i < SIEVE_MAX / 2) {
            uint64_t w = sieve_bits[i >> 6] & (~0ULL << (i & 63));
            if (w) {
                uint64_t j = (i & ~63ULL) + (uint64_t)__builtin_ctzll(w);
                return (u128)(2 * j + 1);
            }
            i = (i | 63) + 1;
        }
        c = (u128)SIEVE_MAX + 1; /* SIEVE_MAX is even; first odd above it */
    }
    while (!is_prime(c)) c += 2;
    return c;
}

/* ------------------------- subset-sum oracle ---------------------------- */

/* Same divisor set and same yes/no answer as the Python divisors_upto +
 * delta_expressible (divisors of n = prod fac[0..depth) that are <= delta,
 * then subset-sum). Three exact shortcuts on top of the naive bitset:
 *  1. if the kept divisors sum to < delta, delta is unreachable (early 0);
 *  2. contiguous-prefix phase: with divisors processed ascending, while
 *     d <= r+1 every sum in [0, r+d] stays reachable — if r reaches delta,
 *     early 1 without touching the bitset; when a d breaks the chain the
 *     gap at r+1 is permanent (all remaining divisors exceed it), so the
 *     reachable set of the processed divisors is exactly [0, r] and the
 *     bitset is seeded with that;
 *  3. the bitset is capped at delta+1 bits and OR passes stop at the
 *     high-water mark of possibly-nonzero words (bits above can never
 *     influence bit delta — shifts only move bits upward), and bit delta
 *     is checked after every divisor for early 1.
 * All are exact, so the oracle's answers are identical to Python's.
 * Requires 0 < delta < DELTA_MAX. */
static int cmp_u64(const void *A, const void *B) {
    uint64_t a = *(const uint64_t *)A, b = *(const uint64_t *)B;
    return a < b ? -1 : a > b;
}

static int delta_expressible(int depth, u128 delta) {
    uint64_t lim = (uint64_t)delta;
    size_t nds = 1;
    u128 dsum = 1; /* sum of divisors kept, clamped at delta */
    ds[0] = 1;
    for (int i = 0; i < depth; i++) {
        u128 p = fac[i].p, pp = 1;
        size_t next = 0;
        for (int e = 0; e < fac[i].a; e++) {
            pp *= p;
            for (size_t j = 0; j < nds; j++) { /* snapshot of ds, as Python */
                u128 v = (u128)ds[j] * pp;
                if (v <= delta) {
                    if (next == ext_cap) {
                        ext_cap *= 2;
                        ext = realloc(ext, ext_cap * sizeof *ext);
                        if (!ext) { fprintf(stderr, "oom\n"); exit(1); }
                    }
                    ext[next++] = (uint64_t)v;
                    dsum += v;
                    if (dsum > delta) dsum = delta;
                }
            }
        }
        if (nds + next > ds_cap) {
            while (nds + next > ds_cap) ds_cap *= 2;
            ds = realloc(ds, ds_cap * sizeof *ds);
            if (!ds) { fprintf(stderr, "oom\n"); exit(1); }
        }
        memcpy(ds + nds, ext, next * sizeof *ext);
        nds += next;
    }
    if (dsum < delta) return 0; /* total of kept divisors < delta: unreachable */

    qsort(ds, nds, sizeof *ds, cmp_u64);

    /* contiguous-prefix phase (shortcut 2) */
    uint64_t r = 0;
    size_t i = 0;
    while (i < nds && ds[i] <= r + 1) {
        r += ds[i];
        if (r >= lim) return 1;
        i++;
    }
    if (i == nds) return 0; /* reachable set is [0, r] with r < lim */

    /* bitset phase, seeded with [0, r] */
    size_t words = (size_t)(lim / 64 + 1); /* dsum >= delta, so lim is the tight cap */
    size_t fw = (size_t)(r >> 6);
    memset(bits, 0, words * sizeof *bits);
    if (fw) memset(bits, 0xFF, fw * sizeof *bits);
    bits[fw] = (r & 63) == 63 ? ~0ULL : ((1ULL << ((r & 63) + 1)) - 1);
    size_t hw = fw;
    for (; i < nds; i++) {
        uint64_t v = ds[i];
        size_t w = (size_t)(v >> 6);
        unsigned sh = (unsigned)(v & 63);
        size_t top = hw + w + 1;
        if (top > words - 1) top = words - 1;
        if (sh == 0) {
            for (size_t k = top + 1; k-- > w; ) bits[k] |= bits[k - w];
        } else {
            for (size_t k = top + 1; k-- > 0; ) {
                uint64_t x = 0;
                if (k >= w) x = bits[k - w] << sh;
                if (k > w)  x |= bits[k - w - 1] >> (64 - sh);
                bits[k] |= x;
            }
        }
        hw = top;
        if ((bits[lim >> 6] >> (lim & 63)) & 1) return 1;
    }
    return (int)((bits[lim >> 6] >> (lim & 63)) & 1);
}

/* ------------------------------- DFS ------------------------------------ */

/* k_max: max number of additional prime factors (>= p_start) fitting under
 * N_CAP — exact port (m*p <= N_CAP evaluated divisionally). */
static int k_max(u128 n, u128 p) {
    int k = 0;
    u128 m = n;
    while (m <= N_CAP / p) {
        m *= p;
        p = next_prime(p);
        k++;
    }
    return k;
}

/* min(k_max(n,p), cap) — identical pruning power for "< cap" tests, but
 * bounded at cap iterations (<= cap-1 next_prime calls). The MIN_DEPTH prune
 * only needs "can we fit (MIN_DEPTH-depth) more distinct primes", so the
 * full k_max (15-20 iterations on small n) is wasted there: a=2 of the
 * monster ran at 195k nodes/s instead of ~20M because of this. */
static int k_max_cap(u128 n, u128 p, int cap) {
    int k = 0;
    u128 m = n;
    while (k < cap && m <= N_CAP / p) {
        m *= p;
        p = next_prime(p);
        k++;
    }
    return k;
}

/* delta*p + sig >= DELTA_MAX, evaluated without forming the product. */
static int delta_overshoots(u128 delta, u128 p, u128 sig) {
    u128 T, q;
    if (sig >= DELTA_MAX) return 1; /* sum > sig >= DELTA_MAX */
    T = DELTA_MAX - sig;            /* 0 < T <= DELTA_MAX */
    q = T / p;
    return delta > q || (delta == q && T % p == 0);
}

static void dfs(u128 p_start, u128 n, u128 sig, int depth) {
    if (deadline_hit) return;
    nodes++;
    if ((nodes & 4095) == 0) { /* Python: every 1000; see header comment */
        if (now() - t0 > (double)TIME_BUDGET) { deadline_hit = 1; return; }
    }
    if (nodes % 10000000 == 0) {
        char c1[32], c2[32], nb[64];
        u64_commas(c1, nodes);
        u64_commas(c2, tested);
        u128_str(nb, n);
        printf("progress: nodes=%s tested=%s found=%zu n=%s elapsed=%.0fs\n",
               c1, c2, nfound, nb, now() - t0);
        fflush(stdout);
    }

    if (MIN_DEPTH > 0 && depth < MIN_DEPTH) {
        /* prune: no descendant can reach MIN_DEPTH distinct prime factors
         * (k_max_cap bounds how many more distinct primes fit within N_CAP,
         * capped at the needed count — exact same decision as full k_max) */
        int need = (int)(MIN_DEPTH - depth);
        if (k_max_cap(n, p_start, need) < need) return;
    }

    int abundant = 0, km = 0;
    u128 delta = 0;
    if (sig > 2 * n) {
        delta = sig - 2 * n;
        if (delta >= DELTA_MAX) return;
        if (depth >= MIN_DEPTH) { /* below MIN_DEPTH not weird-eligible (Liddy–Riedl) */
            tested++;
            if (!delta_expressible(depth, delta)) {
            char nb[64], db[64];
            if (nfound == found_cap) {
                found_cap = found_cap ? found_cap * 2 : 1024;
                found = realloc(found, found_cap * sizeof *found);
                if (!found) { fprintf(stderr, "oom\n"); exit(1); }
            }
            found[nfound].n = n;
            found[nfound].delta = delta;
            found[nfound].depth = depth;
            memcpy(found[nfound].f, fac, (size_t)depth * sizeof *fac);
            nfound++;
            u128_str(nb, n);
            u128_str(db, delta);
            printf("*** WEIRD n=%s delta=%s fac=", nb, db);
            fprint_fac(stdout, fac, depth);
            putchar('\n');
            fflush(stdout);
            }
        }
        abundant = 1;
        /* extension by prime p (a=1) gives delta' = delta*p + sig; increasing
         * in p, so the p-loop below breaks as soon as this exceeds DELTA_MAX */
    } else {
        km = k_max(n, p_start);
        if (km == 0) return;
    }

    double abund = ratio(sig, n);
    u128 p = p_start;
    while (n <= N_CAP / p) { /* Python: n * p <= N_CAP */
        u128 np = next_prime(p); /* dfs arg and loop increment, as Python */
        if (abundant) {
            if (delta_overshoots(delta, p, sig)) break;
            fac[depth].p = p;
            fac[depth].a = 1;
            dfs(np, n * p, sig * (p + 1), depth + 1);
        } else {
            /* can choosing p (any exponent) still reach abundancy 2? Each
             * further prime-power factor q^b contributes multiplier
             * sigma(q^b)/q^b < q/(q-1) <= p/(p-1); at most km+1 factors fit. */
            if (abund * pow((double)p / (double)(p - 1), (double)(km + 1)) <= 2.0)
                break;
            u128 ppow = 1, sumpow = 1; /* sumpow = 1 + p + ... + p^a = sigma(p^a) */
            int a = 0;
            while (ppow <= N_CAP / n / p) { /* exact: n*(ppow*p) <= N_CAP */
                ppow *= p;                  /* ppow = p^a <= N_CAP/n */
                sumpow += ppow;
                a++;
                u128 nn = n * ppow;         /* <= N_CAP */
                u128 ss = sig * sumpow;     /* = sigma(nn), exactly as Python */
                fac[depth].p = p;
                fac[depth].a = a;
                dfs(np, nn, ss, depth + 1);
                if (deadline_hit) return;
            }
        }
        if (deadline_hit) return;
        p = np;
    }
}

/* ------------------------------- main ------------------------------------ */

/* int(float(env)) semantics (Python); `dflt` used when the var is unset. */
static u128 parse_env_u128(const char *name, u128 dflt) {
    const char *s = getenv(name);
    if (!s) return dflt;
    double d = strtod(s, NULL);
    if (!(d >= 0.0)) {
        fprintf(stderr, "%s: cannot parse '%s'\n", name, s);
        exit(1);
    }
    if (d >= 3.0e38) {
        fprintf(stderr, "%s: value %s exceeds u128 working range\n", name, s);
        exit(1);
    }
    return (u128)d; /* truncation toward zero, like Python int() */
}

static int cmp_found(const void *A, const void *B) {
    const found_t *a = A, *b = B;
    return a->n < b->n ? -1 : a->n > b->n;
}

int main(void) {
    N_CAP = parse_env_u128("N_CAP", (u128)1000000000000000000ULL * 1000000ULL);
    DELTA_MAX = parse_env_u128("DELTA_MAX", 10000000);
    ALLOW_EVEN = getenv("ALLOW_EVEN") && strcmp(getenv("ALLOW_EVEN"), "1") == 0;
    TIME_BUDGET = getenv("TIME_BUDGET") ? atol(getenv("TIME_BUDGET")) : 600;
    MIN_DEPTH = getenv("MIN_DEPTH") ? atol(getenv("MIN_DEPTH")) : 0;

    if (N_CAP < 1 || N_CAP > N_CAP_CLAMP) {
        fprintf(stderr, "N_CAP out of supported range (1..1e36)\n");
        return 1;
    }
    if (DELTA_MAX < 2 || DELTA_MAX > DELTA_MAX_CLAMP) {
        fprintf(stderr, "DELTA_MAX out of supported range (2..2^40)\n");
        return 1;
    }

    ds_cap = ext_cap = 4096;
    ds = malloc(ds_cap * sizeof *ds);
    ext = malloc(ext_cap * sizeof *ext);
    bits = malloc(((size_t)(DELTA_MAX / 64) + 2) * sizeof *bits);
    if (!ds || !ext || !bits) { fprintf(stderr, "oom\n"); return 1; }

    sieve_init();

    printf("search v2: odd=%s, N_CAP=%.2e, DELTA_MAX=%.1e, MIN_DEPTH=%ld\n",
           ALLOW_EVEN ? "False" : "True", (double)N_CAP, (double)DELTA_MAX, MIN_DEPTH);
    fflush(stdout);

    /* SPF shard: when SPF=p (prime) is set, cover exactly the factorizations
     * whose smallest prime factor equals p (disjoint union over p = full
     * search). Root factor p^a forced for a=1,2,... within N_CAP. */
    u128 SPF = parse_env_u128("SPF", 0);
    u128 P2 = parse_env_u128("P2", 0);
    u128 P3 = parse_env_u128("P3", 0);
    u128 EXPA = parse_env_u128("EXPA", 0); /* >0: fix exponent of SPF to EXPA
        (disjoint partition over a=1..amax; trivially complete union) */
    u128 EXPB = parse_env_u128("EXPB", 0); /* >0: fix exponent of P2 to EXPB
        (same partition argument, one level down) */

    t0 = now();
    if (SPF >= 2) {
        if (next_prime(SPF - 1) != SPF) {
            fprintf(stderr, "SPF=%.0f is not prime\n", (double)SPF);
            return 1;
        }
        printf("SPF shard: smallest prime factor = %.0f\n", (double)SPF);
        if (P2 >= 2) {
            /* P2 sub-shard: within the SPF shard, force the second prime to
             * be exactly P2 (all exponents of SPF and of P2 enumerated).
             * Disjoint union over viable P2 = full SPF shard (no candidate
             * lost: skipped (a,P2) pairs are exactly those whose subtree
             * provably cannot reach abundancy 2 — same viability formula as
             * dfs()'s deficient branch, with km recomputed at P2). */
            if (P2 <= SPF || next_prime(P2 - 1) != P2) {
                fprintf(stderr, "P2=%.0f must be prime > SPF\n", (double)P2);
                return 1;
            }
            printf("P2 sub-shard: second prime factor = %.0f\n", (double)P2);
            if (P3 >= 2) {
                /* P3 sub-sub-shard: within the P2 sub-shard, force the third
                 * prime to be exactly P3. Same completeness argument, one
                 * level deeper: skipped (a,b,P3) subtrees provably contain no
                 * abundant node (viability formula, km recomputed at P3). */
                if (P3 <= P2 || next_prime(P3 - 1) != P3) {
                    fprintf(stderr, "P3=%.0f must be prime > P2\n", (double)P3);
                    return 1;
                }
                printf("P3 sub-sub-shard: third prime factor = %.0f\n", (double)P3);
            }
        }
        fflush(stdout);
        u128 nn = 1, sumpow = 1;
        int a = 0;
        while (nn <= N_CAP / SPF) {
            nn *= SPF;
            sumpow += nn;
            a++;
            if (EXPA >= 1 && (u128)a != EXPA) continue;
            fac[0].p = SPF;
            fac[0].a = a;
            if (P2 >= 2) {
                double abund = ratio(sumpow, nn);
                int km = k_max(nn, P2);
                if (km == 0) continue;
                if (abund * pow((double)P2 / (double)(P2 - 1), (double)(km + 1)) <= 2.0)
                    continue;
                u128 ppow = 1, sump = 1; /* sump = sigma(P2^b) */
                int b = 0;
                while (ppow <= N_CAP / nn / P2) {
                    ppow *= P2;
                    sump += ppow;
                    b++;
                    if (EXPB >= 1 && (u128)b != EXPB) continue;
                    fac[1].p = P2;
                    fac[1].a = b;
                    if (P3 >= 2) {
                        u128 n2 = nn * ppow, s2 = sumpow * sump;
                        double abund2 = ratio(s2, n2);
                        int km2 = k_max(n2, P3);
                        if (km2 == 0) continue;
                        if (abund2 * pow((double)P3 / (double)(P3 - 1), (double)(km2 + 1)) <= 2.0)
                            continue;
                        u128 ppp = 1, sp3 = 1; /* sp3 = sigma(P3^c) */
                        int c = 0;
                        while (ppp <= N_CAP / n2 / P3) {
                            ppp *= P3;
                            sp3 += ppp;
                            c++;
                            fac[2].p = P3;
                            fac[2].a = c;
                            dfs(next_prime(P3), n2 * ppp, s2 * sp3, 3);
                            if (deadline_hit) break;
                        }
                    } else {
                        dfs(next_prime(P2), nn * ppow, sumpow * sump, 2);
                    }
                    if (deadline_hit) break;
                }
            } else {
                dfs(next_prime(SPF), nn, sumpow, 1);
            }
            if (deadline_hit) break;
        }
    } else {
        dfs(ALLOW_EVEN ? 2 : 3, 1, 1, 0);
    }

    {
        char c1[32], c2[32];
        u64_commas(c1, nodes);
        u64_commas(c2, tested);
        printf("\ndone in %.1fs | nodes=%s | tested=%s | weird=%zu\n",
               now() - t0, c1, c2, nfound);
    }
    qsort(found, nfound, sizeof *found, cmp_found);
    for (size_t i = 0; i < nfound; i++) {
        char nb[64], db[64];
        u128_str(nb, found[i].n);
        u128_str(db, found[i].delta);
        printf("  n=%s delta=%s fac=", nb, db);
        fprint_fac(stdout, found[i].f, found[i].depth);
        putchar('\n');
    }
    fflush(stdout);
    return 0;
}
