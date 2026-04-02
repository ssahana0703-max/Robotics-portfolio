# 🔍 Real-Time Fire Perception (ROS 2 & OpenCV)

This package implements a computer vision pipeline to detect and track fire signatures using color segmentation and image moments.

## 🛠 Key Features
- **HSV Segmentation:** Robustly isolates fire-colored pixels, minimizing interference from ambient lighting.
- **Dynamic Tuning:** Integrated OpenCV trackbars for real-time threshold calibration.
- **ROS 2 Integration:** Uses `cv_bridge` to convert sensor data for real-time processing.
- **Centroid Tracking:** Calculates the (X, Y) coordinates of the fire for autonomous navigation.

## 🚀 How to Run
1. Source your ROS 2 Humble environment.
2. Run the launch file:
   ```bash
   ros2 launch my_robot_controller fire_detector_launch.py
   ```
