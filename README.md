# SAFE-Match | Sequential Matching Problem

Audited Round 2 implementation for the IIT Madras × Romeo & Juliet Sequential Matching Problem, by **Nandan A R**.

## Release source

The complete audited and reproducible project is stored in [SAFE_Match_Final_Deep_Audited_Release_2026-10-17.zip](SAFE_Match_Final_Deep_Audited_Release_2026-10-17.zip). It contains the runnable `policy.py`, offline vendored matching dependency, `Dockerfile`, organizer's public evaluation kit, 46 unit tests, adversarial tests, result files, technical report, provenance and licenses.

**Verified release archive SHA-256:** `a43ecd17f7cdaa65060ef480c9b69ce355802c17885f4484eb4bb5940d39a17e`.

The release archive has passed local tests. **Docker and organizer private evaluation were not verified** as of packaging. Do not equate local benchmark results with hidden leaderboard performance.

## Reproduce

```bash
unzip SAFE_Match_Final_Deep_Audited_Release_2026-10-17.zip -d safe-match
cd safe-match
python -m unittest -v
python preflight.py --require-docker
```

Full instructions, source code, technical report and machine-readable results are inside the release archive. See also the repository workflow for container validation.

## Competition submission

Submit an immutable public source reference (full 40-character commit SHA or version-specific archive and SHA-256) and direct report/results URLs via the organizer's **Final submission** GitHub issue form. Publishing this repository does **not** by itself submit an entry to the organizers.

The organizer announcement specified **17 October 2026, 11:59 PM IST** as the final deadline.

## Direct repository files

- [Audited policy source](policy.py)
- [Dockerfile](Dockerfile)
- [Technical report](REPORT.md)
- [Test report](TEST_REPORT.md)
- [Public matched-seed benchmark JSON](results/public_101_103.json)
- [Machine-readable final audit](results/FINAL_INDEPENDENT_AUDIT.json)
- [Archive Docker validation workflow](.github/workflows/validate-release.yml)

The byte-exact archive remains the canonical complete project: the directly visible files are for review; unpack the archive to execute all tests with its bundled `vendor/` dependency and official kit.
