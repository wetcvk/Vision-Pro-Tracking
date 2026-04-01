# Vision Pro 追踪数据接收与处理系统

一个基于 `avp_stream` 的 Apple Vision Pro 追踪数据采集与处理系统，用于实时接收头部、手腕、手指的姿态数据，并保存为结构化的 JSON Lines 格式，方便后续用于机器人模仿学习、动作重定向等研究。

---

##  功能特性

- **实时数据接收**：通过 IP 连接 Vision Pro，低延迟获取追踪流数据
- **结构化数据解析**：将原始流数据解析为 `AVPFrame`，包含头部、左右手腕、手指关节、捏合距离、手腕翻转角
- **坐标变换工具**：安全提取 4×4 齐次变换矩阵中的平移分量 (`x, y, z`)
- **持久化存储**：以 `JSONL` 格式自动保存每一帧数据，便于后续读取与分析
- **模块化架构**：`streamer -> parser -> pipeline -> saver` 分层设计，预留了相机、机器人控制、动作重定向扩展接口

---

##  项目结构

```
visionpro/
├── app/
│   ├── avp/                      # Vision Pro 连接与解析层
│   │   ├── streamer.py           # 封装 avp_stream 数据流客户端
│   │   ├── parser.py             # 原始数据解析为 AVPFrame
│   │   └── visionpro_plt.py      # 可视化扩展（预留）
│   ├── common/                   # 公共工具模块
│   │   ├── types.py              # 数据类型定义（AVPFrame 等）
│   │   ├── transforms.py         # 数组/矩阵安全转换、坐标提取
│   │   └── data_saver.py         # JSONL 数据保存器
│   ├── pipelines/                # 业务管道
│   │   └── receiver_pipeline.py  # 主接收循环管道
│   └── data/                     # 采集的数据存储目录
├── configs/
│   └── system.yaml               # 系统配置文件
├── scripts/
│   ├── run_receiver.py           # 启动接收管道
│   ├── receiver_test.py          # 测试脚本
│   └── another_test.py           # 其他测试脚本
├── requirements.txt
└── README.md
```

---

##  快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Vision Pro IP

编辑 `configs/system.yaml`，将 `avp.ip` 修改为 Vision Pro Tracking Streamer 上显示的实际 IP 地址：

```yaml
avp:
  ip: "192.168.3.78"   # ← 修改为你的 Vision Pro IP
  record: false
```

### 3. 启动接收程序

```bash
python scripts/run_receiver.py
```

程序启动后将持续接收数据，按 `Ctrl+C` 停止。采集的数据会自动保存到 `app/data/tracking_MMDDHHMMSS.jsonl`。

---

## ️ 配置说明

`configs/system.yaml` 中主要配置项如下：

| 配置块 | 关键项 | 说明 |
|--------|--------|------|
| `avp` | `ip` | Vision Pro 的 IP 地址 |
| `runtime` | `loop_sleep_s` | 主循环间隔，控制 CPU 占用 |
| `runtime` | `print_interval_s` | 控制台打印间隔 |
| `processing` | `enable_filter` | 是否启用低通滤波（预留） |
| `dataset` | `enable` / `save_dir` | 数据集保存开关与路径（预留） |
| `camera` | `enable` / `width` / `height` | 相机采集扩展（预留） |
| `robot` | `enable` / `type` | 机器人控制扩展（预留） |
| `retargeting` | `enable` / `scale` / `workspace` | 动作重定向扩展（预留） |

---

##  数据格式

每一帧保存的数据结构如下（以 `JSONL` 中的一行为例）：

数据格式为 float32 各项数据含义参见/app/data/data_sample.json

```json
{
  "frame_id": 1,
  "timestamp_ns": 1712345678901234567,
  "head": [[...], [...], [...], [...]],          // 4x4 矩阵
  "left_wrist": [[...], [...], [...], [...]],    // 4x4 矩阵
  "right_wrist": [[...], [...], [...], [...]],   // 4x4 矩阵
  "left_fingers": [...],                         // 含25个4x4矩阵
  "right_fingers": [...],                        // 含25个4x4矩阵
  "left_pinch_distance": 0.01234,
  "right_pinch_distance": 0.05678,
  "left_wrist_roll": 0.12345,
  "right_wrist_roll": 0.67890
}
```

---

##  后续扩展计划

- [ ] 启用低通滤波，平滑姿态抖动
- [ ] 接入相机流，实现视觉-动作同步采集
- [ ] 接入真实机器人或 ROS 控制接口
- [ ] 动作重定向（Retargeting），将人手姿态映射到机械臂末端
- [ ] 导出为标准 HDF5 / RLDS 数据集格式

---

##  许可

本项目为毕业设计研究项目，仅供学习与研究使用。
