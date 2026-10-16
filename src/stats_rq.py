"""Statistics for RQ1-RQ3 on MMPD.

Every estimate carries its subject count. Every CI is a subject-level (cluster) bootstrap, because
windows from one person are not independent. Skin tone is fixed within a subject (between-subject
comparison); lighting and motion vary within a subject (paired comparisons).
"""
import numpy as np
import pandas as pd
from scipy import stats

SEEDS = (2082, 2083, 2084)      # bootstraps repeated with 3 seeds; the SD across seeds is reported
N_BOOT = 5000
KEY = ["subject", "video", "window"]
BETWEEN = ["skin_group"]
PAIRED = ["light", "motion"]
LIGHT_ORDER = ["LED-low", "LED-high", "Incandescent", "Nature"]
MOTION_ORDER = ["Stationary", "Rotation", "Talking", "Walking"]


# ----------------------------------------------------------------------------- cleaning
def clean_windows(df, skin_groups=None, drop_exercise=False):
    """Keep windows that exist for every method, attach the skin-tone group, add error columns."""
    log = {"windows_in": int(len(df))}
    df = df[np.isfinite(df.ref_hr) & np.isfinite(df.pred_hr)].copy()
    if drop_exercise:
        df = df[df.exercise == 2]
        log["after_dropping_post_exercise"] = int(len(df))
    n_methods = df.method.nunique()
    complete = df.groupby(KEY).method.nunique()
    df = df.set_index(KEY).loc[complete[complete == n_methods].index].reset_index()
    log["after_common_windows"] = int(len(df))
    if skin_groups:
        g = {int(v): k for k, vs in skin_groups.items() for v in vs}
        df["skin_group"] = df.skin_tone.map(g)
    df["err"] = df.pred_hr - df.ref_hr
    df["abs_err"] = df.err.abs()
    df["ape"] = df.abs_err / df.ref_hr * 100
    log["subjects"] = int(df.subject.nunique())
    log["videos"] = int(df.groupby(["subject", "video"]).ngroups)
    return df, log


def add_baseline(df):
    """'Knows nothing' predictor: the mean reference HR of all OTHER subjects."""
    cols = [c for c in df.columns if c not in ("method", "family", "pred_hr", "snr_db", "err", "abs_err", "ape")]
    one = df.drop_duplicates(KEY)[cols].copy()
    m = one.groupby("subject").ref_hr.mean()
    one["pred_hr"] = one.subject.map({s: m.drop(s).mean() for s in m.index})
    one["method"], one["family"], one["snr_db"] = "Mean-HR baseline", "baseline", np.nan
    one["err"] = one.pred_hr - one.ref_hr
    one["abs_err"] = one.err.abs()
    one["ape"] = one.abs_err / one.ref_hr * 100
    return pd.concat([df, one], ignore_index=True)


# ----------------------------------------------------------------------------- metrics
def point_metrics(d):
    subj = d.groupby("subject").agg(mae=("abs_err", "mean"), pred=("pred_hr", "mean"), ref=("ref_hr", "mean"))
    return dict(n_subjects=d.subject.nunique(), n_windows=len(d),
                MAE=d.abs_err.mean(), RMSE=np.sqrt((d.err ** 2).mean()), MAPE=d.ape.mean(),
                Pearson=d[["pred_hr", "ref_hr"]].corr().iloc[0, 1] if d.pred_hr.std() > 0 else np.nan,
                SNR_dB=d.snr_db.mean(),
                MAE_subject=subj.mae.mean(),
                Pearson_subject=subj[["pred", "ref"]].corr().iloc[0, 1] if len(subj) > 2 and subj.pred.std() > 0 else np.nan)


def cluster_boot(d, kind="window", n_boot=N_BOOT, seed=SEEDS[0]):
    """Resample SUBJECTS with replacement. kind='window': pooled MAE; 'subject': mean of subject MAEs."""
    g = d.groupby("subject").abs_err
    s, n, m = g.sum().values, g.size().values, g.mean().values
    idx = np.random.default_rng(seed).integers(0, len(s), size=(n_boot, len(s)))
    v = s[idx].sum(1) / n[idx].sum(1) if kind == "window" else m[idx].mean(1)
    return np.percentile(v, [2.5, 97.5])


def boot_ci_3seeds(d, kind="window", n_boot=N_BOOT):
    cis = np.array([cluster_boot(d, kind, n_boot, sd) for sd in SEEDS])
    return cis.mean(0), cis.std(0)


def subject_mae(d):
    return d.groupby("subject").abs_err.mean().mean()


def metrics_table(df, n_boot=N_BOOT):
    rows = []
    for (fam, m), d in df.groupby(["family", "method"]):
        r = dict(family=fam, method=m, **point_metrics(d))
        (lo, hi), (a, b) = boot_ci_3seeds(d, "window", n_boot)
        r.update(MAE_CI_low=lo, MAE_CI_high=hi, MAE_CI_seed_sd=max(a, b))
        (lo, hi), _ = boot_ci_3seeds(d, "subject", n_boot)
        r.update(MAE_subject_CI_low=lo, MAE_subject_CI_high=hi)
        rows.append(r)
    return pd.DataFrame(rows).sort_values(["family", "MAE"])


# ----------------------------------------------------------------------------- RQ2
def holm(p):
    p = np.asarray(p, float)
    out = np.full_like(p, np.nan)
    ok = np.isfinite(p)
    order = np.argsort(p[ok])
    m = int(ok.sum())
    adj = np.maximum.accumulate((m - np.arange(m)) * p[ok][order])
    tmp = np.empty(m)
    tmp[order] = np.minimum(adj, 1)
    out[ok] = tmp
    return out


def group_table(df, factor, n_boot=N_BOOT):
    """Per method x level: subject-level MAE, cluster-bootstrap CI, and the n behind it."""
    rows = []
    for (m, lvl), d in df.groupby(["method", factor]):
        (lo, hi), _ = boot_ci_3seeds(d, "subject", n_boot)
        rows.append(dict(method=m, factor=factor, level=lvl, n_subjects=d.subject.nunique(),
                         n_windows=len(d), MAE_subject=subject_mae(d), CI_low=lo, CI_high=hi,
                         MAE_window=d.abs_err.mean()))
    t = pd.DataFrame(rows)
    t["CI_width"] = t.CI_high - t.CI_low
    return t


def rq2_tests(df, between=BETWEEN, paired=PAIRED):
    rows = []
    for m, d in df.groupby("method"):
        for f in between:                      # skin tone: one value per subject
            s = d.groupby(["subject", f]).abs_err.mean().reset_index()
            lv = sorted(s[f].dropna().unique())
            groups = [s.loc[s[f] == l, "abs_err"] for l in lv]
            if len(lv) == 2 and all(len(g) > 0 for g in groups):
                t = stats.mannwhitneyu(*groups, alternative="two-sided")
                eff = f"{lv[1]} minus {lv[0]}: {groups[1].mean() - groups[0].mean():+.2f} bpm"
                name = "Mann-Whitney U (subject MAE)"
            elif len(lv) > 2:
                t = stats.kruskal(*groups)
                eff = " / ".join(f"{l}={g.mean():.2f}" for l, g in zip(lv, groups))
                name = "Kruskal-Wallis (subject MAE)"
            else:
                continue
            rows.append(dict(method=m, factor=f, test=name, stat=t.statistic, p=t.pvalue,
                             n=" vs ".join(str(len(g)) for g in groups), effect=eff))
        for f in paired:                       # lighting, motion: vary within a subject
            w = d.groupby(["subject", f]).abs_err.mean().unstack().dropna()
            if w.shape[1] >= 3 and len(w) > 2:
                t = stats.friedmanchisquare(*[w[c] for c in w.columns])
                rows.append(dict(method=m, factor=f, test=f"Friedman (paired, subject x {f})",
                                 stat=t.statistic, p=t.pvalue, n=str(len(w)),
                                 effect=" / ".join(f"{c}={w[c].mean():.2f}" for c in w.columns)))
    t = pd.DataFrame(rows)
    if len(t):
        t["p_holm"] = holm(t.p.values)         # corrected across all methods x factors
    return t


def paired_pairwise(df, factor, n_boot=N_BOOT, seed=SEEDS[0]):
    rng = np.random.default_rng(seed)
    rows = []
    for m, d in df.groupby("method"):
        w = d.groupby(["subject", factor]).abs_err.mean().unstack().dropna()
        cols = list(w.columns)
        for i, a in enumerate(cols):
            for b in cols[i + 1:]:
                diff = (w[a] - w[b]).values
                p = stats.wilcoxon(w[a], w[b]).pvalue if np.any(diff != 0) else 1.0
                bs = [rng.choice(diff, len(diff)).mean() for _ in range(n_boot)]
                rows.append(dict(method=m, factor=factor, pair=f"{a} - {b}", mean_diff=diff.mean(),
                                 CI_low=np.percentile(bs, 2.5), CI_high=np.percentile(bs, 97.5),
                                 n_subjects=len(diff), p=p))
    t = pd.DataFrame(rows)
    if len(t):
        t["p_holm"] = t.groupby("method").p.transform(lambda s: holm(s.values))
    return t


# ----------------------------------------------------------------------------- RQ3
def _nakagawa(res):
    v_f = float(np.var(np.asarray(res.model.exog) @ np.asarray(res.fe_params)))
    v_r = float(np.asarray(res.cov_re)[0, 0])
    v_e = float(res.scale)
    tot = v_f + v_r + v_e
    return v_f / tot, (v_f + v_r) / tot, v_r / tot


def _fit(formula, data):
    """ML fit tried with several optimisers; keep the best FINITE log-likelihood.
    (statsmodels' lbfgs can report 'converged' with llf = inf and a zero random-effect variance.)"""
    import warnings
    import statsmodels.formula.api as smf
    best = None
    for method in ("powell", "nm", "bfgs", "lbfgs"):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                r = smf.mixedlm(formula, data, groups=data["subject"]).fit(reml=False, method=method, maxiter=5000)
        except Exception:
            continue
        if np.isfinite(r.llf) and (best is None or r.llf > best.llf + 1e-6):
            best = r
    if best is None:
        raise RuntimeError(f"Mixed model failed with every optimiser: {formula}")
    return best


def _design(df):
    d = df[df.family != "baseline"].dropna(subset=["skin_group"]).copy()
    d["log_abs_err"] = np.log1p(d.abs_err)
    terms = {}
    lv = sorted(d.skin_group.unique())
    if len(lv) == 2:
        d["skin_dark"] = (d.skin_group == lv[1]).astype(float)
        terms["skin tone"] = ["skin_dark"]
    else:
        terms["skin tone"] = []
        for l in lv[1:]:
            c = f"skin_{l}".replace("-", "_")
            d[c] = (d.skin_group == l).astype(float)
            terms["skin tone"].append(c)
    for f, ref, order in (("light", "LED-low", LIGHT_ORDER), ("motion", "Stationary", MOTION_ORDER)):
        terms[f] = []
        for l in [x for x in order if x in set(d[f]) and x != ref]:
            c = f"{f}_{l}".replace("-", "_")
            d[c] = (d[f] == l).astype(float)
            terms[f].append(c)
    d["post_exercise"] = (d.exercise == 1).astype(float)
    terms["exercise"] = ["post_exercise"] if d.post_exercise.nunique() > 1 else []
    d["is_sup"] = (d.family == "supervised").astype(float)
    return d, {k: v for k, v in terms.items() if v}


def rq3_models(df, response="log_abs_err"):
    """Per family: y ~ skin + lighting + motion + post-exercise (+ method), random intercept per subject.
    y = log(1 + |error|) because absolute errors are strongly right-skewed.
    A factor's share = drop in marginal R^2 (Nakagawa) when it is removed; LRT gives the p-value.
    NOTE: skin tone is constant within a subject, so the subject random intercept competes with it,
    while lighting and motion vary within a subject. The factors are NOT on equal footing."""
    d, terms = _design(df)
    r2_rows, coef_rows = [], []
    for fam, g in d.groupby("family"):
        extra = ["C(method)"] if g.method.nunique() > 1 else []
        all_terms = sum(terms.values(), []) + extra
        full = _fit(f"{response} ~ " + " + ".join(all_terms), g)
        r2m, r2c, subj = _nakagawa(full)
        row = dict(family=fam, n_subjects=g.subject.nunique(), n_windows=len(g),
                   R2_marginal=r2m, R2_conditional=r2c, subject_variance_share=subj)
        for name, cols in terms.items():
            if not cols:
                continue
            keep = [t for t in all_terms if t not in cols]
            red = _fit(f"{response} ~ " + (" + ".join(keep) if keep else "1"), g)
            row[f"dR2_{name}"] = r2m - _nakagawa(red)[0]
            row[f"LRT_p_{name}"] = stats.chi2.sf(2 * (full.llf - red.llf), len(cols))
        r2_rows.append(row)
        ci = full.conf_int()
        for p in full.fe_params.index:
            coef_rows.append(dict(family=fam, term=p, coef=full.fe_params[p], CI_low=ci.loc[p, 0],
                                  CI_high=ci.loc[p, 1], p=full.pvalues[p]))
    inter = []
    if d.family.nunique() == 2:
        main = sum(terms.values(), []) + ["C(method)"]
        m0 = _fit(f"{response} ~ " + " + ".join(main), d)
        for name, cols in terms.items():
            if not cols:
                continue
            for c in cols:
                d[f"{c}_x_sup"] = d[c] * d.is_sup
            m1 = _fit(f"{response} ~ " + " + ".join(main + [f"{c}_x_sup" for c in cols]), d)
            inter.append(dict(factor=name, interaction=f"{name} x family", df=len(cols),
                              LR=2 * (m1.llf - m0.llf), p=stats.chi2.sf(2 * (m1.llf - m0.llf), len(cols))))
    return pd.DataFrame(r2_rows), pd.DataFrame(coef_rows), pd.DataFrame(inter)


# ----------------------------------------------------------------------------- Bland-Altman
def bland_altman_repeated(d):
    """Bias and 95% limits of agreement with repeated measures per subject
    (Bland & Altman 2007, true value varies): total SD = sqrt(between + within)."""
    g = d.groupby("subject").err
    n, k = len(d), g.ngroups
    mi, di = g.size().values, g.mean().values
    bias = d.err.mean()
    ms_w = ((d.err - g.transform("mean")) ** 2).sum() / max(n - k, 1)
    ms_b = (mi * (di - bias) ** 2).sum() / max(k - 1, 1)
    div = (n ** 2 - (mi ** 2).sum()) / ((k - 1) * n) if k > 1 else 1
    sd = np.sqrt(max((ms_b - ms_w) / div, 0) + ms_w)
    return dict(bias=bias, sd=sd, loa_low=bias - 1.96 * sd, loa_high=bias + 1.96 * sd,
                n_subjects=k, n_windows=n)
