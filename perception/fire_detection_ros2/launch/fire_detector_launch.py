from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Camera Node (Generic USB Camera)
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            name='webcam',
            parameters=[{
                'video_device': '/dev/video0',
                'image_size': [640, 480]
            }]
        ),

        # 2. Your Fire Detection Node
        Node(
            package='my_robot_controller', # Change to your actual package name
            executable='fire_node', # The name defined in setup.py
            name='fire_detector',
            output='screen',
            parameters=[
                {'use_sim_time': False}
            ],
            # Remapping ensures your node listens to the correct camera topic
            remappings=[
                ('/image_raw', '/image_raw') 
            ]
        )
    ])
