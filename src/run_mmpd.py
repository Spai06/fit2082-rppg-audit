"""Run every method on every MMPD video and write one row per 30 s window.

Resumable: one CSV per subject in results/windows/. Subjects already written are skipped, so a Colab
disconnect (or working through the dataset in batches) costs at most the subject in progress.

  python src/run_mmpd.py --data /content/data/mmpd --toolbox /content/rPPG-Toolbox \
      --out results --device cuda [--subjects 1 2] [--weights PURE|UBFC-rPPG] [--no-deep|--no-unsup]
"""
import argparse
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mmpd  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--toolbox", required=True)
    ap.add_argument("--out", default="results")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--subjects", type=int, nargs="*")
    ap.add_argument("--weights", default="PURE", help="checkpoint family: PURE (main) or UBFC-rPPG (sensitivity)")
    ap.add_argument("--no-deep", action="store_true")
    ap.add_argument("--no-unsup", action="store_true")
    args = ap.parse_args()

    mmpd.add_toolbox_to_path(args.toolbox)
    import torch
    torch.manual_seed(2082)
    np.random.seed(2082)
    if args.device.startswith("cuda") and not torch.cuda.is_available():
        print("No GPU found - using CPU (deep models will be slow).")
        args.device = "cpu"
    if args.no_unsup:
        mmpd.UNSUP_METHODS = []
    haar = os.path.join(args.toolbox, "dataset", "haarcascade_frontalface_default.xml")
    assert os.path.exists(haar), f"Haar cascade not found at {haar}"

    tag = "" if args.weights == "PURE" else f"_{args.weights}"
    wdir = os.path.join(args.out, f"windows{tag}")
    os.makedirs(wdir, exist_ok=True)

    deep = {}
    if not args.no_deep:
        for name, spec in mmpd.DEEP_SPECS.items():
            wfile = spec[3].replace("PURE_", f"{args.weights}_")
            deep[name] = mmpd.load_deep_model(name, os.path.join(args.toolbox, "final_model_release", wfile),
                                              args.device)
    with open(os.path.join(wdir, "_provenance.json"), "w") as f:
        json.dump({m: {"weights": mmpd.DEEP_SPECS[m][3].replace("PURE_", f"{args.weights}_"),
                       "trained_on": args.weights,
                       "used_on": "MMPD (no released checkpoint was trained on MMPD, so no leakage)"}
                   for m in deep}, f, indent=2)

    subjects = mmpd.find_subjects(args.data)
    if args.subjects:
        subjects = {k: v for k, v in subjects.items() if k in args.subjects}
    print(f"{len(subjects)} subject folders found: {list(subjects)}")

    for sid, folder in subjects.items():
        path = os.path.join(wdir, f"subject_{sid}.csv")
        if os.path.exists(path):
            print(f"subject {sid}: already done, skipping")
            continue
        mats = sorted(glob.glob(os.path.join(folder, "*.mat")))
        if not mats:
            print(f"subject {sid}: no .mat files, skipping")
            continue
        t0 = time.time()
        rows, qc = [], []
        for k, m in enumerate(mats, 1):
            try:
                r, q = mmpd.process_video(m, sid, deep, args.device, haar)
            except Exception as e:      # never lose a whole subject to one bad file
                print(f"  !! {os.path.basename(m)} failed: {e!r}")
                qc.append(dict(subject=sid, video=os.path.basename(m), error=repr(e)))
                continue
            rows += r
            qc.append(q)
            print(f"  [{k}/{len(mats)}] {os.path.basename(m)} {q['face_crop']} "
                  f"ref_hr {q['mean_ref_hr']:.1f}", flush=True)
        df = pd.DataFrame(rows)
        if len(df):
            df["abs_err"] = (df.pred_hr - df.ref_hr).abs()
        df.to_csv(path, index=False)
        pd.DataFrame(qc).to_csv(os.path.join(wdir, f"qc_subject_{sid}.csv"), index=False)
        print(f"subject {sid}: {len(df)} rows from {len(mats)} videos in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
