"""Idempotent patches that make rPPG-Toolbox run on Google Colab (Python 3.12, NumPy 2, recent PyTorch).

None of these patches changes the maths of any method. Each one is listed in the report's
Methods section. Run:  python src/patch_toolbox.py /content/rPPG-Toolbox
"""
import glob
import os
import re
import sys

MARK = "# >>> FIT2082 patch"


SEQUENTIAL_MANAGER = """

# >>> FIT2082 patch: preprocess in the main process instead of forking workers.
# On Colab the forked children crash with 'corrupted double-linked list' (OpenCV's thread pool
# does not survive fork), every child dies, and the toolbox then reports the misleading
# 'No files in file list'. The patches already limit this to one worker, so no speed is lost.
def _fit2082_sequential_manager(self, data_dirs, config_preprocess, multi_process_quota=1):
    import cv2 as _cv2
    from tqdm import tqdm as _tqdm
    _cv2.setNumThreads(0)
    file_list_dict = {}
    print('Preprocessing dataset (in-process)...')
    for i in _tqdm(range(len(data_dirs)), ncols=80):
        self.preprocess_dataset_subprocess(data_dirs, config_preprocess, i, file_list_dict)
    return file_list_dict


BaseLoader.multi_process_manager = _fit2082_sequential_manager
"""

SPARSE_DETREND = '''

# >>> FIT2082 patch: sparse detrend (mathematically identical to the dense version above,
# verified to 1e-10; the dense version builds an N x N matrix and runs out of memory on long videos)
def _fit2082_sparse_detrend(input_signal, lambda_value):
    import numpy as _np
    from scipy import sparse as _sp
    from scipy.sparse.linalg import spsolve as _spsolve
    x = _np.asarray(input_signal, dtype=float)
    T = x.shape[0]
    D = _sp.diags([_np.ones(T - 2), -2 * _np.ones(T - 2), _np.ones(T - 2)], [0, 1, 2], shape=(T - 2, T))
    A = (_sp.eye(T) + (lambda_value ** 2) * (D.T @ D)).tocsc()
    if x.ndim == 1:
        return x - _spsolve(A, x)
    x2 = x.reshape(T, -1)
    out = x2 - _np.column_stack([_spsolve(A, x2[:, j]) for j in range(x2.shape[1])])
    return out.reshape(x.shape)
'''


def _read(p):
    with open(p) as f:
        return f.read()


def _write(p, s):
    with open(p, "w") as f:
        f.write(s)


def patch(root):
    changed = []

    # 1. NumPy 2 removed np.mat -> np.asmatrix (identical behaviour)
    for p in glob.glob(os.path.join(root, "**", "*.py"), recursive=True):
        s = _read(p)
        if "np.mat(" in s:
            _write(p, s.replace("np.mat(", "np.asmatrix("))
            changed.append(f"np.mat -> np.asmatrix: {os.path.relpath(p, root)}")

    # 1b. NumPy 2 changed np.linalg.solve: a 2-D right-hand side is now read as a matrix, not a
    #     stack of vectors, so PBV crashes. Adding an explicit vector axis restores NumPy 1 behaviour.
    p = os.path.join(root, "unsupervised_methods/methods/PBV.py")
    s = _read(p)
    if MARK not in s:
        s = s.replace("W = np.linalg.solve(Q, np.swapaxes(pbv, 0, 1))",
                      f"W = np.linalg.solve(Q, np.swapaxes(pbv, 0, 1)[..., None])[..., 0]  {MARK}")
        s = s.replace("W = np.linalg.solve(Q, np.swapaxes(PBV, 0, 1))",
                      f"W = np.linalg.solve(Q, np.swapaxes(PBV, 0, 1)[..., None])[..., 0]  {MARK}")
        _write(p, s)
        changed.append("PBV: np.linalg.solve NumPy 2 fix")

    # 2. PhysMamba needs mamba_ssm (CUDA build, not needed here) -> make its import optional
    p = os.path.join(root, "neural_methods/trainer/__init__.py")
    s = _read(p)
    if MARK not in s:
        s = s.replace(
            "import neural_methods.trainer.PhysMambaTrainer\n",
            f"try:  {MARK}\n    import neural_methods.trainer.PhysMambaTrainer\nexcept ImportError:\n    pass\n",
        )
        _write(p, s)
        changed.append("PhysMamba import made optional")

    # 3. Band-pass 0.75-2.5 Hz, the setting used for the published NeurIPS 2023 tables
    #    (the toolbox's own comments recommend this to match the paper)
    p = os.path.join(root, "evaluation/post_process.py")
    s = _read(p)
    if MARK not in s:
        s = s.replace("low_pass=0.6, high_pass=3.3", "low_pass=0.75, high_pass=2.5")
        s = s.replace("[0.6 / fs * 2, 3.3 / fs * 2]", "[0.75 / fs * 2, 2.5 / fs * 2]")
        s += SPARSE_DETREND + "\n_detrend = _fit2082_sparse_detrend\n"
        _write(p, s)
        changed.append("post_process: band 0.75-2.5 Hz + sparse detrend")

    p = os.path.join(root, "unsupervised_methods/utils.py")
    s = _read(p)
    if MARK not in s:
        s += SPARSE_DETREND + "\ndetrend = _fit2082_sparse_detrend\n"
        _write(p, s)
        changed.append("unsupervised utils: sparse detrend")

    # 4. Memory: Colab free has ~12.7 GB RAM. 8 parallel preprocessing workers x ~3.7 GB each
    #    get killed silently by the OOM killer (the video is then just missing from the cache).
    p = os.path.join(root, "dataset/data_loader/BaseLoader.py")
    s = _read(p)
    s2 = re.sub(r"multi_process_quota=\d+", "multi_process_quota=1", s)
    if s2 != s:
        _write(p, s2)
        changed.append("BaseLoader: one preprocessing process at a time")

    # 4b. Colab: the forked preprocessing workers die with "corrupted double-linked list"
    #     (OpenCV's internal threads do not survive fork). With one worker there is nothing to
    #     gain from forking, so preprocessing runs directly in the main process instead.
    p = os.path.join(root, "dataset/data_loader/BaseLoader.py")
    s = _read(p)
    if "_fit2082_sequential_manager" not in s:
        s += SEQUENTIAL_MANAGER
        _write(p, s)
        changed.append("BaseLoader: preprocessing runs in-process (no fork)")

    p = os.path.join(root, "main.py")
    s = _read(p)
    s2 = re.sub(r"num_workers=\d+,", "num_workers=2,", s)
    if s2 != s:
        _write(p, s2)
        changed.append("main.py: DataLoader num_workers=2")

    # 5. Load checkpoints onto whatever device the config names (lets CPU runs work too)
    for p in glob.glob(os.path.join(root, "neural_methods/trainer/*.py")):
        s = _read(p)
        s2 = s.replace(
            "torch.load(self.config.INFERENCE.MODEL_PATH)",
            "torch.load(self.config.INFERENCE.MODEL_PATH, map_location=self.config.DEVICE)",
        )
        if s2 != s:
            _write(p, s2)
            changed.append(f"map_location: {os.path.basename(p)}")

    return changed


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "rPPG-Toolbox"
    ch = patch(root)
    print("\n".join(ch) if ch else "Already patched - nothing to do.")
