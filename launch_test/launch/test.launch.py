from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression, FindExecutable, PathJoinSubstitution, FileContent
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os
from glob import glob

def generate_launch_description():
    pkg_share = get_package_share_directory('launch_test')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    urdf = FileContent(PathJoinSubstitution([FindPackageShare('launch_test'), 'config/drone.urdf.xml']))

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time, 'robot_description': urdf}],
            arguments=[urdf]),
        Node(
            package='odom_converter',
            executable='odom_converter',
            name='odom_converter',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
        ),
        ExecuteProcess(
             prefix=['xterm -hold -e'],
            cwd='/home/ubuntu/PX4-Autopilot',
            cmd=[[
                'MicroXRCEAgent udp4 -p 8888'
             ]],
            shell=True
        )
    ])

