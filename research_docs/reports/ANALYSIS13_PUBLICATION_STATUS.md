# Analysis 13 publication audit — 15 October 2026

## Confirmed from the user's Windows inventory

- Seven notebook files: 13A, 13B, 13C, 13D, original 13E, 13E continuation, and 13F.
- 13A–13F CSV and JSON outputs, including 18-row completed 13B spatial transition table, 13E same-date tile-union QA and 13F hypothetical scenarios.
- Ten selected Analysis 13 figures: two 13A, six 13B, one 13C and one 13F.
- Unit test file `tests/test_analysis13.py`.
- Publishing clone exists on `main`, points to the expected GitHub remote; no changes were shown by `git status --short`.
- The source directory `src/analysis13/` was not listed because the PowerShell inventory filtered on filenames; its presence must be checked, not assumed absent.

## GitHub audit

The GitHub `main` branch contains earlier Notebooks 09–12, selected scene-12 data and the shortened README. No Analysis 13 notebooks, code, figures, tables or reports were listed in the GitHub repository tree at audit time.

## Publication posture

Publish 13A–13C as exploratory radar screening; 13D as hydrological chronology/data readiness; 13E as optical-reference usability assessment without accuracy claims; 13F as hypothetical methane detectability scenarios only. No independent water-class accuracy, measured methane flux, stage–area relation or causal flood-to-methane inference is supported.

## What to exclude

- `.ipynb_checkpoints/`, `__pycache__/`, `.venv/`, `.git/`, Earth Engine credentials, temporary exports and scene GeoTIFF caches.
- The reviewed 13B ZIP itself (the CSV, six figures and report are staged individually).
- Any blank reference-labelling templates represented as validated observations.

## Recommended process

1. Run `stage_analysis13.ps1` in PowerShell from this kit's extracted folder. It checks paths, synchronizes the publishing clone, copies selected files without deleting originals, and stages them with Git **without committing or pushing**.
2. Review `git diff --cached --stat` and `git diff --cached -- README.md` in the publishing clone.
3. When satisfied, `git commit -m "Publish Analysis 13 exploratory findings and reproducibility package"` then `git push origin main`.

The README draft should not be confused with proof that any additional remote-sensing processing was run.
