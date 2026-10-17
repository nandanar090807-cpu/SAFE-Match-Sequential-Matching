# SAFE-Match — Development and Tool Provenance

**Participant:** Nandan A R. Individual submission.

- OpenAI ChatGPT was used for coding assistance, troubleshooting, code review, test planning, documentation, report drafting and release packaging.
- The delivered inference system is **not** an AI language model. `policy.py` is a deterministic, CPU-only constraint/heuristic/graph-matching policy. No ChatGPT API is called while it runs.
- **Training/model data:** No learned model, model weights, training dataset, external model service, GPU or training compute. Evaluation uses public organizer seed-generated simulations. Experiment seeds 101/102/103. Inference random seed not applicable.
- **Code dependency:** NetworkX 3.6.1 under BSD-3-Clause, vendored with source and license. The `vendor/` tree has a SHA-256 manifest and accompanying verification utility.
- **Organizer kit:** Public `kit.py`, `evaluate.py` and official reference policy with organizer licensing files in the complete release ZIP.
- **Contestant code/documentation rights:** See the repository `LICENSE`.
- **Reproducibility:** See [FINAL_SUBMISSION_REPORT.md](FINAL_SUBMISSION_REPORT.md), [results/public_101_103.json](results/public_101_103.json) and the [successful Docker validation workflow](https://github.com/nandanar090807-cpu/SAFE-Match-Sequential-Matching/actions/runs/39024657695).
