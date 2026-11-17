#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import Header
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2


class FakePointCloudPublisher(Node):
    def __init__(self):
        super().__init__('fake_pointcloud_publisher')

        # 2 MB target:
        # PointXYZ float32 = 12 bytes per point
        # 2 * 1024 * 1024 / 12 ≈ 174762 points
        self.num_points = 174762
        self.frame_id = 'lidar_frame'

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self.pub = self.create_publisher(PointCloud2, '/lidar/points', qos)
        self.timer = self.create_timer(0.1, self.publish_cloud)  # 10 Hz

        self.phase = 0.0
        self.get_logger().info(
            f'Publishing fake PointCloud2 on /lidar/points at 10 Hz, '
            f'~{self.num_points * 12 / (1024*1024):.2f} MiB payload'
        )

    def publish_cloud(self):
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = self.frame_id

        # Generate deterministic fake points
        points = []
        for i in range(self.num_points):
            x = float(i % 512) * 0.01
            y = float((i // 512) % 512) * 0.01
            z = 2.0 * math.sin(0.01 * i + self.phase)
            points.append((x, y, z))

        msg = point_cloud2.create_cloud_xyz32(header, points)
        self.pub.publish(msg)
        self.phase += 0.1


def main():
    rclpy.init()
    node = FakePointCloudPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()