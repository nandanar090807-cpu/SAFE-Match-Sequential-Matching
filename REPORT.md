# SAFE-Match: technical retest and remediation (16 October historical results)

**Author:** Nandan A R · **Date:** 16 October 2026 · **Status:** locally tested; Docker not verified

**Current-release notice (17 October):** This report contains historical experiments and earlier test counts. `FINAL_INDEPENDENT_AUDIT_2026-10-17.md` is the current, evidence-backed pre-submission ledger; the released `policy.py` behavior is unchanged from the vendored ZIP.

## Competition objective and policy

The released evaluation metric is Mutual Second-Meeting Intention (MSMI) per 100 arrived members, averaged equally across six scenario families. An MSMI event requires a first date within 30 simulation days of assignment and recorded affirmative second-meeting intentions from both members within three days of the date. A lawful introduction also requires reciprocal feasibility and availability. The target is not the number of introductions, generic acceptance or attribute similarity.

SAFE-Match constructs reciprocal hard-constraint feasible edges from the current public state only. It uses NetworkX maximum-weight general-graph matching to allocate disjoint pairs, revalidates the batch against observed hard constraints, and falls back to a deterministic greedy/augmenting method if the solver is unavailable. Heuristic soft-attribute weights are a surrogate for expected event value. The clarification planner uses a 12-unit daily budget, prioritizes paired hard bundles where both answers could unlock an edge, then uses leftover budget for relevant soft attributes. Missing or declined hard preferences are never inferred. No lookahead into unobserved data is permitted.

The previous competitive improvement filtered out three soft questions absent from the released outcome generator (`emotional_availability`, `space_for_relationship`, `relocate`). The matching score still uses these observed fields as minor heuristics: do not claim they are mathematically justified MSMI probabilities. The released generator may not represent private tests.

## Newly executed retest on 16 October

- **33 existing regression tests passed** before remediation.
- **37 tests passed** after adding four new tests for root-level packaging, image input files, and safe fallback memory preservation/nonfinite sanitization.
- **Seven adversarial suites passed**, including an observed 62,573 pairwise eligibility comparisons with zero mismatches against the exact released `kit.eligibility` function, 84 legal in-process ask/match calls over six scenario families, repeat-pair and determinism checks, empty budget handling, and near-limit memory roundtrip.
- A 200-member input with **19,900 feasible edges** returned 100 nonoverlapping pairs in a successful fresh Python process. The local measured wall time was **2.05 seconds** using the currently installed NetworkX 3.6.1.
- A separate two-core-affinity, 1 GiB address-space run completed the dense case in **1.82 seconds wall time**, with **115,864 KiB peak resident memory**. This is a local process check, not Docker verification.
- The unmodified public `evaluate.py` executed a 60-decision-day plus 40-follow-up-day episode on seed 711 (development scenario) for both the previous and corrected package. **Both were valid**, with **1 MSMI event, 102 introductions, 267 clarification units, and identical action SHA-256** (`8a464cd6204b7b7c5bea9953dcb38c88876a42785320e1edd7fd7dd09c6c69ce`). Timing differs naturally between runs.
- A proposed early-filtering refinement to the soft-question planner was **rejected** after 18 full episodes (3 new seeds × 6 families): MSMI events remained **14 versus 14**, while clarification cost increased **4,537 → 4,551**. The released policy retains the original, better-performing selection order.

Complete logs, inputs and raw results accompany this report.

## Confirmed defects and resolution

| Severity | Finding | Action | Validation |
|---|---|---|---|
| High (submission packaging) | Previous ZIP only held inference entrypoint and Dockerfile inside `candidate/`, not its root | Place both at root; use a clean build context | Root layout regression test passed |
| Medium (fallback correctness) | Unexpected malformed state could cause the safe-empty fallback to replace valid incoming memory with `{}` | Preserve a finite, bounded JSON memory value, otherwise use `null`; bound diagnostic string | Two new subprocess regression tests passed |
| Low (documentation) | A comment said edge score incentivized waiting despite no waiting term | Remove misleading comment; make surrogate limitations explicit | Source review and passing unit suite |
| Optimization candidate rejected | Early filtering unused soft fields could alter which later soft questions receive budget | Did not deploy | 18 matched-seed full-episode comparison, no MSMI gain and slightly higher cost |

## Important unresolved issues

1. **Docker build/assessed image execution:** not available in this audit environment. The latest release bundles and checksum-verifies NetworkX **3.6.1** and runs it successfully in isolated `python -S` tests. The older 3.4.2 installation issue no longer applies. **Actual Docker compatibility remains unverified** pending a Docker-enabled runner.
2. **Private evaluation and statistical confidence:** a finite number of public synthetic worlds cannot demonstrate first-place potential or a reliable improvement on private seeds. Earlier public-seed gains may be concentrated in some seeds; scenarios are not statistically independent when population seeds are reused.
3. **Clarification objective:** current heuristic is not a calibrated Monte Carlo value-of-information policy. Unobserved answers are never used, but extra questions may have low expected return.
4. **Fallback optimality:** the general-graph greedy/augmenting fallback is not globally optimal when more than 16 vertices remain. The primary NetworkX solver is exact for the given weighted graph, not for the future sequential MSMI objective.
5. **Outcome calibration:** the fixed surrogate is not calibrated to the official complete recorded MSMI event; no causal advantage is asserted from the data.

**Judgement:** Code is eligible for continued testing, with confirmed packaging and fallback faults fixed. **Conditionally ready only after Docker validation.** The current evidence is insufficient to promise ranking or victory.

## Additional failover test

A separate 200-member / 19,900-edge input was run with `python -S policy.py`, which disables site-package imports and therefore forces the dependency-free fallback path. It exited successfully in **0.18 seconds** locally, returned 100 disjoint pairs, and emitted no diagnostics. This is a validity/runtime smoke test only; the fallback is not guaranteed to achieve the global maximum matching weight. See `results/fallback_no_networkx.json`.

## Repeated official-kit scenario comparison (seeds 101–103)

A fresh, unmodified-kit, trusted *in-process* experiment compared the corrected policy with all three published baseline modes on the same 3 seeds × 6 scenario families, for **72 valid policy episodes**. A second execution added coverage and first-introduction waiting-time diagnostics and reproduced the original episode MSMI/cost totals exactly.

| Policy | Valid episodes | MSMI events | MSMI per 100 arrived | Clarification units | Mean first-introduction coverage | Mean wait among served (days) |
|---|---:|---:|---:|---:|---:|---:|
| SAFE-Match | 18/18 | **19** | **0.528** | 4,478 | 37.50% | 6.78 |
| Organizer greedy | 18/18 | 14 | 0.389 | 3,720 | 37.17% | 6.45 |
| Organizer no-asks | 18/18 | 5 | 0.139 | 0 | 14.28% | 4.17 |
| Organizer random | 18/18 | 10 | 0.278 | 3,720 | 37.67% | 6.54 |

Other recorded diagnostics: SAFE-Match assigned 1,438 introductions and recorded 771 missing feedback events across the 18 episodes, versus 1,437 introductions and 819 missing feedback events for greedy. Mean wait excludes unserved people; coverage records the share introduced at least once.

This public sample favors SAFE-Match on the primary outcome, but only three independent population seeds are represented. The seed-blocked SAFE-Match-versus-greedy MSMI differences (events summed across six related scenarios) were **0, +2, +3** for seeds 101, 102 and 103 respectively. That is far too little independent evidence for a reliable private-evaluation claim. One family, sparse geography, scored zero qualifying MSMI events for SAFE-Match on all three seeds; addressing this might require a different clarification strategy, but no untested change was deployed.

**Exact commands and data:** `python reproduce_public.py --seeds 101,102,103 --variants all --output results/public_101_103_with_diagnostics.json`. A complete action digest for every episode is in the JSON. The 72 episodes used the exact public `kit.py`; they are not the 120-process Docker evaluator. Seed 711 *was* separately checked using the unchanged public `evaluate.py` in 120 fresh processes, with an identical action digest before and after the fixes.