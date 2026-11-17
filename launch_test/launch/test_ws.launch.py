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

    bridge_config_clk = os.path.join(pkg_share, 'config', 'bridge_clock.yaml')
    bridge_config_lidar = os.path.join(pkg_share, 'config', 'bridge_lidar.yaml')
    assert os.path.isfile(bridge_config_clk), f"File non trovato: {bridge_config_clk}"
    assert os.path.isfile(bridge_config_lidar), f"File non trovato: {bridge_config_lidar}"

    bridge_clk = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge_clk',
        output='screen',
        parameters=[{'config_file': bridge_config_clk, 'use_sim_time': use_sim_time}]
    )
    bridge_lidar = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge_lidar',
        output='screen',
        parameters=[{'config_file': bridge_config_lidar, 'use_sim_time': use_sim_time}]
    )
    delayed_bridge = TimerAction(
        period=30.0,  # secondi
        actions=[bridge_clk, bridge_lidar]
    )
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'),
        # Node(
        #     package='robot_state_publisher',
        #     executable='robot_state_publisher',
        #     name='robot_state_publisher',
        #     output='screen',
        #     parameters=[{'use_sim_time': use_sim_time, 'robot_description': urdf}],
        #     arguments=[urdf]),
        ExecuteProcess(
            prefix=['xterm -hold -e'],
            cwd='/home/ubuntu/PX4-Autopilot',
            cmd=[[
                'make px4_sitl gz_x500'
            ]],
            shell=True,
            output='screen'
        ),
        # Node(
        #     package='odom_converter',
        #     executable='odom_converter',
        #     name='odom_converter',
        #     output='screen',
        #     parameters=[{'use_sim_time': use_sim_time}],
        # ),
        # ExecuteProcess(
        #      prefix=['xterm -hold -e'],
        #     cwd='/home/ubuntu/PX4-Autopilot',
        #     cmd=[[
        #         'MicroXRCEAgent udp4 -p 8888'
        #      ]],
        #     shell=True
        # ),
       delayed_bridge
    ])

