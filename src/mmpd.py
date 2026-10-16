"""MMPD / Mini-MMPD: read one .mat video, run every method, return one row per 30 s window.

Signal handling reuses rPPG-Toolbox code (method functions, detrend, band-pass, FFT heart rate, SNR,
model classes, normalisation), so MMPD goes through the same path validated on UBFC-rPPG in RQ1.
Preprocessing mirrors MMPDLoader + BaseLoader (uint8 conversion, Haar face crop with a 1.5 box,
INTER_AREA resize to 72x72, PPG resampled to the frame count) without writing the toolbox's cache,
which would need ~150 GB for all of MMPD.
"""
import glob
import os
import re
import sys

import cv2
import numpy as np
import scipy.io as sio

FS = 30
WIN_S = 30
UNSUP_METHODS = ["GREEN", "CHROM", "POS", "OMIT", "LGI", "PBV"]
LIGHT = {1: "LED-low", 2: "LED-high", 3: "Incandescent", 4: "Nature"}
MOTION = {1: "Stationary", 2: "Rotation", 3: "Talking", 4: "Walking"}


def add_toolbox_to_path(toolbox_dir):
    if toolbox_dir not in sys.path:
        sys.path.insert(0, toolbox_dir)


# ----------------------------------------------------------------------------- files and labels
def find_subjects(root):
    """{subject number: folder} for every subjectN folder under root (any depth)."""
    out = {}
    for d in glob.glob(os.path.join(root, "**", "subject*"), recursive=True):
        m = re.fullmatch(r"subject(\d+)", os.path.basename(d))
        if m and os.path.isdir(d):
            out[int(m.group(1))] = d
    return dict(sorted(out.items()))


def _scalar(x):
    a = np.asarray(x).ravel()
    v = a[0] if a.size else ""
    return v.strip() if isinstance(v, str) else v


def read_mat(path):
    """Returns (frames uint8 (T,H,W,3), ppg (T,), labels dict). Label codes follow MMPDLoader."""
    mat = sio.loadmat(path)
    frames = np.asarray(mat["video"])
    if frames.dtype != np.uint8:                       # MMPD stores float in [0, 1]
        frames = np.round(frames * 255).astype(np.uint8)
    ppg = np.asarray(mat["GT_ppg"]).T.reshape(-1)
    # MMPD videos end with a black frame and a zero PPG sample. Trimming them would drop a whole
    # 30 s window (1800 frames = exactly two windows), so the trailing bad samples are replaced by
    # the last good ones instead. The count is logged per video in the QC table.
    bright = frames.reshape(frames.shape[0], -1).mean(1)
    last = frames.shape[0] - 1
    while last > 0 and bright[last] < 0.02 * 255:
        last -= 1
    n_repaired = frames.shape[0] - 1 - last
    if n_repaired:
        frames[last + 1:] = frames[last]
        good_ppg = last if last < len(ppg) else len(ppg) - 1
        ppg[good_ppg + 1:] = ppg[good_ppg]
    def _map(value, table, field):
        if value not in table:
            raise ValueError(f"{os.path.basename(path)}: unexpected {field} label {value!r}. "
                             f"Known values: {sorted(table)}. Add it to mmpd.py and say so in the report.")
        return table[value]

    light = _map(_scalar(mat["light"]), {"LED-low": 1, "LED-high": 2, "Incandescent": 3, "Nature": 4}, "light")
    mo = _scalar(mat["motion"])
    # 'Watching Videos' is a known bad label for Walking in older MMPD releases (as in MMPDLoader)
    motion = _map(mo, {"Stationary": 1, "Stationary (after exercise)": 1, "Rotation": 2, "Talking": 3,
                       "Walking": 4, "Watching Videos": 4}, "motion")
    lab = dict(
        light=light, motion=motion, motion_raw=mo,
        exercise=1 if _scalar(mat["exercise"]) == "True" else 2,
        skin_tone=int(np.asarray(mat["skin_color"]).ravel()[0]),
        gender=1 if _scalar(mat["gender"]) == "male" else 2,
        glasser=1 if _scalar(mat["glasser"]) == "True" else 2,
        hair_cover=1 if _scalar(mat["hair_cover"]) == "True" else 2,
        makeup=1 if _scalar(mat["makeup"]) == "True" else 2,
    )
    lab["frames_repaired"] = int(n_repaired)
    assert lab["skin_tone"] in (3, 4, 5, 6), f"Unexpected skin tone {lab['skin_tone']} in {path}"
    return frames, ppg, lab


# ----------------------------------------------------------------------------- preprocessing
def face_box(frame, haar_path, upscale=4, coef=1.5):
    """Haar face box as BaseLoader does (largest face, 1.5x box). Mini-MMPD frames are 80x60, too
    small for the detector, so detection runs on an upscaled copy and the box is scaled back.
    Returns (box, how) where how is 'upscaled' / 'native' / 'whole-frame' (logged per video)."""
    det = cv2.CascadeClassifier(haar_path)
    for scale, how in ((1, "native"), (upscale, "upscaled")):
        img = cv2.resize(frame, (frame.shape[1] * scale, frame.shape[0] * scale),
                         interpolation=cv2.INTER_CUBIC) if scale != 1 else frame
        zones = det.detectMultiScale(img[:, :, :3].astype(np.uint8))
        if len(zones):
            x, y, w, h = (v / scale for v in zones[np.argmax(zones[:, 2])])
            # BaseLoader.face_detection enlarges the box and stores it in an int array, which
            # truncates. Reproduced exactly here, or the crop lands one pixel off the toolbox's.
            return [int(max(0, x - (coef - 1.0) / 2 * w)), int(max(0, y - (coef - 1.0) / 2 * h)),
                    int(coef * w), int(coef * h)], how
    return [0, 0, frame.shape[1], frame.shape[0]], "whole-frame"


def crop_resize(frames, box, size=72):
    """Static box from the first frame (toolbox default), then INTER_AREA resize."""
    x, y, w, h = box
    out = np.empty((frames.shape[0], size, size, 3), dtype=np.uint8)
    for i, f in enumerate(frames):
        c = f[max(y, 0):min(y + h, f.shape[0]), max(x, 0):min(x + w, f.shape[1])]
        if c.size == 0:
            c = f
        out[i] = cv2.resize(c, (size, size), interpolation=cv2.INTER_AREA)
    return out


def resample_ppg(ppg, n):
    return np.interp(np.linspace(1, ppg.shape[0], n), np.linspace(1, ppg.shape[0], ppg.shape[0]), ppg)


# ----------------------------------------------------------------------------- heart rate
def hr_and_snr(sig, ref_hr=np.nan, fs=FS, diff_flag=False):
    """The prediction branch of the toolbox's calculate_metric_per_video: detrend (lambda=100),
    1st-order Butterworth 0.75-2.5 Hz (after patching), periodogram FFT peak; SNR at ref_hr."""
    from scipy.signal import butter, filtfilt
    from evaluation import post_process as pp
    x = np.asarray(sig, dtype=float)
    x = pp._detrend(np.cumsum(x), 100) if diff_flag else pp._detrend(x, 100)
    b, a = butter(1, [0.75 / fs * 2, 2.5 / fs * 2], btype="bandpass")
    x = filtfilt(b, a, np.double(x))
    hr = float(pp._calculate_fft_hr(x, fs=fs))
    snr = float(pp._calculate_SNR(x, ref_hr, fs=fs)) if np.isfinite(ref_hr) else np.nan
    return hr, snr


def run_unsupervised(frames72, method):
    from unsupervised_methods.methods.GREEN import GREEN
    from unsupervised_methods.methods.CHROME_DEHAAN import CHROME_DEHAAN
    from unsupervised_methods.methods.POS_WANG import POS_WANG
    from unsupervised_methods.methods.OMIT import OMIT
    from unsupervised_methods.methods.LGI import LGI
    from unsupervised_methods.methods.PBV import PBV
    x = frames72.astype(np.float64)
    return {"GREEN": lambda: GREEN(x), "CHROM": lambda: CHROME_DEHAAN(x, FS), "POS": lambda: POS_WANG(x, FS),
            "OMIT": lambda: OMIT(x), "LGI": lambda: LGI(x), "PBV": lambda: PBV(x)}[method]()


# ----------------------------------------------------------------------------- deep models
DEEP_SPECS = {   # name: (kind, input types, chunk length, weights file)
    "TS-CAN": ("Tscan", ["DiffNormalized", "Standardized"], 180, "PURE_TSCAN.pth"),
    "PhysNet": ("Physnet", ["DiffNormalized"], 128, "PURE_PhysNet_DiffNormalized.pth"),
    "EfficientPhys": ("EfficientPhys", ["Standardized"], 180, "PURE_EfficientPhys.pth"),
    "DeepPhys": ("DeepPhys", ["DiffNormalized", "Standardized"], 180, "PURE_DeepPhys.pth"),
}


def load_deep_model(name, weights_path, device):
    import torch
    kind = DEEP_SPECS[name][0]
    if kind == "Tscan":
        from neural_methods.model.TS_CAN import TSCAN
        model = TSCAN(frame_depth=10, img_size=72)
    elif kind == "EfficientPhys":
        from neural_methods.model.EfficientPhys import EfficientPhys
        model = EfficientPhys(frame_depth=10, img_size=72)
    elif kind == "DeepPhys":
        from neural_methods.model.DeepPhys import DeepPhys
        model = DeepPhys(img_size=72)
    else:
        from neural_methods.model.PhysNet import PhysNet_padding_Encoder_Decoder_MAX
        model = PhysNet_padding_Encoder_Decoder_MAX(frames=128)
    if device.startswith("cuda") and kind != "Physnet":   # the toolbox wraps these in DataParallel
        model = torch.nn.DataParallel(model)
    sd = torch.load(weights_path, map_location=device)
    has_mod = any(k.startswith("module.") for k in sd)
    want_mod = isinstance(model, torch.nn.DataParallel)
    if has_mod and not want_mod:
        sd = {k[len("module."):]: v for k, v in sd.items()}
    elif want_mod and not has_mod:
        sd = {"module." + k: v for k, v in sd.items()}
    model.load_state_dict(sd)
    return model.to(device).eval()


def _norm_stats(f):
    n = f.size
    s1 = s2 = 0.0
    for i in range(0, f.shape[0], 500):
        c = f[i:i + 500].astype(np.float64)
        s1 += c.sum(); s2 += (c * c).sum()
    mean = s1 / n
    std = np.sqrt(max(s2 / n - mean * mean, 0.0))
    d1 = d2 = 0.0
    dn = 0
    for i in range(0, f.shape[0] - 1, 500):
        a = f[i:i + 501].astype(np.float64)
        d = ((a[1:] - a[:-1]) / (a[1:] + a[:-1] + 1e-7)).astype(np.float32).astype(np.float64)
        d1 += d.sum(); d2 += (d * d).sum(); dn += d.size
    dmean = d1 / dn
    return mean, std, np.sqrt(max(d2 / dn - dmean * dmean, 0.0))


def _chunk(f, start, L, types, stats):
    mean, std, dstd = stats
    T = f.shape[0]
    a = f[start:start + L].astype(np.float64)
    parts = []
    for t in types:
        if t == "DiffNormalized":
            nxt = f[start + 1:min(start + L + 1, T)].astype(np.float64)
            d = np.zeros_like(a, dtype=np.float32)
            m = nxt.shape[0]
            d[:m] = ((nxt - a[:m]) / (nxt + a[:m] + 1e-7)).astype(np.float32)
            d = d / np.float32(dstd)
            d[np.isnan(d)] = 0
            parts.append(d)
        else:
            s = ((a - mean) / std).astype(np.float32)
            s[np.isnan(s)] = 0
            parts.append(s)
    return np.concatenate(parts, axis=-1)


def run_deep(frames72, name, model, device, batch_size=4):
    """Replicates the toolbox trainers' test loop (checked against toolbox output to ~1e-5)."""
    import torch
    kind, types, L, _ = DEEP_SPECS[name]
    stats = _norm_stats(frames72)
    n_chunks = frames72.shape[0] // L
    T = frames72.shape[0]
    starts = [i * L for i in range(n_chunks)]
    tail = T - n_chunks * L
    if tail > 0 and T >= L:
        # The toolbox drops the frames that don't fill a chunk. With 1800-frame MMPD videos that
        # would cost PhysNet (chunk 128) its second 30 s window, and every method must be scored on
        # the same windows, so one extra chunk ending at the last frame covers the tail. Only its
        # final 'tail' samples are kept, so nothing is counted twice.
        starts.append(T - L)

    def infer(batch):
        x = torch.from_numpy(np.stack(batch)).to(device)
        if kind == "Physnet":
            out, _, _, _ = model(x.permute(0, 4, 1, 2, 3).contiguous())
            return out.reshape(len(batch), -1).cpu().numpy()
        N, D, H, W, C = x.shape
        x = x.permute(0, 1, 4, 2, 3).contiguous().reshape(N * D, C, H, W)
        if kind in ("Tscan", "EfficientPhys"):        # these trim to a multiple of the frame depth
            x = x[: (N * D) // 10 * 10]
        if kind == "EfficientPhys":                   # ...and need one extra frame for its internal diff
            x = torch.cat([x, x[-1:]], 0)
        return model(x).reshape(N, -1).cpu().numpy()

    out_chunks = []
    with torch.no_grad():
        for b0 in range(0, len(starts), batch_size):
            group = starts[b0:b0 + batch_size]
            res = infer([_chunk(frames72, s, L, types, stats) for s in group])
            out_chunks.extend(res[i] for i in range(len(group)))
    if not out_chunks:
        return np.zeros(0)
    if tail > 0 and T >= L:
        return np.concatenate(out_chunks[:-1] + [out_chunks[-1][-tail:]])
    return np.concatenate(out_chunks)


# ----------------------------------------------------------------------------- one video
def process_video(path, subject, deep_models, device, haar_path, win_s=WIN_S):
    frames, ppg, lab = read_mat(path)
    box, how = face_box(frames[0], haar_path)
    f72 = crop_resize(frames, box)
    ppg = resample_ppg(ppg, f72.shape[0])
    L = win_s * FS
    n_win = f72.shape[0] // L
    ref = []
    for w in range(n_win):
        ref.append(hr_and_snr(ppg[w * L:(w + 1) * L])[0])

    base = dict(subject=subject, video=os.path.splitext(os.path.basename(path))[0],
                light=LIGHT[lab["light"]], motion=MOTION[lab["motion"]], **{k: v for k, v in lab.items()
                if k in ("exercise", "skin_tone", "gender", "glasser", "hair_cover", "makeup")})
    rows = []

    def add(sig, method, family, diff_flag):
        for w in range(min(n_win, len(sig) // L)):
            hr, snr = hr_and_snr(sig[w * L:(w + 1) * L], ref[w], diff_flag=diff_flag)
            rows.append(dict(base, method=method, family=family, window=w, pred_hr=hr,
                             ref_hr=ref[w], snr_db=snr))

    for m in UNSUP_METHODS:
        add(np.asarray(run_unsupervised(f72, m)).ravel(), m, "unsupervised", False)
    for m, model in deep_models.items():
        add(run_deep(f72, m, model, device), m, "supervised", True)

    qc = dict(base, n_frames=f72.shape[0], face_crop=how, box=str(box),
              frames_repaired=lab["frames_repaired"],
              ppg_len=len(ppg), mean_ref_hr=float(np.nanmean(ref)) if ref else np.nan)
    return rows, qc


# ----------------------------------------------------------------------------- timing check
def alignment_check(path, haar_path, method="POS", max_lag_s=5):
    """Proposal W5: check that video and reference line up before generating results.

    Cross-correlates the recovered pulse (band-passed) with the band-passed reference PPG over
    +/- max_lag_s. MMPD stores one PPG sample per video frame, so a correct file peaks at lag ~0
    (a small positive lag is physiological: the pulse reaches the face after the finger sensor...
    in MMPD both come from the face video clock, so expect ~0). |r| stays low when the method
    cannot recover the pulse at all, so read the lag only when r is high enough.
    """
    from scipy.signal import butter, filtfilt
    frames, ppg, lab = read_mat(path)
    box, how = face_box(frames[0], haar_path)
    f72 = crop_resize(frames, box)
    b, a = butter(2, [0.75 / FS * 2, 2.5 / FS * 2], btype="bandpass")
    x = filtfilt(b, a, np.asarray(run_unsupervised(f72, method), dtype=float).ravel())
    y = filtfilt(b, a, np.asarray(ppg, dtype=float).ravel())
    n = min(len(x), len(y))
    x, y = x[:n], y[:n]
    best = (np.nan, -np.inf)
    for lag in range(-max_lag_s * FS, max_lag_s * FS + 1):
        xa, ya = (x[lag:], y[:n - lag]) if lag >= 0 else (x[:lag], y[-lag:])
        if len(xa) > FS * 10:
            r = float(np.corrcoef(xa, ya)[0, 1])
            if r > best[1]:
                best = (lag / FS, r)
    return dict(file=os.path.basename(path), light=LIGHT[lab["light"]], motion=MOTION[lab["motion"]],
                face_crop=how, lag_s=best[0], r=best[1])
