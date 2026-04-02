from setuptools import find_packages, setup
import os       

from glob import glob 
package_name = 'my_robot_controller'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Sahana Srinivasan,
    maintainer_email='ssahana0703@gmail.com',
	description='ROS 2 Perception node for real-time fire detection using OpenCV and HSV segmentation.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [ 'fire_node = my_robot_controller.fire_detector:main',
        ],
    },
)
