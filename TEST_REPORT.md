# Reproducible test ledger (16 October 2026 historical snapshot)

This ledger documents **earlier, 16 October experiments**. Current source passes **46/46 unit tests** with vendored NetworkX **3.6.1**, confirmed on 17 October. See `FINAL_INDEPENDENT_AUDIT_2026-10-17.md` for current re-execution evidence. Older references to NetworkX 3.4.2 are historical only. All historical numerical observations are saved under `results/`.

| Check | Actual outcome | Evidence |
|---|---|---|
| Original source regression suite | 33 passed, 0 failed | Previous baseline ZIP; `results/unit_tests_37.log` includes all 33 unchanged tests |
| Corrected build regression suite | **37 passed, 0 failed** | `results/unit_tests_37.log` |
| Supplemental stress suite | **7 passed, 0 failed** | `results/adversarial_results_reproduced.json`, `stress_process.py` |
| Independent eligibility comparison | **62,573 pairs**, zero differences vs released `kit.eligibility` | Stress JSON |
| Six-family synthetic ask/match legal-action smoke tests | **84 decisions**, zero invalid actions | Stress JSON |
| Dense 200-member input | **19,900 feasible edges; 100 disjoint pairs**, 1.98–2.05s observed | Stress JSON, `results/dense200_request.json` |
| Sparse 200-member state | Zero pairs (as expected) | Stress JSON |
| Near-maximum memory payload | **900,036-byte output**, finite and carried unchanged | Stress JSON |
| Missing NetworkX fallback | **100 disjoint pairs; 0.18 seconds**, no crash | `results/fallback_no_networkx.json` |
| Two-core CPU affinity + 1 GiB virtual-memory cap | **1.82s wall**, **115,864 KiB max RSS**, exit 0 | `results/limited200_runtime.log` |
| Official unmodified evaluator (seed 711, development) | **valid; 1 MSMI; 102 introductions; 267 ask units** | `results/verified_evaluator_711.json` |
| Decision-by-decision regression against pre-fix code, same seed | **Identical action SHA-256** | `results/prior_evaluator_711.json`, `results/verified_evaluator_711.json` |
| Three-seed × six-family × four-policy public replay | **72/72 valid**; SAFE-Match 19 MSMI vs 14 greedy, 10 random, 5 no-asks | `results/public_101_103_with_diagnostics.json` |
| Proposed early clarification filter | **Rejected:** 14 vs 14 MSMI, +14 ask units over 18 matched scenarios | `results/rejected_early_filter_1111_1113.json` |
| Docker build + offline invocation | **NOT RUN** (Docker unavailable in execution environment) | No Docker logs claimed |
| Historical NetworkX 3.4.2 runtime | **Superseded** by self-contained NetworkX 3.6.1 release; actual Docker build remains unverified | `README.md`, `verify_vendor.py` |
| Private evaluation | **UNKNOWN** | No access |

**Exact organizer reference file Git blob hashes:**

- `kit.py`: `b0356b84211debdb8fc1c3ea81348a034dd2ddbd`
- `evaluate.py`: `f9fa2617a3ef84da85502ec2bd730185d5049f65`

The stress suite is portable: `python stress_process.py`. The built-in regression tests are portable: `python -m unittest -v`. See README for all comparison commands.

**Interpretation:** Zero invalid local actions in this test corpus is not a proof that every private input will pass. The primary reported advantage uses only three independent public seeds and should not be converted into a statistically certain winning forecast. Docker remains the blocking compliance check.