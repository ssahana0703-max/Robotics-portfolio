"""
Project: Real-Time Fire Perception Node
Description: A ROS 2 node that uses OpenCV for HSV-based color segmentation
             to detect and track fire signatures in real-time.
Author: Sahana Srinivasan
Tools: ROS 2 Humble, OpenCV, Python
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class FireDetectorNode(Node):
    def __init__(self):
        super().__init__('fire_detector')
        self.subscription = self.create_subscription(
            Image, '/image_raw', self.image_callback, 10)
        self.bridge = CvBridge()

        # 1. Create a Window for Tuning
        cv2.namedWindow("Tuning")
        # Standard fire starting values (Orange/Yellow range)
        cv2.createTrackbar("Low H", "Tuning", 18, 179, lambda x: None)
        cv2.createTrackbar("High H", "Tuning", 35, 179, lambda x: None)
        cv2.createTrackbar("Low S", "Tuning", 100, 255, lambda x: None)
        cv2.createTrackbar("Low V", "Tuning", 200, 255, lambda x: None) # High V ignores red shirts

        self.get_logger().info("Fire Detector with Tuning Sliders Started!")

    def image_callback(self, msg):
        # Convert ROS Image to OpenCV format
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 2. Get current slider positions
        l_h = cv2.getTrackbarPos("Low H", "Tuning")
        u_h = cv2.getTrackbarPos("High H", "Tuning")
        l_s = cv2.getTrackbarPos("Low S", "Tuning")
        l_v = cv2.getTrackbarPos("Low V", "Tuning")

        lower_fire = np.array([l_h, l_s, l_v])
        upper_fire = np.array([u_h, 255, 255])

        # 3. Create the Mask
        mask = cv2.inRange(hsv_frame, lower_fire, upper_fire)

        # 4. Find Contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            if area > 500:  # Filter out small noise
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])

            # 5. DATA LOGGING TO TERMINAL
                    self.get_logger().info(f"🔥 FIRE DETECTED! Coordinates: X={cX}, Y={cY} | Area: {int(area)}")
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    # Draw the box on the original frame
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                    cv2.circle(frame, (x + w//2, y + h//2), 5, (0, 0, 255), -1)

        # 5. Show Windows
        cv2.imshow("Robot Perception Feed", frame)
        cv2.imshow("Mask (B&W Filter)", mask)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = FireDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()