/*
 * grimm.c — verification engine for Grimm's conjecture (Erdős #375).
 *
 * Statement: for every block of consecutive composite integers n+1..n+k
 * there exist DISTINCT primes p_1..p_k with p_i | n+i. One failing block
 * is a counterexample (none is expected; Laishram–Shorey, IJNT 2006,
 * verified all blocks with n <= 19,236,701,629).
 *
 * Reduction (standard; cross-validated against a full-matching sympy
 * oracle in grimm_reference.py, gate b): in a block of length k, any
 * prime q > k divides AT MOST ONE member (two members differ by <= k-1
 * < q). So a member with a prime factor > k can always take that factor,
 * and the block is OK iff its k-smooth members (ALL prime factors <= k)
 * admit a matching into the primes <= k. We test that with exact
 * Hopcroft–Karp. Testing maximal blocks (prime gaps) suffices: any block
 * of composites sits inside a maximal run and inherits its assignment by
 * restriction; conversely a failing sub-block would make its maximal run
 * fail too. So maximal-run OK/FAIL is exactly the conjecture.
 *
 * Method: segmented odd-only sieve of Eratosthenes over [2, N_MAX];
 * consecutive primes delimit maximal composite runs; per block, factor
 * members by primes <= k only, collect smooth ones, run Hopcroft–Karp on
 * (smooth members) x (primes <= k). A matching failure prints a loud
 * CANDIDATE COUNTEREXAMPLE line and the engine keeps going.
 *
 * uint64 throughout; intended range n <= 1e13 (< 2^63).
 *
 * Build:   clang -O3 -o grimm grimm.c -lm
 *
 * Env (parsed with strtod + truncation, like search_odd_weird.c):
 *   N_MAX        upper bound (default 1e10)
 *   N_START      resume offset (default 2). State = N_START only: blocks
 *                are independent, and the boundary block straddling
 *                N_START is re-verified in FULL (the engine walks back to
 *                the largest prime <= N_START), so shards stitch without
 *                gaps or double-counted claims.
 *   SEG          segment size in integers (default 1e7; forced even)
 *   PROGRESS     progress line every PROGRESS integers (default 1e8)
 *   DUMP_BLOCKS  =1 prints one "block:" line per block (used by gate b)
 *
 * Output (stdout, always flushed): config, record-gap, block (opt),
 * CANDIDATE COUNTEREXAMPLE, progress, done.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>
#include <math.h>
#include <time.h>

/* KCAP: max supported block length. The largest prime gap ever found
 * below 2^63 is 1550, so k <= 1549; 65536 gives >40x headroom. */
#define KCAP  65536
/* SLOTS: max distinct prime factors of any uint64 (primorial 53# > 2^63,
 * so omega(m) <= 15 for m < 2^63); 20 gives headroom. */
#define SLOTS 20

/* ------------------------------ config ---------------------------------- */

static uint64_t N_MAX    = 10000000000ULL; /* 1e10 */
static uint64_t N_START  = 2;
static uint64_t SEG      = 10000000;       /* 1e7 */
static uint64_t PROGRESS = 100000000;      /* 1e8 */
static int      DUMP_BLOCKS = 0;

static uint64_t env_u64(const char *name, uint64_t dflt) {
    const char *s = getenv(name);
    return s ? (uint64_t)strtod(s, NULL) : dflt;
}

static double now_s(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + 1e-9 * (double)ts.tv_nsec;
}

/* --------------------------- base primes -------------------------------- */

static uint32_t *primes = NULL;   /* all primes up to base limit */
static int       nprimes = 0;
static int       pi_of_k[KCAP + 1]; /* pi_of_k[k] = # primes <= k */

static uint64_t isqrt_u64(uint64_t x) {
    uint64_t r = (uint64_t)sqrt((double)x);
    while ((r + 1) * (r + 1) <= x) r++;
    while (r * r > x) r--;
    return r;
}

static void build_base_primes(uint64_t lim) {
    uint8_t *comp = calloc(lim + 1, 1);
    for (uint64_t p = 2; p * p <= lim; p++)
        if (!comp[p])
            for (uint64_t j = p * p; j <= lim; j += p) comp[j] = 1;
    for (uint64_t p = 2; p <= lim; p++) if (!comp[p]) nprimes++;
    primes = malloc((size_t)nprimes * sizeof(uint32_t));
    int w = 0;
    for (uint64_t p = 2; p <= lim; p++) if (!comp[p]) primes[w++] = (uint32_t)p;
    free(comp);
    /* pi_of_k table */
    int pi = 0;
    for (int k = 0; k <= KCAP; k++) {
        while (pi < nprimes && (uint64_t)primes[pi] <= (uint64_t)k) pi++;
        pi_of_k[k] = pi;
    }
}

/* index of prime q within primes[0..np); q must be present */
static int prime_index(uint64_t q, int np) {
    int lo = 0, hi = np - 1;
    while (lo <= hi) {
        int mid = (lo + hi) >> 1;
        if (primes[mid] == q) return mid;
        if (primes[mid] < q) lo = mid + 1; else hi = mid - 1;
    }
    fprintf(stderr, "FATAL: prime_index(%" PRIu64 ") not found\n", q);
    exit(2);
}

/* ------------------------- segmented sieve ------------------------------ */

/* mark odd composites in [wlo, hi]; wlo odd >= 3; mark[(v-wlo)/2] = 1 */
static void mark_segment(uint64_t wlo, uint64_t hi, uint8_t *mark) {
    uint64_t size = (hi - wlo) / 2 + 1;
    memset(mark, 0, size);
    for (int i = 1; i < nprimes; i++) { /* skip p=2: evens not represented */
        uint64_t p = primes[i];
        if (p * p > hi) break;
        uint64_t start = p * p;
        if (start < wlo) {
            start = (wlo / p) * p;
            if (start < wlo) start += p;
        }
        if ((start & 1) == 0) start += p; /* want odd multiples of odd p */
        for (uint64_t j = start; j <= hi; j += 2 * p) mark[(j - wlo) >> 1] = 1;
    }
}

/* largest prime <= n (n >= 2), via a window sieve below n */
static uint64_t prev_prime_le(uint64_t n) {
    uint64_t W = 1u << 16; /* >> max gap 1550 ever seen in uint64 */
    uint8_t *wmark = NULL;
    uint64_t wcap = 0, best;
    for (;;) {
        uint64_t lo = (n > W) ? n - W + 1 : 2;
        uint64_t wlo = lo < 3 ? 3 : lo;
        if ((wlo & 1) == 0) wlo++;
        uint64_t size = (wlo > n) ? 0 : (n - wlo) / 2 + 1;
        if (size > wcap) { free(wmark); wcap = size; wmark = malloc(wcap); }
        best = 0;
        if (size) {
            mark_segment(wlo, n, wmark);
            for (uint64_t i = size; i-- > 0; )
                if (!wmark[i]) { best = wlo + 2 * i; break; }
        }
        if (!best && lo <= 2 && n >= 2) best = 2;
        if (best) { free(wmark); return best; }
        W *= 2; /* no prime in window: grow (not expected in practice) */
    }
}

/* ------------------------- per-block state ------------------------------ */

static uint64_t  sm_m[KCAP];          /* smooth member values */
static uint32_t  sm_fac[KCAP * SLOTS];/* their prime indices (<= k) */
static int       sm_cnt[KCAP];
static int       matchL[KCAP], matchR[KCAP], dist_[KCAP], queue_[KCAP];

static int hk_bfs(int s) {
    int qh = 0, qt = 0, found = 0;
    for (int u = 0; u < s; u++) {
        if (matchL[u] < 0) { dist_[u] = 0; queue_[qt++] = u; }
        else dist_[u] = -1;
    }
    while (qh < qt) {
        int u = queue_[qh++];
        for (int t = 0; t < sm_cnt[u]; t++) {
            int v = (int)sm_fac[(size_t)u * SLOTS + t];
            int u2 = matchR[v];
            if (u2 < 0) found = 1;
            else if (dist_[u2] < 0) { dist_[u2] = dist_[u] + 1; queue_[qt++] = u2; }
        }
    }
    return found;
}

static int hk_dfs(int u) {
    for (int t = 0; t < sm_cnt[u]; t++) {
        int v = (int)sm_fac[(size_t)u * SLOTS + t];
        int u2 = matchR[v];
        if (u2 < 0 || (dist_[u2] == dist_[u] + 1 && hk_dfs(u2))) {
            matchL[u] = v; matchR[v] = u;
            return 1;
        }
    }
    dist_[u] = -1;
    return 0;
}

static int hk_run(int s, int np) {
    for (int u = 0; u < s; u++) matchL[u] = -1;
    for (int v = 0; v < np; v++) matchR[v] = -1;
    int match = 0;
    while (hk_bfs(s))
        for (int u = 0; u < s; u++)
            if (matchL[u] < 0 && hk_dfs(u)) match++;
    return match;
}

/* ------------------------------ stats ----------------------------------- */

static uint64_t nblocks = 0, total_smooth = 0, maxk = 0, maxgap = 0;
static uint64_t maxmatch = 0, nbad = 0;

/* -------------------------- block processing ---------------------------- */

static void process_block(uint64_t a, uint64_t b, uint64_t gap) {
    uint64_t k = b - a + 1;
    nblocks++;
    if (k > maxk) maxk = k;
    if (gap > maxgap) {
        maxgap = gap;
        printf("record-gap: p=%" PRIu64 " gap=%" PRIu64 "\n", a - 1, gap);
        fflush(stdout);
    }
    if (k > KCAP) {
        fprintf(stderr, "FATAL: block length %" PRIu64 " exceeds KCAP=%d\n", k, KCAP);
        exit(2);
    }
    int np = pi_of_k[k];
    int s = 0;
    for (uint64_t m = a; m <= b; m++) {
        uint64_t rem = m;
        uint32_t fac[SLOTS];
        int cnt = 0, pi = 0, smooth;
        while (pi < np) {
            uint64_t p = primes[pi];
            if (p * p > rem) break;
            if (rem % p == 0) {
                if (cnt >= SLOTS) { fprintf(stderr, "FATAL: SLOTS overflow\n"); exit(2); }
                fac[cnt++] = (uint32_t)pi;
                do { rem /= p; } while (rem % p == 0);
            }
            pi++;
        }
        if (rem == 1) smooth = 1;
        else if (pi < np) {
            /* broke on p*p > rem: rem is prime (smaller primes divided out) */
            if (rem <= k) { smooth = 1; fac[cnt++] = (uint32_t)prime_index(rem, np); }
            else smooth = 0;
        } else smooth = 0; /* all primes <= k tried, rem > 1 => factor > k */
        if (smooth) {
            sm_m[s] = m;
            sm_cnt[s] = cnt;
            memcpy(&sm_fac[(size_t)s * SLOTS], fac, (size_t)cnt * sizeof(uint32_t));
            s++;
        }
    }
    total_smooth += (uint64_t)s;
    int match = s ? hk_run(s, np) : 0;
    if ((uint64_t)match > maxmatch) maxmatch = (uint64_t)match;
    int ok = (match == s);
    if (!ok) {
        nbad++;
        printf("CANDIDATE COUNTEREXAMPLE: block %" PRIu64 "..%" PRIu64
               " k=%" PRIu64 " smooth=%d matched=%d\n", a, b, k, s, match);
        fflush(stdout);
    }
    if (DUMP_BLOCKS) {
        printf("block: a=%" PRIu64 " b=%" PRIu64 " k=%" PRIu64
               " smooth=%d match=%d ok=%d\n", a, b, k, s, match, ok);
    }
}

static uint64_t prev_prime;

static void note_prime(uint64_t p) {
    uint64_t gap = p - prev_prime;
    if (gap >= 2) process_block(prev_prime + 1, p - 1, gap);
    prev_prime = p;
}

/* ------------------------------- main ----------------------------------- */

int main(void) {
    N_MAX    = env_u64("N_MAX", N_MAX);
    N_START  = env_u64("N_START", N_START);
    SEG      = env_u64("SEG", SEG);
    PROGRESS = env_u64("PROGRESS", PROGRESS);
    DUMP_BLOCKS = getenv("DUMP_BLOCKS") && strcmp(getenv("DUMP_BLOCKS"), "1") == 0;
    if (SEG & 1) SEG++;
    if (SEG < 16) SEG = 16;
    if (PROGRESS < 1) PROGRESS = 1;
    if (N_MAX < 2) { fprintf(stderr, "FATAL: N_MAX < 2\n"); return 2; }
    if (N_START > N_MAX) { fprintf(stderr, "FATAL: N_START > N_MAX\n"); return 2; }

    double t0 = now_s();
    printf("config: N_MAX=%" PRIu64 " N_START=%" PRIu64 " SEG=%" PRIu64
           " PROGRESS=%" PRIu64 " DUMP_BLOCKS=%d\n",
           N_MAX, N_START, SEG, PROGRESS, DUMP_BLOCKS);
    fflush(stdout);

    /* base primes: must cover sqrt(N_MAX) (segment sieve) and KCAP
     * (block factoring needs all primes <= k <= KCAP) */
    uint64_t blim = isqrt_u64(N_MAX) + 2;
    if (blim < KCAP + 1) blim = KCAP + 1;
    build_base_primes(blim);

    uint64_t lo0;
    if (N_START <= 2) {
        prev_prime = 1;
        note_prime(2); /* gap 1, no block; sets prev_prime = 2 */
        lo0 = 3;
    } else {
        prev_prime = prev_prime_le(N_START);
        lo0 = N_START + 1;
        if ((lo0 & 1) == 0) lo0++;
    }

    uint8_t *seg = malloc(SEG / 2 + 1);
    uint64_t next_prog = PROGRESS;
    for (uint64_t lo = lo0; lo <= N_MAX; ) {
        uint64_t hi = lo + SEG - 1; /* N_MAX <= 1e13: no overflow */
        if (hi > N_MAX) hi = N_MAX;
        mark_segment(lo, hi, seg);
        uint64_t size = (hi - lo) / 2 + 1;
        for (uint64_t i = 0; i < size; i++)
            if (!seg[i]) note_prime(lo + 2 * i);
        if (hi >= next_prog) {
            printf("progress: n=%" PRIu64 " blocks=%" PRIu64 " smooth=%" PRIu64
                   " maxk=%" PRIu64 " elapsed=%.0fs\n",
                   hi, nblocks, total_smooth, maxk, now_s() - t0);
            fflush(stdout);
            next_prog = (hi / PROGRESS + 1) * PROGRESS;
        }
        if (hi >= N_MAX) break;
        lo += SEG;
    }

    double el = now_s() - t0;
    uint64_t span = N_MAX - (N_START < 2 ? 1 : N_START);
    printf("done: N_MAX=%" PRIu64 " N_START=%" PRIu64 " blocks=%" PRIu64
           " smooth=%" PRIu64 " maxk=%" PRIu64 " maxmatch=%" PRIu64
           " counterexamples=%" PRIu64 " elapsed=%.1fs rate=%.0f ints/s\n",
           N_MAX, N_START, nblocks, total_smooth, maxk, maxmatch, nbad,
           el, el > 0 ? (double)span / el : 0.0);
    fflush(stdout);
    return nbad ? 1 : 0;
}
