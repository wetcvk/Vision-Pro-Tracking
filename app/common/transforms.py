import numpy as np


def safe_array(x):
    if x is None:
        return None
    return np.asarray(x, dtype=np.float32)


def safe_first_matrix(x):
    """
    把 (1,4,4) 取成 (4,4)
    """
    arr = safe_array(x)
    if arr is None:
        return None
    if arr.ndim == 3 and arr.shape[0] == 1:
        return arr[0]
    return arr


def extract_xyz(T):
    """
    从 4x4 齐次变换矩阵中取平移分量
    """
    if T is None:
        return None
    if T.shape != (4, 4):
        return None
    return T[:3, 3].astype(np.float32)


def format_xyz(xyz):
    if xyz is None:
        return "None"
    return np.array2string(np.round(xyz, 4), separator=", ")


def fingers_count(fingers):
    if fingers is None:
        return 0
    if fingers.ndim >= 3:
        return int(fingers.shape[0])
    return 0
