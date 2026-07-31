/* Erdős #287 — meet-in-the-middle counterexample hunt, C port of mitm_287.py.
 *
 * Reproduces the Python engine's mathematics exactly:
 *  - same 3-prime residue hash (P1=2^61-1, P2=2^31-1, P3=999999937),
 *    inverses n^(p-2) mod p, residues accumulated mod p per term;
 *  - same float pruning: IEEE doubles, same operation order as the Python
 *    (max_rem precomputed with CPython's Neumaier-compensated sum()
 *     semantics, bit-identical to Python's max_rem; EPS=1e-9);
 *  - same split j=k//2, same lo/hi bounds, same window (min_s2,max_s2),
 *    same boundary-gap join 1 <= tup2[0] - last_fj <= GAP.
 *
 * Deliberate differences (all in the SAFE direction):
 *  - the hash table keys a 64-bit digest of the residue triple, so the join
 *    is a SUPERSET of Python's exact-triple join: digest collisions can only
 *    ADD spurious candidates (rejected by verify_hits.py), never remove a
 *    true match (a missed hit would be a missed counterexample — unsafe);
 *  - hit candidates (full k-tuples) are dumped to hits_287_k{K}_gap{GAP}.txt
 *    and verified externally by verify_hits.py (same Fraction check as
 *    mitm_287.py); the engine itself does no exact arithmetic;
 *  - always exhaustive (verification is external, so early-exit is moot).
 *
 * Memory: 16 bytes/entry (u64 digest + u64 packed tuple: first term in bits
 * [6:0], then GAP_BITS per step), open addressing with linear probing,
 * power-of-2 slots at <=2/3 load plus a 1-bit occupancy map (no sentinel
 * value can alias a real entry). Two counting/insertion passes over the
 * first half; the second half is streamed with no storage.
 *
 * Build:  clang -O3 -o mitm_287 mitm_287.c -lm
 * Run:    GAP=2 ./mitm_287 [k_lo [k_hi]]     (defaults: 22 40, like Python)
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <limits.h>
#include <math.h>
#include <time.h>

#define P1 (((uint64_t)1 << 61) - 1)
#define P2 (((uint64_t)1 << 31) - 1)
#define P3 (999999937ULL)

#define EPS 1e-9
#define MAXN 4096   /* max term value (terms stay < ~1100 for k<=80, GAP<=8) */
#define MAXK 80     /* max k */

static int K, GAP, J, N_SECOND, GAP_BITS;
static int m1_lo, m1_hi, min_last, max_last;
static double min_s1, max_s1, min_s2, max_s2;

static uint64_t inv1[MAXN], inv2[MAXN], inv3[MAXN];
/* max_rem(l, r) = sum_{i=1..r} 1.0/(l+i) with CPython sum()'s Neumaier
 * compensation (see precompute) */
static double mr[MAXN][MAXK + 1];

static uint64_t first_count, second_count, cand_count;

typedef struct { uint64_t key, packed; } Slot;   /* 16 bytes */
static Slot *slots;
static uint64_t *occmap;    /* occupancy bitmap, 1 bit per slot */
static uint64_t mask;       /* nslots - 1 */
static FILE *hitsf;

static double now(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

static inline uint64_t mulmod(uint64_t a, uint64_t b, uint64_t m) {
    return (uint64_t)(((__uint128_t)a * b) % m);
}

static uint64_t powmod(uint64_t b, uint64_t e, uint64_t m) {
    uint64_t r = 1;
    while (e) {
        if (e & 1) r = mulmod(r, b, m);
        b = mulmod(b, b, m);
        e >>= 1;
    }
    return r;
}

/* Deterministic 64-bit digest of the residue triple. Same triple -> same
 * digest, so a true match is never missed; distinct triples may collide
 * (prob ~2^-64), which only yields a spurious, verifier-rejected candidate. */
static inline uint64_t mix64(uint64_t a, uint64_t b, uint64_t c) {
    uint64_t h = a + 0x9E3779B97F4A7C15ULL;
    h = (h ^ (h >> 30)) * 0xBF58476D1CE4E5B9ULL;
    h = (h ^ b) * 0xBF58476D1CE4E5B9ULL;
    h = (h ^ (h >> 27)) * 0x94D049BB133111EBULL;
    h = (h ^ c) * 0x94D049BB133111EBULL;
    h = h ^ (h >> 31);
    return h;
}

static void precompute(void) {
    for (int n = 1; n < MAXN; n++) {
        inv1[n] = powmod((uint64_t)n, P1 - 2, P1);
        inv2[n] = powmod((uint64_t)n, P2 - 2, P2);
        inv3[n] = powmod((uint64_t)n, P3 - 2, P3);
        if (mulmod((uint64_t)n, inv1[n], P1) != 1 ||
            mulmod((uint64_t)n, inv2[n], P2) != 1 ||
            mulmod((uint64_t)n, inv3[n], P3) != 1) {
            fprintf(stderr, "FATAL: inverse self-test failed at n=%d\n", n);
            exit(1);
        }
    }
    /* mr[l][r] = max_rem(l, r) = sum(1.0/(l+i) for i in 1..r). CPython's
     * builtin sum() on floats uses Neumaier compensated summation (since
     * 3.12, bltinmodule.c); replicate it bit-exactly. The (res, comp) state
     * after i=1..r is the same whether carried incrementally across r or
     * rebuilt fresh per r (identical operation sequence), so one pass fills
     * the whole row. Verified bit-identical to Python's max_rem via hex
     * float comparison. */
    for (int l = 0; l < MAXN; l++) {
        mr[l][0] = 0.0;
        double res = 0.0, comp = 0.0;
        for (int r = 1; r <= MAXK; r++) {
            double x = 1.0 / (l + r);
            double t = res + x;
            if (fabs(res) > fabs(x)) comp += (res - t) + x;
            else                     comp += (x - t) + res;
            res = t;
            mr[l][r] = res + comp;
        }
    }
}

static inline int occupied(uint64_t i) {
    return (int)((occmap[i >> 6] >> (i & 63)) & 1ULL);
}

static void insert(uint64_t key, uint64_t packed) {
    uint64_t i = key & mask;
    while (occupied(i)) i = (i + 1) & mask;
    occmap[i >> 6] |= 1ULL << (i & 63);
    slots[i].key = key;
    slots[i].packed = packed;
}

/* packed first-half tuple: bits [6:0] = first term; then GAP_BITS per step
 * holding (gap - 1) */
static int decode_last(uint64_t packed) {
    uint64_t gmask = (1ULL << GAP_BITS) - 1;
    int v = (int)(packed & 0x7F);
    for (int i = 0; i < J - 1; i++)
        v += 1 + (int)((packed >> (7 + GAP_BITS * i)) & gmask);
    return v;
}

static void dump_candidate(uint64_t packed, const int *tup2) {
    uint64_t gmask = (1ULL << GAP_BITS) - 1;
    int v = (int)(packed & 0x7F);
    fprintf(hitsf, "%d", v);
    for (int i = 0; i < J - 1; i++) {
        v += 1 + (int)((packed >> (7 + GAP_BITS * i)) & gmask);
        fprintf(hitsf, " %d", v);
    }
    for (int i = 0; i < N_SECOND; i++)
        fprintf(hitsf, " %d", tup2[i]);
    fputc('\n', hitsf);
    cand_count++;
}

static void probe(uint64_t key, const int *tup2) {
    uint64_t i = key & mask;
    while (occupied(i)) {
        if (slots[i].key == key) {
            int d = tup2[0] - decode_last(slots[i].packed);
            if (1 <= d && d <= GAP)
                dump_candidate(slots[i].packed, tup2);
        }
        i = (i + 1) & mask;
    }
}

/* First half: j terms. Mirrors mitm_287.py rec1 exactly. do_insert=0: count
 * leaves + gather window stats; do_insert=1: insert into the hash table. */
static void rec1(int pos, int last, double s,
                 uint64_t r1, uint64_t r2, uint64_t r3, uint64_t packed,
                 int do_insert) {
    int rem = J - pos - 1;
    int lo = (pos == 0) ? 2 : last + 1;
    int hi = (pos == 0) ? (K - 1) : last + GAP;
    for (int nxt = lo; nxt <= hi; nxt++) {
        double ns = s + 1.0 / nxt;
        if (ns >= 1.0) continue;
        if (ns + mr[nxt][rem] + mr[nxt + rem][N_SECOND] < 1.0 - EPS) continue;
        uint64_t nr1 = r1 + inv1[nxt]; if (nr1 >= P1) nr1 -= P1;
        uint64_t nr2 = r2 + inv2[nxt]; if (nr2 >= P2) nr2 -= P2;
        uint64_t nr3 = r3 + inv3[nxt]; if (nr3 >= P3) nr3 -= P3;
        uint64_t np = (pos == 0)
            ? (uint64_t)nxt
            : packed | ((uint64_t)(nxt - last - 1) << (7 + GAP_BITS * (pos - 1)));
        if (rem == 0) {
            first_count++;
            if (do_insert) {
                insert(mix64(nr1, nr2, nr3), np);
            } else {
                if (ns < min_s1) min_s1 = ns;
                if (ns > max_s1) max_s1 = ns;
                if (nxt < min_last) min_last = nxt;
                if (nxt > max_last) max_last = nxt;
            }
        } else {
            rec1(pos + 1, nxt, ns, nr1, nr2, nr3, np, do_insert);
        }
    }
}

/* Second half: k-j terms. Mirrors mitm_287.py rec2 exactly, except the exact
 * Fraction check is deferred to verify_hits.py (candidates are dumped). */
static void rec2(int pos, int last, double s,
                 uint64_t r1, uint64_t r2, uint64_t r3, int *tup) {
    int rem = N_SECOND - pos - 1;
    int lo = (pos == 0) ? m1_lo : last + 1;
    int hi = (pos == 0) ? m1_hi : last + GAP;
    for (int nxt = lo; nxt <= hi; nxt++) {
        double ns = s + 1.0 / nxt;
        if (ns >= max_s2 + EPS) continue;
        if (ns + mr[nxt][rem] < min_s2 - EPS) continue;
        uint64_t nr1 = r1 + inv1[nxt]; if (nr1 >= P1) nr1 -= P1;
        uint64_t nr2 = r2 + inv2[nxt]; if (nr2 >= P2) nr2 -= P2;
        uint64_t nr3 = r3 + inv3[nxt]; if (nr3 >= P3) nr3 -= P3;
        tup[pos] = nxt;
        if (rem == 0) {
            second_count++;
            /* tgt = (1 - nr) mod p */
            uint64_t t1 = P1 + 1 - nr1; if (t1 >= P1) t1 -= P1;
            uint64_t t2 = P2 + 1 - nr2; if (t2 >= P2) t2 -= P2;
            uint64_t t3 = P3 + 1 - nr3; if (t3 >= P3) t3 -= P3;
            probe(mix64(t1, t2, t3), tup);
        } else {
            rec2(pos + 1, nxt, ns, nr1, nr2, nr3, tup);
        }
    }
}

int main(int argc, char **argv) {
    int k_lo = 22, k_hi = 40;
    if (argc > 1) k_lo = atoi(argv[1]);
    if (argc > 2) k_hi = atoi(argv[2]);
    const char *g = getenv("GAP");
    GAP = g ? atoi(g) : 2;
    if (k_lo < 2 || k_hi < k_lo || k_hi > MAXK || GAP < 1 || GAP > 8) {
        fprintf(stderr,
                "usage: GAP=2 ./mitm_287 [k_lo [k_hi]]  (2<=k_lo<=k_hi<=%d, 1<=GAP<=8)\n",
                MAXK);
        return 2;
    }
    GAP_BITS = (GAP <= 2) ? 1 : (GAP <= 4 ? 2 : 3);
    precompute();

    int tup[MAXK];
    for (K = k_lo; K <= k_hi; K++) {
        J = K / 2;
        N_SECOND = K - J;
        double t0 = now();
        char path[256];
        snprintf(path, sizeof path, "hits_287_k%d_gap%d.txt", K, GAP);
        hitsf = fopen(path, "w");
        if (!hitsf) { fprintf(stderr, "cannot open %s\n", path); return 1; }
        first_count = 0; second_count = 0; cand_count = 0;

        if (J < 1 || N_SECOND < 1 || 7 + GAP_BITS * (J - 1) > 64) {
            printf("k=%d: none (halves=0+0, cand=0, %.1fs)\n", K, now() - t0);
            fflush(stdout);
            fclose(hitsf);
            continue;
        }

        /* pass 1: count first-half leaves + window stats */
        min_s1 = 2.0; max_s1 = -1.0; min_last = INT_MAX; max_last = 0;
        rec1(0, 0, 0.0, 0, 0, 0, 0, 0);
        uint64_t n = first_count;
        if (n == 0) {
            printf("k=%d: none (halves=0+0, cand=0, %.1fs)\n", K, now() - t0);
            fflush(stdout);
            fclose(hitsf);
            continue;
        }

        uint64_t nslots = 1ULL << 16;
        while (nslots < n + (n >> 1)) nslots <<= 1;   /* load <= 2/3 */
        mask = nslots - 1;
        slots = malloc((size_t)nslots * sizeof(Slot));
        occmap = calloc((size_t)(nslots >> 6) + 1, sizeof(uint64_t));
        if (!slots || !occmap) {
            fprintf(stderr, "FATAL: table alloc failed (%llu slots)\n",
                    (unsigned long long)nslots);
            return 1;
        }
        fprintf(stderr, "k=%d: first_half=%llu, table %llu slots (%.1f MB)\n",
                K, (unsigned long long)n, (unsigned long long)nslots,
                (double)(nslots * sizeof(Slot)) / 1048576.0);

        /* pass 2: insert (enumeration is deterministic; count must match) */
        first_count = 0;
        rec1(0, 0, 0.0, 0, 0, 0, 0, 1);
        if (first_count != n) {
            fprintf(stderr, "FATAL: nondeterministic first-half count\n");
            return 1;
        }

        /* join window from first-half sums (mirrors mitm_287.py) */
        min_s2 = 1.0 - max_s1;
        max_s2 = 1.0 - min_s1;
        m1_lo = min_last + 1; if (m1_lo < 3) m1_lo = 3;
        m1_hi = max_last + GAP;

        rec2(0, 0, 0.0, 0, 0, 0, tup);

        free(slots); free(occmap);
        slots = NULL; occmap = NULL;
        fclose(hitsf);

        if (cand_count)
            printf("k=%d: %llu candidates dumped -> %s (halves=%llu+%llu, %.1fs)\n",
                   K, (unsigned long long)cand_count, path,
                   (unsigned long long)n, (unsigned long long)second_count,
                   now() - t0);
        else
            printf("k=%d: none (halves=%llu+%llu, cand=0, %.1fs)\n",
                   K, (unsigned long long)n, (unsigned long long)second_count,
                   now() - t0);
        fflush(stdout);
    }
    printf("done: k=%d..%d complete (verify hits files with verify_hits.py)\n",
           k_lo, k_hi);
    return 0;
}
