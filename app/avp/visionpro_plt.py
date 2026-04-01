import matplotlib
matplotlib.use("TkAgg")

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from avp_stream import VisionProStreamer

# =========================
# Config
# =========================
AVP_ADDR = "192.168.3.78"

MODE_WORLD = "WORLD"
MODE_BIMANUAL = "BIMANUAL_ZOOM"

display_mode = MODE_BIMANUAL   # 默认启动双手整体缩放模式

# WORLD 模式下的真实米制显示范围
WORLD_XLIM = (-1.2, 1.2)
WORLD_YLIM = (0, 1.8)

# BIMANUAL_ZOOM 模式参数
BIMANUAL_TARGET_HALF_RANGE = 0.95
BIMANUAL_PADDING = 0.20

# 视觉样式
JOINT_SIZE = 40
EXTRA_JOINT_SIZE = 80
LINE_WIDTH = 3

streamer = VisionProStreamer(ip=AVP_ADDR)

# =========================
# Hand topology
# =========================
FINGER_CHAINS_25 = [
    [0, 1, 2, 3, 4],        # thumb
    [5, 6, 7, 8, 9],        # index
    [10, 11, 12, 13, 14],   # middle
    [15, 16, 17, 18, 19],   # ring
    [20, 21, 22, 23, 24],   # pinky
]

PALM_LINKS_25 = [
    (0, 5),
    (5, 10),
    (10, 15),
    (15, 20),
]

# =========================
# Utilities
# =========================
def to_numpy_hand(hand_obj):
    arr = np.asarray(hand_obj)
    if arr.ndim == 3 and arr.shape[1:] == (4, 4):
        return arr
    return None


def try_get_left_right(data):
    left_arr = None
    right_arr = None

    try:
        if hasattr(data, "left"):
            left_arr = to_numpy_hand(data.left)
        if hasattr(data, "right"):
            right_arr = to_numpy_hand(data.right)
    except Exception:
        pass

    if left_arr is None:
        try:
            left_arr = to_numpy_hand(data["left_arm"])
        except Exception:
            pass

    if right_arr is None:
        try:
            right_arr = to_numpy_hand(data["right_arm"])
        except Exception:
            pass

    if left_arr is None:
        try:
            left_arr = to_numpy_hand(data["left_fingers"])
        except Exception:
            pass

    if right_arr is None:
        try:
            right_arr = to_numpy_hand(data["right_fingers"])
        except Exception:
            pass

    return left_arr, right_arr


def world_xz_points(hand_arr):
    # hand_arr: (N, 4, 4)
    return hand_arr[:, [0, 2], 3]


def split_main_extra(pts):
    n = len(pts)
    if n >= 25:
        main_pts = pts[:25]
        extra_pts = pts[25:] if n > 25 else np.empty((0, 2))
        return main_pts, extra_pts
    return pts, np.empty((0, 2))


def compute_global_transform(left_world_pts, right_world_pts,
                             target_half_range=0.95, padding=0.20):
    """
    对双手整体点集计算统一缩放:
      displayed_pts = (pts - center) * scale
    返回 center, scale
    """
    all_pts_list = []
    if left_world_pts is not None and len(left_world_pts) > 0:
        all_pts_list.append(left_world_pts)
    if right_world_pts is not None and len(right_world_pts) > 0:
        all_pts_list.append(right_world_pts)

    if not all_pts_list:
        return np.zeros(2), 1.0

    all_pts = np.vstack(all_pts_list)
    min_xy = all_pts.min(axis=0)
    max_xy = all_pts.max(axis=0)
    center = (min_xy + max_xy) / 2.0
    span = max_xy - min_xy
    max_span = max(float(span[0]), float(span[1]), 1e-9)

    scale = (2.0 * target_half_range) / (max_span * (1.0 + padding))
    return center, scale


def apply_global_transform(pts, center, scale):
    if pts is None or len(pts) == 0:
        return np.empty((0, 2))
    return (pts - center) * scale


def update_line_from_chain(line_obj, pts, chain):
    valid = [i for i in chain if i < len(pts)]
    if len(valid) < 2:
        line_obj.set_data([], [])
        return
    xy = pts[valid]
    line_obj.set_data(xy[:, 0], xy[:, 1])


def update_segment(line_obj, pts, a, b):
    if a < len(pts) and b < len(pts):
        line_obj.set_data([pts[a, 0], pts[b, 0]], [pts[a, 1], pts[b, 1]])
    else:
        line_obj.set_data([], [])


def draw_one_hand(main_pts, extra_pts, finger_lines, palm_lines, scatter_obj, extra_scatter_obj):
    scatter_obj.set_offsets(main_pts if len(main_pts) > 0 else np.empty((0, 2)))
    extra_scatter_obj.set_offsets(extra_pts if len(extra_pts) > 0 else np.empty((0, 2)))

    for line_obj, chain in zip(finger_lines, FINGER_CHAINS_25):
        update_line_from_chain(line_obj, main_pts, chain)

    for line_obj, (a, b) in zip(palm_lines, PALM_LINKS_25):
        update_segment(line_obj, main_pts, a, b)


def apply_axes_mode():
    if display_mode == MODE_WORLD:
        ax.set_xlim(*WORLD_XLIM)
        ax.set_ylim(*WORLD_YLIM)
        ax.set_title("Tracking Streamer - Bimanual Hand Skeleton [WORLD x-z]")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("z (m)")
    else:
        ax.set_xlim(-1.0, 1.0)
        ax.set_ylim(-1.0, 1.0)
        ax.set_title("Tracking Streamer - Bimanual Hand Skeleton [BIMANUAL ZOOM]")
        ax.set_xlabel("display x")
        ax.set_ylabel("display z")

    fig.canvas.draw_idle()


# =========================
# Figure
# =========================
fig, ax = plt.subplots(figsize=(9, 9))
ax.grid(True)
ax.set_aspect("equal", adjustable="box")

left_finger_lines = [ax.plot([], [], linewidth=LINE_WIDTH)[0] for _ in range(5)]
left_palm_lines = [ax.plot([], [], linewidth=LINE_WIDTH)[0] for _ in range(len(PALM_LINKS_25))]
left_scatter = ax.scatter([], [], s=JOINT_SIZE, label="left hand")
left_extra_scatter = ax.scatter([], [], s=EXTRA_JOINT_SIZE, marker="x", label="left extra")

right_finger_lines = [ax.plot([], [], linewidth=LINE_WIDTH)[0] for _ in range(5)]
right_palm_lines = [ax.plot([], [], linewidth=LINE_WIDTH)[0] for _ in range(len(PALM_LINKS_25))]
right_scatter = ax.scatter([], [], s=JOINT_SIZE, label="right hand")
right_extra_scatter = ax.scatter([], [], s=EXTRA_JOINT_SIZE, marker="x", label="right extra")

info_text = ax.text(
    0.02, 0.98, "",
    transform=ax.transAxes,
    va="top"
)

ax.legend(loc="upper right")
apply_axes_mode()

# =========================
# Keyboard control
# =========================
def on_key(event):
    global display_mode

    if event.key == "m":
        display_mode = MODE_BIMANUAL if display_mode == MODE_WORLD else MODE_WORLD
        apply_axes_mode()
    elif event.key == "r":
        apply_axes_mode()

fig.canvas.mpl_connect("key_press_event", on_key)

# =========================
# Animation update
# =========================
def update(_frame):
    data = streamer.get_latest()

    if data is not None:
        left_arr, right_arr = try_get_left_right(data)

        left_world_pts = world_xz_points(left_arr) if left_arr is not None else None
        right_world_pts = world_xz_points(right_arr) if right_arr is not None else None

        if display_mode == MODE_WORLD:
            left_disp_pts = left_world_pts if left_world_pts is not None else np.empty((0, 2))
            right_disp_pts = right_world_pts if right_world_pts is not None else np.empty((0, 2))
        else:
            center, scale = compute_global_transform(
                left_world_pts,
                right_world_pts,
                target_half_range=BIMANUAL_TARGET_HALF_RANGE,
                padding=BIMANUAL_PADDING
            )
            left_disp_pts = apply_global_transform(left_world_pts, center, scale)
            right_disp_pts = apply_global_transform(right_world_pts, center, scale)

        left_main, left_extra = split_main_extra(left_disp_pts)
        right_main, right_extra = split_main_extra(right_disp_pts)

        draw_one_hand(
            left_main, left_extra,
            left_finger_lines, left_palm_lines,
            left_scatter, left_extra_scatter
        )

        draw_one_hand(
            right_main, right_extra,
            right_finger_lines, right_palm_lines,
            right_scatter, right_extra_scatter
        )

        left_n = 0 if left_arr is None else len(left_arr)
        right_n = 0 if right_arr is None else len(right_arr)
        info_text.set_text(
            f"mode = {display_mode}\n"
            f"left joints = {left_n}\n"
            f"right joints = {right_n}\n"
            f"[m] toggle mode   [r] reset view"
        )
    else:
        info_text.set_text(
            f"mode = {display_mode}\n"
            f"waiting for tracking data...\n"
            f"[m] toggle mode   [r] reset view"
        )

    artists = []
    artists.extend(left_finger_lines)
    artists.extend(left_palm_lines)
    artists.extend(right_finger_lines)
    artists.extend(right_palm_lines)
    artists.extend([left_scatter, left_extra_scatter, right_scatter, right_extra_scatter, info_text])
    return artists


ani = FuncAnimation(
    fig,
    update,
    interval=33,
    blit=False,
    cache_frame_data=False
)

plt.show()