#!/usr/bin/env python3
import math
import numpy as np
from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from px4_msgs.msg import VehicleOdometry
from px4_msgs.msg import SensorCombined
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class OdomConverter(Node):

    def __init__(self):
        super().__init__('odom_converter_node')
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        self.tf_broadcaster = TransformBroadcaster(self)
        self.subscription=self.create_subscription(VehicleOdometry, '/fmu/out/vehicle_odometry', self.handler, qos_profile)
        self.subscription_2=self.create_subscription(SensorCombined, '/fmu/out/sensor_combined', self.handler_comb, qos_profile)
        self.publisher_odom=self.create_publisher(Odometry, '/odom', 1)
        self.publisher_imu=self.create_publisher(Imu, '/imu', 1)
        self.subscription
        self.publisher_odom
        self.publisher_imu
    
    def handler(self, msg):
        num = msg.timestamp
        s = str(num)

        # Prime 9 cifre
        nanosec=int(s[-6:]+'000')
        sec=int(s[:-6])


        t = TransformStamped()
        t.header.stamp.sec =sec
        t.header.stamp.nanosec=nanosec
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'

        t.transform.translation.x = float(msg.position[0])
        t.transform.translation.y = float(-msg.position[1])
        t.transform.translation.z = float(-msg.position[2])

        t.transform.rotation.x = float(msg.q[1])
        t.transform.rotation.y = float(-msg.q[2])
        t.transform.rotation.z = float(-msg.q[3])
        t.transform.rotation.w = float(msg.q[0])

        # self.tf_broadcaster.sendTransform(t)

        msg_odom=Odometry();
        msg_odom.header.stamp.sec =sec
        msg_odom.header.stamp.nanosec=nanosec
        msg_odom.header.frame_id='odom'

        msg_odom.child_frame_id='base_link'
        msg_odom.pose.pose.position.x=float(msg.position[0])
        msg_odom.pose.pose.position.y=float(-msg.position[1])
        msg_odom.pose.pose.position.z=float(-msg.position[2])
        
        msg_odom.pose.pose.orientation.x=float(msg.q[1])
        msg_odom.pose.pose.orientation.y=float(-msg.q[2])
        msg_odom.pose.pose.orientation.z=float(-msg.q[3])
        msg_odom.pose.pose.orientation.w=float(msg.q[0])

        msg_odom.twist.twist.linear.x=float(msg.velocity[0])
        msg_odom.twist.twist.linear.y=float(-msg.velocity[1])
        msg_odom.twist.twist.linear.z=float(-msg.velocity[2])

        msg_odom.twist.twist.angular.x=float(msg.angular_velocity[0])
        msg_odom.twist.twist.angular.y=float(-msg.angular_velocity[1])
        msg_odom.twist.twist.angular.z=float(-msg.angular_velocity[2])

        self.publisher_odom.publish(msg_odom)

    def handler_comb(self, msg):
            num = msg.timestamp
            s = str(num)

            # Prime 9 cifre
            nanosec=int(s[-6:]+'000')
            sec=int(s[:-6])
            msg_imu = Imu()

            msg_imu.header.stamp.sec = sec
            msg_imu.header.stamp.nanosec = nanosec
            msg_imu.header.frame_id = 'base_link'

            # Orientation (Quaternion)
  

            # Angular velocity (rad/s)
            msg_imu.angular_velocity.x = float(msg.gyro_rad[0])
            msg_imu.angular_velocity.y = float(-msg.gyro_rad[1])
            msg_imu.angular_velocity.z = float(-msg.gyro_rad[2])

            # Linear acceleration (m/s^2)  
            msg_imu.linear_acceleration.x = float(msg.accelerometer_m_s2[0])
            msg_imu.linear_acceleration.y = float(-msg.accelerometer_m_s2[1])
            msg_imu.linear_acceleration.z = float(-msg.accelerometer_m_s2[2])

            self.publisher_imu.publish(msg_imu)

def main(args=None):
    rclpy.init(args=args)
    pub=OdomConverter()
    rclpy.spin(pub)
    pub.destroy_node()
    rclpy.shutdown()




