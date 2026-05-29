

#  Real-Time Fire Perception Node (ROS 2 & OpenCV)

A ROS 2 Humble node that utilizes real-time computer vision techniques to detect, segment, and track fire signatures through an HSV color segmentation pipeline.


## 🧠 Perception Pipeline Architecture

The perception node handles raw image streams and processes them through a sequence of matrix transformations to isolate high-intensity thermal signatures:

```text
       ┌────────────────────────┐
       │     /image_raw         │  ◄── (v4l2_camera Stream @ 640x480)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │   cv_bridge Conversion │  ◄── (Converts ROS Image msg to BGR)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │    BGR ──▶ HSV Space   │  ◄── (Isolates Hue from Light Intensity)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │   HSV Range Threshold  │  ◄── (Dynamic trackbars isolate fire hues)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  Contour Vectorization │  ◄── (Extracts geometric boundaries)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ Area Filtering & Image │  ◄── (Noise threshold > 500 px²;
       │ Moments (Centroid)     │       calculates spatial cX, cY)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  Target Visualization  │  ◄── (Draws Bounding Box + Centroid)
       └────────────────────────┘

```

---

## 🛠️ Features & Configuration Parameters

* **HSV Color Space Segmentation:** Decouples color saturation and hue from illumination changes, preventing false positives from changing room brightness.
* **Live Calibration Sliders:** Built-in OpenCV Trackbar window allows for instant range tweaking while the node is streaming live data.
* **Spatial Tracking:** Calculates spatial centroids using geometric image moments ($M_{00}, M_{10}, M_{01}$) to pinpoint exact target pixel coordinates.

### Default Tuning Presets

| Parameter | Default Value | Max Value | Target Filtering Role |
| --- | --- | --- | --- |
| **Low H** | `18` | `179` | Filters out cold reds, starts at early orange/yellow hues. |
| **High H** | `35` | `179` | Caps off the spectrum before reaching bright greens. |
| **Low S** | `100` | `255` | Eliminates pale, low-saturation ambient background lights. |
| **Low V** | `200` | `255` | Strictly accepts high-brightness signatures (ignores orange/red clothing). |

---

## 📂 Repository Structure

```text
my_robot_controller/
├── docs/
│   └── fire_detection_demo.gif     # Live system demonstration clip
├── launch/
│   └── fire_perception.launch.py   # Launch file grouping camera & perception nodes
├── my_robot_controller/
│   ├── __init__.py
│   └── fire_node.py                # Main Python ROS 2 Node source code
├── package.xml
├── setup.cfg
└── setup.py

```

---

## 🚀 Installation & Running

### 1. Prerequisites

Ensure you have a working installation of **ROS 2 Humble** and a Linux-compatible USB web-camera available at `/dev/video0`.

### 2. Build the Package

Navigate to your ROS 2 workspace directory (`colcon_ws`) and compile:

```bash
cd ~/colcon_ws
colcon build --packages-select my_robot_controller
source install/setup.bash

```

### 3. Execution via Launch File

The included launch file handles initialization of the physical webcam node (`v4l2_camera_node`), handles target topic remapping, and sets up stdout logging output flags inside a single terminal execution:

```bash
ros2 launch my_robot_controller fire_perception.launch.py

```

---

## 📊 Live Logging Output Sample

When the tracking surface area crosses the 500px filter threshold, spatial coordinate updates are continuously streamed to the console:

```text
[fire_detector-2] [INFO] [Fire Detector]: 🔥 FIRE DETECTED! Coordinates: X=293, Y=229 | Area: 25112
[fire_detector-2] [INFO] [Fire Detector]: 🔥 FIRE DETECTED! Coordinates: X=294, Y=228 | Area: 25219
[fire_detector-2] [INFO] [Fire Detector]: 🔥 FIRE DETECTED! Coordinates: X=297, Y=224 | Area: 24987

```

---

## 📝 License

MIT
