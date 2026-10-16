# FIT2082 rPPG audit on MMPD — project guide

Companion to `notebooks/FIT2082_MMPD_Audit.ipynb`.

## 1. What the project must deliver (from the proposal)

| RQ | Question | Measured by |
|---|---|---|
| RQ1 | Heart-rate error of the methods, overall and against published values | MAE, RMSE, MAPE, Pearson r, SNR, per window and per subject; first reproduce a published UBFC-rPPG result |
| RQ2 | How error changes with skin tone, lighting and motion, and whether the differences are significant | Same metrics per group, bootstrapped 95% CIs, **n subjects behind every estimate** |
| RQ3 | Which factor explains the most variation, and do classical and deep methods react the same way | Mixed-effects model, subject random effect, variance per factor, family comparison |

Checklist:

- [ ] rPPG-Toolbox for every method, one shared preprocessing path
- [ ] Classical: GREEN, CHROM, POS, OMIT, LGI, PBV
- [ ] Deep: PhysNet, TS-CAN, EfficientPhys — released weights, inference only, provenance recorded
- [ ] Baselines: mean-HR predictor, GREEN as the floor for a real method, published toolbox values
- [ ] 30 s non-overlapping windows
- [ ] Video–reference timing checked on 10 files before any results
- [ ] Group sizes counted before analysis, collapse rule stated openly
- [ ] Metrics at window **and** subject level
- [ ] Bootstrapped CIs with subject counts for every group
- [ ] Paired tests for lighting and motion; between-subject test for skin tone
- [ ] Non-parametric tests, multiple-comparison correction, CIs carrying the interpretation
- [ ] "The data cannot settle this" where CIs overlap
- [ ] Fixed seeds; anything random reported as mean ± SD over three runs
- [ ] Bland–Altman per subgroup
- [ ] RQ3 in statsmodels with the skin-tone asymmetry stated
- [ ] Model spec checked by a second reader (W10)
- [ ] Public Git repo with `configs/`, `src/`, `results/`, pinned `requirements.txt`, dated lab notebook, README with one command

| Milestone | When | Where |
|---|---|---|
| M1: published UBFC number reproduced | W4 | notebook B4 |
| M2: overall results table, RQ1 answered | W7 | E1, `rq1b_mmpd_overall.csv` |
| Decision point: group < 4 subjects | W8 | C2 prints the check |
| M3: RQ3 answered, checked by a second reader | W10 | E1, `rq3_*.csv` |
| Report draft to supervisor | **Fri 23 Oct** | |
| Final submission | **Mon 2 Nov** | |

## 2. Decisions taken, and what to change in your slides

| # | Decision | Why | Slide/report change |
|---|---|---|---|
| 1 | Mini-MMPD (48 GB, 80×60) | 370 GB is impossible on free Colab; everything is resized to 72×72 anyway | Note the reduced-resolution choice (your risk register allows it) |
| 2 | Factors: skin tone, lighting, motion | Matches the proposal now that MMPD is available | Revert any rPPG-10/ROI wording |
| 3 | Skin groups 3 vs 4–6 | MMPD has Fitzpatrick 3–6 only; "I–III vs IV–VI" maps to this | Skin-tone axis shows 3, 4, 5, 6 — no I–II |
| 4 | Reference HR from the contact PPG via the same FFT path | MMPD gives one PPG sample per frame | No ECG/Pan-Tompkins step |
| 5 | Band-pass 0.75–2.5 Hz, periodogram peak | Settings behind the published tables | Slide says 0.7–4.0 Hz + Welch — fix |
| 6 | Nine methods | Proposal said six to eight; slide title says eight | Fix the count |
| 7 | PURE-trained weights only | No released checkpoint saw MMPD, so no leakage | One line in Methods |
| 8 | Post-exercise videos kept, exercise as covariate | Keeps 20% more data; sensitivity run excludes them | One line |
| 9 | RQ3 on log(1+|error|) | Absolute errors are strongly right-skewed | One line, with raw-error sensitivity |
| 10 | Black final frame repaired; PhysNet tail chunk added | Otherwise 1800-frame videos lose a window, and PhysNet would have half the windows of other methods | Two lines in Methods |

## 3. Setup (once)

1. Google Drive: `MyDrive/FIT2082_rPPG/data/mini_MMPD/`.
2. UBFC-rPPG: dataset page → Drive link → right-click `DATASET_2` → *Organize → Add shortcut → My Drive*. Don't download it.
3. Mini-MMPD: OneDrive link + password → download ~8 subject folders at a time → upload to `data/mini_MMPD/`.
4. Colab: upload the notebook, set Runtime → T4 GPU.
5. GitHub: empty repo + fine-grained token in Colab Secrets as `GH_TOKEN`.

## 4. Run order and "done when"

| Step | Notebook | Done when |
|---|---|---|
| 1 | Part A | "rPPG-Toolbox imports OK" and the patch list prints |
| 2 | B0–B3 | "42 of 42 videos cached" for each run |
| 3 | B4 | **Milestone 1**: every method within tolerance, or you've written down why not |
| 4 | B5 | UBFC 30 s window table (context for the MMPD comparison) |
| 5 | C0–C2 | batch copied, labels catalogued, group sizes printed and logged |
| 6 | C3 | timing check on 10 videos, median lag ≈ 0 |
| 7 | D1 | pilot subject looks sane (2 windows per video, plausible reference HR) |
| 8 | D2 | batch done; then swap batches in Drive and repeat C0 → D2 until 33/33 |
| 9 | D3 | checkpoint-sensitivity run |
| 10 | E1–E2 | `headline.md` plus three sensitivity headlines |
| 11 | F | pushed to GitHub; `python src/make_results.py` works in a fresh clone |

Compute: Part B is a few hours (reading 42 large videos from Drive four times). Part D is roughly 10–20 seconds per video on a T4, so about 2–3 hours for all 660, spread across batches. Everything is resumable.

## 5. Timeline from here (Fri 25 Sep, end of W8)

| Dates | Do |
|---|---|
| Sat 26 – Sun 27 Sep | Setup, Part B (Milestone 1), first MMPD batch |
| Mid-sem break (28 Sep – 4 Oct) | Remaining batches, Part D complete, first pass of Part E |
| W10 (5 Oct) | RQ3 final, second reader checks the model spec (M3) |
| W11 (12 Oct) | Figures, tables, Results section |
| W12 (19 Oct) | Intro, Discussion, Limitations; **draft to supervisor Fri 23 Oct** |
| SWOTVAC | Revisions, repo cleanup, **submit Mon 2 Nov** |

## 6. Report outline and where each piece comes from

1. **Introduction** — proposal §1.
2. **Research questions** — proposal §2, unchanged.
3. **Methods** — MMPD (33 subjects, 660 one-minute videos, 4 lighting × 4 motion conditions, Fitzpatrick 3–6, contact-PPG reference) and UBFC-rPPG for validation; toolbox commit and patches; 72×72 crop; nine methods and checkpoint provenance; 30 s windows; 0.75–2.5 Hz band-pass; statistics (cluster bootstrap 5000 × 3 seeds, Mann–Whitney / Friedman + Wilcoxon with Holm, mixed model with Nakagawa R² and LRTs, repeated-measures Bland–Altman); deviations (section 2 above).
4. **Results** — RQ1a table + figure; RQ1b against the mean-HR baseline; RQ2 per-factor figures and tests (lead with CIs and n); RQ3 variance table and family interactions; sensitivity table.
5. **Discussion** — what drives error, and what that implies (if motion dominates, capture guidance beats retraining; if skin tone matters after controlling for the rest, that's the fairness finding).
6. **Limitations** — Fitzpatrick 3–6 only, no types 1–2; Mini-MMPD downscaling; 1-minute videos (two windows each); deep models out of domain; one repaired frame per video; 1.76 bpm FFT resolution at 30 s.
7. **Reproducibility** — repo URL, commit, `python src/make_results.py`.

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| `No files in file list` (UBFC) | Every preprocessing worker failed — check `cv2.CascadeClassifier` exists (A3) and read the log above the error |
| "x of 42 videos cached" assertion | Delete `/content/cache/<name>` and rerun the cell |
| `np.mat` or PBV `solve` error | Toolbox not patched this session — rerun A5 |
| Session crashed, out of RAM | Restart, rerun Part A, rerun the cell; MMPD videos are streamed chunk by chunk |
| A `.mat` file fails to load | The runner logs it and continues; that video appears in the QC table with its error |
| RQ3 "model could not be fitted" | Check group sizes; report it rather than forcing a model |
| Drive quota exceeded | Delete processed batches from Drive; results are already in `results/windows/` |
