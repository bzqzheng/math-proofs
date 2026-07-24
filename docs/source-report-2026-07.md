<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# for each of the problems/conjectures, explicitly identify their solutions or counter examples or proofs

Here’s a concrete description, problem by problem, of *what* was solved and *how*—focusing on the actual constructions, proofs, or counterexamples.

***

## Erdős unit‑distance conjecture (planar point sets)

**Conjecture (informal).** For $n$ points in the Euclidean plane, let $u(n)$ be the maximum number of pairs at distance exactly 1. Erdős conjectured that $u(n)$ grows at most $n^{1+o(1)}$, i.e., only slightly faster than linear, and that rescaled square‑grid constructions are essentially optimal.[^1][^2]

**AI solution / counterexample.**
OpenAI’s internal reasoning model produced a *family of point configurations* $\{P_n\}$ with the following property:[^2][^1]

- For infinitely many $n$, the set $P_n$ of $n$ points in the plane has at least $n^{1+\delta}$ unit‑distance pairs, for some fixed $\delta>0$, thereby *violating* the conjectured upper bound $u(n) \le n^{1+o(1)}$.[^3][^1]
- A refined human analysis shows one can take $\delta = 0.014$, so the AI‑inspired construction achieves $u(n) \ge n^{1.014}$ for infinitely many $n$.[^1][^2]

**Structure of the proof.**

- The proof replaces the classic Gaussian‑integer construction (points corresponding to $a+bi$) with point sets derived from more complicated algebraic number fields that have richer symmetries.[^4][^1]
- Using tools like infinite class field towers and Golod–Shafarevich theory, the authors show these number fields exist and yield many unit‑length differences when embedded in the plane, leading to the $n^{1+\delta}$ lower bound.[^3][^1]
- The AI generated the core construction and argument; a group of nine external mathematicians extracted, checked, and simplified the proof in a human‑written companion paper.[^2][^4]

So the *solution* here is: an explicit infinite family of planar point sets with at least $n^{1+\delta}$ unit distances, which serves as a counterexample to Erdős’s conjectured asymptotic upper bound.[^1][^2]

***

## Erdős Problem \#1196 and related primitive‑set conjectures

**Conjecture (informal).** A *primitive set* $A\subset\mathbb{N}$ is one in which no element divides another. Erdős and co‑authors formulated conjectures (including \#1196) about the maximal size of certain “Erdős sums” over primitive sets restricted to large integers—roughly, that these sums are bounded by the sum over the primes, and that particular variants obey precise asymptotic bounds.[^5]

**AI‑guided proof.**

GPT‑5.4 Pro suggested a new probabilistic method, later developed into a full proof by Boris Alexeev *et al.* in the paper *Primitive sets and von Mangoldt chains: Erdős Problem \#1196 and beyond*:[^6][^5]

- The key AI‑inspired idea is to bound Erdős sums using **Markov chains with von Mangoldt weights**, where the transition probabilities encode divisibility relations among integers.[^7][^5]
- This “von Mangoldt chain” method leads to a general inequality that any primitive set $A$ satisfies a certain Erdős sum bound, which in turn implies the conjectured behavior for primitive sets of large numbers (\#1196) and for divisibility chains (\#1217).[^5]
- The same technique also yields a short proof of the original Erdős Primitive Set Conjecture (\#164) and a revised Banks–Martin “master” conjecture.[^5]

**What is explicitly proved.**

From the abstract and results:[^5]

- Two 1966 conjectures of Erdős–Sárközy–Szemerédi—on primitive sets of large numbers (problem \#1196) and on divisibility chains (\#1217)—are proved.
- The classic Erdős Primitive Set Conjecture (\#164) is proved, and it is shown that 2 is an “Erdős‑strong” prime (a particular technical strengthening).[^5]
- A revised form of the Banks–Martin conjecture is resolved via the same framework.[^5]

So the *solutions* are:

- A von‑Mangoldt‑chain inequality that bounds Erdős sums for every primitive set.
- Formal theorems confirming the truth of \#1196, \#1217, \#164, and a revised Banks–Martin conjecture, all obtained through the AI‑suggested probabilistic/divisibility framework.[^6][^5]

***

## Jacobian conjecture counterexample (Claude Fable 5)

**Conjecture (classical form).** Keller’s Jacobian conjecture (1939) asks: If a polynomial map $F:\mathbb{C}^n\to\mathbb{C}^n$ has everywhere nonzero constant Jacobian determinant, must $F$ be invertible (and have a polynomial inverse)?[^8]

**AI‑constructed counterexample.**

Levent Alpöge, working with Anthropic’s Claude Fable 5, produced an explicit map $F:\mathbb{C}^3\to\mathbb{C}^3$ such that:[^9][^8]

- The Jacobian determinant of $F$ is the *constant* value $-2$ everywhere (so the classical hypotheses of the conjecture are satisfied).[^9][^8]
- Nevertheless, $F$ is *not* injective: it sends three distinct points
    - $(0,0,-1/4)$,
    - $(1,-3/2,13/2)$, and
    - $(-1,3/2,13/2)$
all to the same image point $(-1/4,0,0)$.[^8][^9]

SymPy and other CAS checks verify both that the Jacobian determinant is identically $-2$ and that the images of these three points coincide, so $F$ is a genuine counterexample to injectivity under constant nonzero Jacobian determinant.[^9][^8]

**Form of the map.**

Public write‑ups describe $F=(F_1,F_2,F_3)$ as a low‑degree polynomial in three variables $x,y,z$ (all components are polynomials in $x,y,z$), explicitly chosen to satisfy:[^8][^9]

- $\det JF(x,y,z) \equiv -2$,
- $F(0,0,-1/4)=F(1,-3/2,13/2)=F(-1,3/2,13/2)=(-1/4,0,0)$.

Alpöge credits Claude Fable 5 with generating and testing candidate maps until this one was found. As of late July 2026, the result is announced on X and discussed by experts, with formal publication and peer review still in progress.[^10][^8]

So the *solution* is literally that explicit 3‑variable polynomial map, plus the short calculation showing constant determinant and 3‑to‑1 behavior, which falsifies the conjecture in dimension 3.[^9][^8]

***

## DeepMind AlphaProof Nexus: Erdős and OEIS conjectures

**Problems (collection).** DeepMind’s AlphaProof Nexus system was run on two curated lists:[^11]

- 353 unsolved problems from the Erdős Problems database.
- 492 open conjectures from the Online Encyclopedia of Integer Sequences (OEIS).

These include a mix of combinatorial identities, extremal bounds, and number‑sequence properties; each entry has a specific formal statement but most are too numerous to list individually.

**AI solutions / proofs.**

According to Center Consulting’s summary of the 2026 milestone:[^11]

- Nexus found *formal proofs* resolving 9 of the 353 Erdős problems.
- It also proved 44 of the 492 OEIS conjectures.
- All proofs were produced in a style compatible with proof assistants (i.e., machine‑checkable formal derivations).[^11]

Examples (as reported in the summary) include:

- An Erdős problem on extremal set systems with forbidden intersections resolved by constructing an explicit extremal family and proving optimality.[^11]
- OEIS conjectures about closed‑form formulas or recurrences for specific integer sequences, where AlphaProof Nexus produced inductive or generating‑function proofs that the proposed formulas are correct.[^11]

The explicit solution for each problem is:

- A fully formal, machine‑verified proof of the conjecture’s statement—either confirming the conjecture exactly as posed or proving a sharpened version if the AI found a stronger bound.[^11]

So here, the “solutions” are a batch of formal proofs, each attached to its respective Erdős or OEIS problem entry; DeepMind’s announcement emphasizes the *number* (9 Erdős, 44 OEIS) and the fact that all were previously labeled “open.”[^11]

***

## Ran–Teng spectral‑region conjecture (ChatGPT‑5.2‑assisted proof)

**Conjecture (informal).** Ran and Teng (2024) formulated a conjecture about the spectral region of a certain operator or matrix class—roughly, describing precisely which complex numbers can appear as eigenvalues under given structural constraints.[^12]

**LLM‑assisted proof.**

The VUB Data Analytics Lab report describes how ChatGPT‑5.2 (Thinking) helped produce a proof:[^12]

- Researchers posed the Ran–Teng conjecture to ChatGPT‑5.2 and iterated through four main proof drafts over seven sessions.[^12]
- The model proposed a sequence of lemmas and an overall structure (often involving resolvent estimates and contour arguments) that, once cleaned up by humans, yielded a full proof.[^12]
- Human mathematicians then checked every step, repaired gaps, and wrote a final paper giving a rigorous proof that Ran and Teng’s conjectural spectral description is correct.[^12]

So the *solution* is a conventional human‑written proof whose central structure and key lemmas were first proposed in LLM output; what is explicitly identified is the final theorem that the spectral region conjectured by Ran and Teng is indeed the actual spectrum of the operator class they studied.[^12]

***

## “Miscellaneous” Erdős problems solved or advanced by AI

**Problem set.**

Terence Tao and other observers track progress on the Erdős Problems database; news coverage in early 2026 notes that about 15 problems had moved from “open” to “solved,” with 11 explicitly involving AI tools like GPT‑5.2 or Gemini‑derived systems.[^13][^14]

**Nature of the solutions.**

Reported examples include:[^14][^13]

- An Erdős problem on sumsets of sparse sets where GPT‑5.2 suggested a sharp combinatorial argument that human researchers then formalized.[^13]
- Several small combinatorial geometry and additive number theory problems where AI located overlooked lemmas and recombined them into complete proofs.[^14]

In each case, the “solution” is a published or preprint proof that settles the problem or conjecture; the AI’s role is to propose the key steps or find the right existing ingredients. Individual statements are tracked in Tao’s GitHub table, but the common pattern is: AI‑suggested proof idea → human verification → new theorem resolving a previously open Erdős problem.[^13][^14]

***

If you’d like more detail for any one item—e.g., the exact polynomial formulas in Alpöge’s Jacobian counterexample, or a concrete OEIS conjecture Nexus proved—I can walk through that specific example step by step.
<span style="display:none">[^15][^16][^17][^18][^19]</span>

<div align="center">⁂</div>

[^1]: https://openai.com/index/model-disproves-discrete-geometry-conjecture/

[^2]: https://www.techtimes.com/articles/316955/20260521/openai-model-cracks-80-year-erds-conjecture-verified-its-harshest-previous-critic.htm

[^3]: https://cdn.openai.com/pdf/74c24085-19b0-4534-9c90-465b8e29ad73/unit-distance-proof.pdf

[^4]: https://letsdatascience.com/news/openai-model-disproves-erds-unit-distance-conjecture-af7968c0

[^5]: https://arxiv.org/abs/2605.00301

[^6]: https://www.buildfastwithai.com/blogs/gpt-5-4-solved-a-60-year-math-problem-what-happened

[^7]: https://note.com/mi6242/n/n60f4bee341b4

[^8]: https://ai-tldr.dev/releases/anthropic-fable-jacobian-disproof/

[^9]: https://lilting.ch/en/articles/jacobian-conjecture-counterexample

[^10]: https://reasoncore.dev/post/levent-alpoge-posts-fableattributed-polynomial-claiming-to-disprove-the-jacobian-conjecture

[^11]: https://www.centerconsulting.com/ai-library/milestones/2026-ai-resolves-open-conjectures

[^12]: https://phys.org/news/2026-03-chatgpt-mathematical-proofs.html

[^13]: https://techcrunch.com/2026/01/14/ai-models-are-starting-to-crack-high-level-math-problems/

[^14]: https://note.com/ai_tech_notes/n/nd2ef4ae0ee3a?hl=en

[^15]: https://dailyaiworld.com/blogs/claude-fable-jacobian-conjecture-counterexample-2026

[^16]: https://www.packetnebula.com/articles/fable-5-jacobian-conjecture-counterexample/

[^17]: https://www.agenticbrew.ai/news/b94a88cf-b5db-4e06-ac1a-3497ca4870e5/openai-s-general-purpose-reasoning-model-disproves-erdos-unit-distance-conjecture

[^18]: https://hyper.ai/en/stories/020c7626bd2412c4953bc6db62867cce

[^19]: https://www.developersdigest.tech/blog/jacobian-conjecture-counterexample-fable

