# Where camera-based heart-rate estimation breaks down: a stratified error audit of rPPG

FIT2082 Computer Science Research Project, Semester 2 2026. Samith Pai. Supervisor: Talha Ilyas.

## Regenerate the headline results (one command)

```bash
python src/make_results.py
```

This rebuilds every table in `results/tables/`, every figure in `results/figures/` and `results/headline.md`
from the saved outputs (`results/ubfc/*.log`, `results/windows/subject_*.csv`, `results/subject_meta.csv`).
It needs no video and no GPU.

## Full pipeline (Google Colab: `notebooks/FIT2082_rPPG_Audit.ipynb`)

| Step | Command / notebook part | Output |
|---|---|---|
| Environment | Part A: clone rPPG-Toolbox at commit `b7500b8`, `python src/patch_toolbox.py <toolbox>` | patched toolbox |
| RQ1a UBFC-rPPG reproduction | Part B: toolbox `main.py` with the configs in `results/configs_used/` | `results/ubfc/*.log` |
| rPPG-10 checks | Part C: inventory, metadata, group sizes, alignment on 10 files | `results/rppg10_inventory.csv`, `results/subject_meta.csv`, `results/alignment/` |
| rPPG-10 audit | `python src/run_audit.py --data <rPPG-10> --toolbox <toolbox> --out results --device cuda` | `results/windows/` |
| Checkpoint sensitivity | `... --weights UBFC-rPPG --no-unsup` | `results/windows_UBFC-rPPG/` |
| Tables and figures | `python src/make_results.py` (+ `--tag`, `--exclude-drift`, `--rq3-response`, `--windows`) | `results/tables*/`, `results/figures*/` |

## Layout

```
configs/analysis.yaml     analysis settings fixed before looking at results
src/patch_toolbox.py      Colab/NumPy-2 compatibility patches for rPPG-Toolbox (no method maths changed)
src/audit.py              rPPG-10 reading, ECG reference (Pan-Tompkins), toolbox methods, windowing
src/run_audit.py          per-window results for every method x subject x ROI (resumable)
src/alignment.py          video-ECG alignment check
src/stats_rq.py           metrics, cluster bootstrap, RQ2 tests, RQ3 mixed-effects models, Bland-Altman
src/make_results.py       all tables and figures
results/                  outputs (small CSV/PNG/log files; no raw data)
lab_notebook.md           dated log of decisions and runs
requirements.txt          package versions frozen from the Colab runtime used
```

## Data (not in this repository)

* UBFC-rPPG DATASET_2 (42 videos): https://sites.google.com/view/ybenezeth/ubfcrppg. Cite Bobbia et al., Pattern Recognit. Lett. 2019.
* rPPG-10 (26 subjects): https://data.mendeley.com/datasets/bx8982xgwt/1. Cite Rodrigues et al., Data in Brief 2025.

## Seeds

Deterministic steps run once. Cluster bootstraps use seeds 2082, 2083 and 2084, and report the mean CI with the SD across seeds.
