# SAFE-Match | Final Round 2 Technical Report

**Participant:** Nandan A R (individual; team size 1)  
**Institution:** Indian Institute of Technology Madras (IIT Madras), BS in Management and Data Science  
**Competition:** IIT Madras × Romeo & Juliet, The Sequential Matching Problem  
**Date:** 17 October 2026

## 1. Solution and hypothesis

**SAFE-Match** is a constraint-first, clarification-aware sequential matching policy. Its aim is to improve **Mutual Second-Meeting Intention (MSMI) per 100 arrived members** while respecting reciprocal hard preferences, scheduling, a limited clarification budget, and the organizer's JSON policy interface. MSMI requires an eligible first date followed by affirmative second-meeting intention from both participants within the required observation window. More introductions alone do not count as success.

The Round 1 hypothesis was that reciprocal feasibility filtering, paired information requests, and globally weighted disjoint allocation could outperform immediate greedy pairing. Round 2 implements and tests that approach in executable code. The observed public experiments offer limited supporting evidence; they do not establish private-case or real-world superiority.

## 2. Methodology and algorithms

**Clarification phase:** At each decision step, the policy reads the current observable member state. It selects paired *hard-constraint* question bundles that may reveal reciprocal feasibility, subject to the public kit's **12-unit daily clarification budget**; remaining capacity may be assigned to relevant soft-attribute questions. Unknown hard constraints are not guessed or assumed satisfied, and unavailable/delayed answers remain unknown.

**Matching phase:** The policy enumerates pairs eligible under both parties' observed hard constraints and availability. It then computes heuristic soft-compatibility edge weights and runs **maximum-weight matching on a general, non-bipartite graph** with NetworkX to choose nonoverlapping introductions. It revalidates the proposed allocation and includes a deterministic greedy/augmenting fallback if the primary solver fails. Selection uses only current visible information; no future outcomes, hidden member data or learned predictor are accessed.

**Inference:** Python 3.11, deterministic CPU-only policy; NetworkX 3.6.1 vendored with source and licence. No trained model or model weights; no inference random seed, GPU, network API or runtime credentials. Edge weights are heuristic proxies, **not calibrated probabilities of MSMI**.

## 3. Public benchmark: baselines and results

We executed **72 valid synthetic full episodes** using the organizer's public kit, comparing SAFE-Match against **greedy**, **no clarification**, and **random feasible** policies on the **same three seeds (101, 102, 103)** across all **six scenario families** (18 episodes per policy). Primary metric: mean MSMI events per 100 arrived members, with equal episode/scenario representation. The compared full-episode machine-readable data are in [`results/public_101_103.json`](results/public_101_103.json) and the release ZIP.

| Policy | Valid episodes | MSMI events | MSMI per 100 arrived | Clarification units |
|---|---:|---:|---:|---:|
| SAFE-Match | 18/18 | 19 | **0.528** | 4,478 |
| Greedy | 18/18 | 14 | 0.389 | 3,720 |
| No clarification | 18/18 | 5 | 0.139 | 0 |
| Random feasible | 18/18 | 10 | 0.278 | 3,720 |

### Scenario-level MSMI events per 100 arrived

Three matched seeds in each family; rounded to three decimals.

| Scenario family | SAFE-Match | Greedy | No clarification | Random feasible |
|---|---:|---:|---:|---:|
| Development | 1.000 | 0.500 | 0.167 | 0.333 |
| Sparse geography | 0.000 | 0.167 | 0.000 | 0.167 |
| Cold start | 0.167 | 0.167 | 0.000 | 0.167 |
| Delayed feedback | 0.333 | 0.500 | 0.333 | 0.167 |
| Regime shift | 0.833 | 0.500 | 0.167 | 0.500 |
| Preference drift | 0.833 | 0.500 | 0.167 | 0.333 |

Across its 18 episodes, SAFE-Match generated **1,438 assignments** and recorded **771 missing feedback events**. A separate public replay with diagnostics reported **37.50% average first-introduction coverage** and **6.78 days average first-introduction wait among served members**. Those replay diagnostics are in `results/public_101_103_with_diagnostics.json` inside the release ZIP. The public experiment JSON records per-episode wall runtimes, assignments, feedback, costs and the individual event outcomes. These numbers describe **simulated public test cases**, not observed production-world success.

SAFE-Match's seed-blocked event differences versus greedy, summed across the six scenarios within each seed, were **0, +2, +3**. With only three independent seeds, the margin should not be interpreted as statistically conclusive.

## 4. Hypothesis-driven optimization and ablation

A proposed soft-question early-filtering change was tested on **18 separate full episodes** (three seeds × six families). The alternative produced **14 MSMI events versus 14** for the retained planner, while using **4,551 instead of 4,537** clarification units. Because it failed to improve the primary outcome and increased question cost, it was **rejected**. This is evidence of a tested engineering choice, not a private-leaderboard result.

## 5. Improvements made after Round 1

The Round 1 research design was developed into a runnable, state-aware algorithm with a defined clarification planner, reciprocal hard-feasibility check, weighted general-graph allocation and post-allocation validation. Subsequent audits fixed release-root packaging and failure-path/memory-handling problems; protected deterministic fallbacks; bundled and checksum-verified the required dependency; added boundary, adversarial, seed-differential and regression tests; and documented limitations rather than claiming learned outcome probabilities. The final inference implementation retained the tested planner when a proposed modification showed no experimental benefit.

## 6. Executable validation and Docker evidence

**Official public Docker check: PASSED.** [GitHub Actions Run #39024657695](https://github.com/nandanar090807-cpu/SAFE-Match-Sequential-Matching/actions/runs/39024657695) checked the **exact canonical ZIP SHA-256**, unpacked it, executed **46/46 successful unit tests**, built the Docker image, completed the restricted offline organizer evaluator on **seed 101, development** (valid; **2 MSMI events**) and passed strict Docker preflight plus final episode-validity assertions. All recorded workflow steps passed. This later result supersedes the older local reports' stated Docker-unavailable limitation; the historical audit JSON remains a truthful record of its earlier environment.

Other recorded checks included seven adversarial suites, 36/36 restricted local process calls, 296/296 vendored file checks and large request/eligibility stress cases. Public Docker success does **not** guarantee all private episodes pass.

**Canonical full release ZIP:** [SAFE_Match_Final_Deep_Audited_Release_2026-10-17.zip](SAFE_Match_Final_Deep_Audited_Release_2026-10-17.zip)  
**Archive SHA-256:** `a43ecd17f7cdaa65060ef480c9b69ce355802c17885f4484eb4bb5940d39a17e`  
**Full project:** Python source, `Dockerfile`, `vendor/`, tests, official evaluator, benchmark JSON, build/reproduction commands and development provenance included inside the ZIP.

### Reproduction (from the extracted release ZIP root)

```bash
python -S verify_vendor.py
PYTHONPATH=vendor python -S -m unittest -v
docker build -t safe-match:submission .
python evaluate.py --image safe-match:submission --seeds 101 --variants development --output results/container_check.json
python preflight.py --require-docker
```

Optional extended evaluation in the full organizer checkout:

```bash
python verify_data.py
python evaluate.py --seeds 101,102,103 --variants all --output results/final.json
```

The public dataset/check files expected by `verify_data.py` are **not all bundled in the contestant archive** and must be sourced from the complete organizer starter checkout. Evaluation data comprise synthetic seed-generated public scenarios rather than any privately obtained participant data. The organizer simulator's reference policy, `kit.py` and `evaluate.py` were used for reproducible offline comparisons.

## 7. Tools, assets, licences and compute

- **Code/logic:** Contestant's SAFE-Match implementation; `LICENSE` included in the project/repository.
- **Dependency:** NetworkX 3.6.1 (BSD-3-Clause), bundled at `vendor/` with its licence and `VENDOR_SHA256.json`.
- **Organizer public kit:** Included reference simulator, evaluator and licensing files (organizer MIT licence).
- **AI disclosure:** OpenAI ChatGPT assisted software coding/review, tests, error analysis, report writing and release preparation. No LLM is used at runtime and no external inference API is needed.
- **Training:** None. No training dataset, training seeds or training compute; synthetic benchmark seeds 101, 102 and 103, deterministic inference.
- **Environment:** Python 3.11, CPU-only, Docker `python:3.11-slim`, restricted offline evaluation, unprivileged process. The base image must be downloaded during initial image construction; the built inference process does not need the network.

## 8. Limitations and future work

- **Private performance unknown.** Three independent public population seeds do not justify a leaderboard or real-world improvement guarantee.
- **Scenario imbalance.** SAFE-Match scored **zero MSMI in sparse geography** in this experiment and performed below greedy in delayed feedback. Geographic sparsity and response latency deserve targeted policy improvement.
- **Uncalibrated heuristics.** The graph weight is not an estimated MSMI probability; exact maximum-weight graph matching does not optimize the sequential, delayed-outcome process itself.
- **Clarification cost and fairness.** SAFE-Match consumed more questions than the greedy baseline. Waiting and coverage were measured descriptively, not optimized with formal subgroup fairness constraints. Further work should test budget-aware value of information and subgroup-level outcomes.
- **Missing feedback.** 771 missing-feedback events across the 18 SAFE-Match synthetic episodes complicate causal conclusions.
- **Robustness.** The public image passed the demonstrated evaluator episode and regression suite, but no private-case guarantee is possible.
