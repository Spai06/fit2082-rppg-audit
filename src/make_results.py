"""Regenerate every results table and figure from saved outputs. One command:

    python src/make_results.py                      (run from the repository root)

Inputs : results/ubfc/*.log              toolbox logs from the UBFC-rPPG runs (RQ1a)
         results/windows/subject_*.csv   per-window MMPD results (run_mmpd.py)
         configs/analysis.yaml
Outputs: results/tables/*.csv, results/figures/*.png, results/headline.md

Sensitivity runs:  --tag noexercise --drop-exercise | --tag rawerr --rq3-response abs_err
                   --windows windows_UBFC-rPPG --tag ubfcweights
"""
import glob
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stats_rq as S  # noqa: E402

# rPPG-Toolbox paper (Liu et al., NeurIPS 2023) Table 7, test set UBFC-rPPG, FFT, whole video.
# OMIT was added to the toolbox after the paper, so it has no published value.
PUBLISHED = pd.DataFrame([
    ("GREEN", 19.73, 31.00, 18.72, 0.37, -11.18), ("ICA", 16.00, 25.65, 15.35, 0.44, -9.91),
    ("CHROM", 4.06, 8.83, 3.84, 0.89, -2.96), ("LGI", 15.80, 28.55, 14.70, 0.36, -8.15),
    ("PBV", 15.90, 26.40, 15.17, 0.48, -9.16), ("POS", 4.08, 7.72, 3.93, 0.92, -2.39),
    ("TS-CAN", 1.30, 2.87, 1.50, 0.99, 1.49), ("PhysNet", 0.98, 2.48, 1.12, 0.99, 1.09),
    ("EfficientPhys", 2.07, 6.32, 2.10, 0.94, -0.12), ("DeepPhys", 1.21, 2.90, 1.42, 0.99, 1.74),
], columns=["method", "MAE", "RMSE", "MAPE", "Pearson", "SNR"])

# MMPD paper (Tang et al., EMBC 2023), Table II: MAE (bpm) of the classical methods on MMPD,
# broken down by skin tone, motion and lighting. Their protocol differs from ours (whole 1-minute
# videos, their own filter settings), so this is a check on the PATTERN, not a target to match.
_MMPD_PUB = {
    "POS":   dict(skin_tone={3: 5.76, 4: 9.06, 5: 12.78, 6: 11.17},
                  motion={"Stationary": 9.70, "Rotation": 7.50, "Talking": 8.05, "Walking": 17.05},
                  light={"LED-low": 9.76, "LED-high": 7.26, "Incandescent": 8.24, "Nature": 10.71}),
    "CHROM": dict(skin_tone={3: 6.57, 4: 10.57, 5: 14.65, 6: 12.53},
                  motion={"Stationary": 10.23, "Rotation": 9.28, "Talking": 9.31, "Walking": 17.61},
                  light={"LED-low": 10.49, "LED-high": 9.53, "Incandescent": 8.80, "Nature": 12.88}),
    "GREEN": dict(skin_tone={3: 12.37, 4: 23.39, 5: 15.22, 6: 20.59},
                  motion={"Stationary": 13.33, "Rotation": 16.67, "Talking": 17.16, "Walking": 29.81},
                  light={"LED-low": 17.12, "LED-high": 14.71, "Incandescent": 15.23, "Nature": 16.78}),
    "LGI":   dict(skin_tone={3: 5.99, 4: 14.43, 5: 14.23, 6: 17.02},
                  motion={"Stationary": 10.80, "Rotation": 9.38, "Talking": 11.36, "Walking": 25.48},
                  light={"LED-low": 11.59, "LED-high": 9.74, "Incandescent": 11.59}),
    "PBV":   dict(skin_tone={3: 7.94, 4: 15.87, 5: 14.62, 6: 17.24},
                  motion={"Stationary": 10.80, "Rotation": 11.18, "Talking": 13.44, "Walking": 25.66},
                  light={"LED-low": 11.91, "LED-high": 13.01}),
}
PUBLISHED_MMPD = pd.DataFrame(
    [dict(method=m, factor=f, level=k, MAE_published=v)
     for m, fs in _MMPD_PUB.items() for f, lv in fs.items() for k, v in lv.items()])


def compare_with_published(tables):
    """Our per-group MAE beside the MMPD paper's, plus the rank correlation of the two orderings."""
    ours = pd.concat([t.assign(factor=name) for name, t in tables.items()
                      if name in ("skin_tone_descriptive", "light", "motion")], ignore_index=True)
    ours["factor"] = ours.factor.replace({"skin_tone_descriptive": "skin_tone"})
    m = PUBLISHED_MMPD.merge(ours[["method", "factor", "level", "MAE_subject", "MAE_window", "n_subjects"]],
                             on=["method", "factor", "level"], how="inner")
    if len(m):
        m["MAE_diff"] = m.MAE_window - m.MAE_published
    return m

TOL_ABS, TOL_REL = 1.0, 0.15
DEEP_LOG_NAMES = {"TSCAN": "TS-CAN", "PHYSNET": "PhysNet", "EFFICIENTPHYS": "EfficientPhys",
                  "DEEPPHYS": "DeepPhys"}
METRIC_RE = re.compile(r"FFT (MAE|RMSE|MAPE|Pearson|SNR) \(FFT Label\): ([-\d.eE]+) \+/- ([-\d.eE]+)")


def parse_toolbox_log(path):
    rows, method = [], None
    base = os.path.basename(path).upper()
    deep = next((v for k, v in DEEP_LOG_NAMES.items() if k in base), None)
    for line in open(path, errors="ignore"):
        m = re.search(r"===Unsupervised Method \( (\w+) \) Predicting ===", line)
        if m:
            method = m.group(1)
        m = METRIC_RE.search(line)
        if m:
            rows.append(dict(method=method or deep, metric=m.group(1), value=float(m.group(2))))
    return rows


def rq1_table(root):
    logs = sorted(glob.glob(os.path.join(root, "results", "ubfc", "*.log")))
    rows = sum((parse_toolbox_log(p) for p in logs), [])
    if not rows:
        return None
    ours = pd.DataFrame(rows).pivot_table(index="method", columns="metric", values="value", aggfunc="last").reset_index()
    t = ours.merge(PUBLISHED, on="method", how="left", suffixes=("", "_published"))
    for k in ["MAE", "RMSE", "MAPE", "Pearson", "SNR"]:
        if k in t and f"{k}_published" in t:
            t[f"{k}_diff"] = t[k] - t[f"{k}_published"]
    tol = np.maximum(TOL_ABS, TOL_REL * t.MAE_published)
    t["within_tolerance"] = np.where(t.MAE_published.isna(), "no published value",
                                     np.where(t.MAE_diff.abs() <= tol, "yes", "NO - debug"))
    return t


def load_windows(root, cfg, windows_dir="windows", drop_exercise=False):
    files = glob.glob(os.path.join(root, "results", windows_dir, "subject_*.csv"))
    if not files:
        return None, None, None
    df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
    qcf = glob.glob(os.path.join(root, "results", windows_dir, "qc_subject_*.csv"))
    qc = pd.concat((pd.read_csv(f) for f in qcf), ignore_index=True) if qcf else pd.DataFrame()
    df, log = S.clean_windows(df, cfg["skin_groups"], drop_exercise)
    return S.add_baseline(df), qc, log


# ----------------------------------------------------------------------------- figures
def fig_rq1(t, out):
    t = t.dropna(subset=["MAE", "MAE_published"]).sort_values("MAE")
    x = np.arange(len(t))
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.bar(x - 0.2, t.MAE, 0.4, label="This work", color="#3b5b92")
    ax.bar(x + 0.2, t.MAE_published, 0.4, label="rPPG-Toolbox published", color="#a8b8d0")
    ax.set_xticks(x, t.method, rotation=30, ha="right")
    ax.set_ylabel("MAE (bpm)")
    ax.set_title("RQ1a: UBFC-rPPG, whole-video FFT, this work vs published")
    ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig)


def fig_groups(gt, title, out, order=None):
    methods = [m for m in gt.method.unique() if m != "Mean-HR baseline"] + ["Mean-HR baseline"]
    levels = [l for l in (order or sorted(gt.level.unique())) if l in set(gt.level)]
    fig, ax = plt.subplots(figsize=(max(9, len(methods) * 1.15), 4.2))
    w = 0.8 / len(levels)
    for j, lv in enumerate(levels):
        g = gt[gt.level == lv].set_index("method").reindex(methods)
        x = np.arange(len(methods)) + (j - (len(levels) - 1) / 2) * w
        n = int(g.n_subjects.max()) if g.n_subjects.notna().any() else 0
        ax.bar(x, g.MAE_subject, w, label=f"{lv} (n={n})")
        ax.errorbar(x, g.MAE_subject, yerr=[g.MAE_subject - g.CI_low, g.CI_high - g.MAE_subject],
                    fmt="none", ecolor="k", lw=1, capsize=2)
    ax.set_xticks(np.arange(len(methods)), methods, rotation=30, ha="right")
    ax.set_ylabel("Subject-level MAE (bpm), 95% cluster-bootstrap CI")
    ax.set_title(title)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig)


def fig_paired(df, factor, order, out):
    d = df[df.family != "baseline"]
    methods = list(d.method.unique())
    cols = min(len(methods), 5)
    rows = int(np.ceil(len(methods) / cols))
    fig, axs = plt.subplots(rows, cols, figsize=(3 * cols, 2.8 * rows), squeeze=False)
    for ax, m in zip(axs.ravel(), methods):
        w = d[d.method == m].groupby(["subject", factor]).abs_err.mean().unstack()
        o = [c for c in order if c in w]
        for _, r in w[o].iterrows():
            ax.plot(range(len(o)), r.values, color="0.75", lw=0.7)
        ax.plot(range(len(o)), w[o].mean().values, color="k", lw=2, marker="o")
        ax.set_xticks(range(len(o)), o, fontsize=7, rotation=20)
        ax.set_title(m, fontsize=9)
    for ax in axs.ravel()[len(methods):]:
        ax.axis("off")
    fig.supylabel("Subject MAE (bpm); grey = one subject (paired)")
    fig.suptitle(f"RQ2: error by {factor} (within subject)", fontsize=11)
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig)


def fig_rq3(r2, out):
    comps = [c for c in r2.columns if c.startswith("dR2_")]
    fig, ax = plt.subplots(figsize=(6, 4.2))
    bottom = np.zeros(len(r2))
    for c in comps:
        v = r2[c].clip(lower=0).values
        ax.bar(r2.family, v, bottom=bottom, label=c.replace("dR2_", ""))
        bottom += v
    ax.bar(r2.family, r2.subject_variance_share, bottom=bottom, label="subject (random intercept)", color="0.8")
    ax.set_ylabel("Share of variance in log(1+|error|)")
    ax.set_title("RQ3: variance attributed to each factor")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig)


def fig_ba(df, method, factor, out, order=None):
    d = df[df.method == method]
    levels = [l for l in (order or sorted(d[factor].dropna().unique())) if l in set(d[factor])]
    fig, axs = plt.subplots(1, len(levels), figsize=(3.6 * len(levels), 3.4), sharey=True, squeeze=False)
    for ax, lv in zip(axs[0], levels):
        g = d[d[factor] == lv]
        ba = S.bland_altman_repeated(g)
        ax.scatter((g.pred_hr + g.ref_hr) / 2, g.err, s=5, alpha=0.4)
        for y, ls in [(ba["bias"], "-"), (ba["loa_low"], "--"), (ba["loa_high"], "--")]:
            ax.axhline(y, color="k", ls=ls, lw=1)
        ax.set_title(f"{lv}: bias {ba['bias']:+.1f}, LoA [{ba['loa_low']:.0f}, {ba['loa_high']:.0f}]\n"
                     f"n={ba['n_subjects']} subjects, {ba['n_windows']} windows", fontsize=8)
        ax.set_xlabel("Mean of rPPG and PPG HR (bpm)")
    axs[0, 0].set_ylabel("rPPG - reference (bpm)")
    fig.suptitle(f"Bland-Altman (repeated-measures LoA): {method} by {factor}", fontsize=10)
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig)


# ----------------------------------------------------------------------------- main
def main(root=".", windows_dir="windows", tag="", drop_exercise=False, rq3_response="log_abs_err"):
    global TOL_ABS, TOL_REL
    cfg = yaml.safe_load(open(os.path.join(root, "configs", "analysis.yaml")))
    TOL_ABS, TOL_REL = cfg.get("rq1_tolerance_bpm", 1.0), cfg.get("rq1_tolerance_rel", 0.15)
    n_boot = cfg.get("n_boot", S.N_BOOT)
    sfx = f"_{tag}" if tag else ""
    tdir, fdir = os.path.join(root, "results", f"tables{sfx}"), os.path.join(root, "results", f"figures{sfx}")
    os.makedirs(tdir, exist_ok=True); os.makedirs(fdir, exist_ok=True)
    md = [f"# Headline results{(' - ' + tag) if tag else ''}\n",
          f"Settings: windows={windows_dir}, drop_post_exercise={drop_exercise}, RQ3 response={rq3_response}\n"]

    t1 = rq1_table(root) if not tag else None
    if t1 is not None:
        t1.to_csv(os.path.join(tdir, "rq1a_ubfc_vs_published.csv"), index=False)
        fig_rq1(t1, os.path.join(fdir, "rq1a_ubfc_vs_published.png"))
        cols = [c for c in ["method", "MAE", "MAE_published", "MAE_diff", "RMSE", "MAPE", "Pearson",
                            "Pearson_published", "SNR", "within_tolerance"] if c in t1]
        md += ["## RQ1a - UBFC-rPPG reproduction (whole video, FFT)\n",
               t1[cols].round(2).to_markdown(index=False), "\n"]

    df, qc, log = load_windows(root, cfg, windows_dir, drop_exercise)
    if df is None:
        print("No MMPD window files yet - only RQ1a produced.")
    else:
        md += [f"Windows: {log}\n"]
        t = S.metrics_table(df, n_boot)
        t.to_csv(os.path.join(tdir, "rq1b_mmpd_overall.csv"), index=False)
        md += ["## RQ1b - MMPD overall (30 s windows)\n",
               t[["family", "method", "n_subjects", "n_windows", "MAE", "MAE_CI_low", "MAE_CI_high",
                  "RMSE", "MAPE", "Pearson", "SNR_dB", "MAE_subject", "Pearson_subject"]].round(2).to_markdown(index=False), "\n"]

        sizes = df.drop_duplicates("subject").groupby(["skin_tone", "skin_group"]).size().rename("n_subjects")
        sizes.to_csv(os.path.join(tdir, "group_sizes.csv"))
        cells = df.drop_duplicates(["subject", "video"]).groupby(["light", "motion"]).size().rename("n_videos").unstack()
        cells.to_csv(os.path.join(tdir, "design_cells.csv"))
        md += ["## Group sizes (count before interpreting anything)\n", sizes.to_frame().to_markdown(), "\n",
               "Videos per lighting x motion cell:\n", cells.to_markdown(), "\n"]

        tables = {"skin_group": S.group_table(df, "skin_group", n_boot),
                  "skin_tone_descriptive": S.group_table(df, "skin_tone", n_boot),
                  "light": S.group_table(df, "light", n_boot),
                  "motion": S.group_table(df, "motion", n_boot)}
        for name, g in tables.items():
            g.to_csv(os.path.join(tdir, f"rq2_by_{name}.csv"), index=False)
        cmp = compare_with_published(tables)
        if len(cmp):
            cmp.to_csv(os.path.join(tdir, "rq2_vs_published_mmpd.csv"), index=False)
            rho = cmp.groupby("factor").apply(
                lambda g: pd.Series({"n_cells": len(g),
                                     "Spearman_rho": g.MAE_window.corr(g.MAE_published, method="spearman"),
                                     "our_mean": g.MAE_window.mean(), "published_mean": g.MAE_published.mean()}))
            md += ["## RQ1c - our per-group MAE vs the MMPD paper's Table II (classical methods)\n",
                   "Their protocol differs (whole 1-minute videos, their own filter settings), so compare the "
                   "pattern, not the absolute values.\n", rho.round(3).to_markdown(), "\n"]
        tests = S.rq2_tests(df[df.family != "baseline"])
        tests.to_csv(os.path.join(tdir, "rq2_tests.csv"), index=False)
        for f in S.PAIRED:
            S.paired_pairwise(df[df.family != "baseline"], f, n_boot).to_csv(
                os.path.join(tdir, f"rq2_{f}_pairwise.csv"), index=False)
        md += ["## RQ2 - tests (Holm-corrected across methods x factors)\n",
               tests.round(4).to_markdown(index=False), "\n"]

        fig_groups(tables["skin_group"], "RQ2: error by skin-tone group", os.path.join(fdir, "rq2_skin.png"))
        fig_groups(tables["skin_tone_descriptive"], "RQ2: error by Fitzpatrick type (descriptive)",
                   os.path.join(fdir, "rq2_skin_tone.png"))
        fig_groups(tables["light"], "RQ2: error by lighting", os.path.join(fdir, "rq2_light.png"), S.LIGHT_ORDER)
        fig_groups(tables["motion"], "RQ2: error by motion", os.path.join(fdir, "rq2_motion.png"), S.MOTION_ORDER)
        fig_paired(df, "light", S.LIGHT_ORDER, os.path.join(fdir, "rq2_light_paired.png"))
        fig_paired(df, "motion", S.MOTION_ORDER, os.path.join(fdir, "rq2_motion_paired.png"))

        try:
            r2, coef, inter = S.rq3_models(df, response=rq3_response)
            r2.to_csv(os.path.join(tdir, "rq3_variance.csv"), index=False)
            coef.to_csv(os.path.join(tdir, "rq3_coefficients.csv"), index=False)
            inter.to_csv(os.path.join(tdir, "rq3_family_interaction.csv"), index=False)
            fig_rq3(r2, os.path.join(fdir, "rq3_variance.png"))
            md += ["## RQ3 - mixed-effects variance attribution\n", r2.round(4).to_markdown(index=False), "\n",
                   "### Do supervised and unsupervised methods react the same way? (LRT)\n",
                   inter.round(4).to_markdown(index=False), "\n"]
        except Exception as e:   # small data can stop a model converging - say so, never hide it
            md += [f"## RQ3 - model could not be fitted: {e!r}\n"]

        for fam in ["unsupervised", "supervised"]:
            for m in t[t.family == fam].sort_values("MAE").method.head(1):
                fig_ba(df, m, "skin_group", os.path.join(fdir, f"ba_{m}_skin.png"))
                fig_ba(df, m, "motion", os.path.join(fdir, f"ba_{m}_motion.png"), S.MOTION_ORDER)
        if len(qc):
            qc.to_csv(os.path.join(tdir, "qc_videos.csv"), index=False)
            if "face_crop" in qc:
                md += ["## Face-crop outcome per video\n", qc.face_crop.value_counts().to_frame().to_markdown(), "\n"]

    with open(os.path.join(root, "results", f"headline{sfx}.md"), "w") as f:
        f.write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--windows", default="windows")
    ap.add_argument("--tag", default="")
    ap.add_argument("--drop-exercise", action="store_true")
    ap.add_argument("--rq3-response", default="log_abs_err", choices=["log_abs_err", "abs_err"])
    a = ap.parse_args()
    main(a.root, a.windows, a.tag, a.drop_exercise, a.rq3_response)
