# hil_fast-lio2
Hardware-In-The-Loop system to perform 3-dimensional Simultaneous Localization and Mapping using FAST-LIO 2 and the PX4 controller. 

Problem Overview
The testing phase of mobile autonomous systems often cannot be done in a completely simulated environment neither can it always be performed "in the field" especially in the early phases of development of novel and experimental technologies. The concept of Hardware-In-The-Loop was introduced to overcome these obstacles, as it requires the use of the real robot's on-board computer to handle the high-level tasks (such as autonomous trajectory estimation) while receiving realistic inputs from a simulation of the physical robot running on a different computer. With this configuration tests are realistic while at the same time eliminating the risk of damage and consequent economic loss that can result from real world testing. 
This works' objective is to create a testing Hardware-In-The-Loop environment to utilize the FAST-LIO 2 algorithm to build a 3-dimensional map of a Gazebo simulation environment with an UAV controlled via PX4 controller. 

References
This work is based on the FAST-LIO 2 LiDAR-based SLAM algorithm, as described in this paper: 
W. Xu, Y. Cai, D. He, J. Lin and F. Zhang, Fast-lio2: Fast direct lidar-inertial
odometry, IEEE Transactions on Robotics, vol. 38, no. 4, pp. 2053–2073, 2022.
The FAST-LIO 2 implementation used in this system is taken from this repo: 
https://github.com/MIT-SPARK/spark-fast-lio
In the future I plan to develop a parallel implementation of this algorithm either with CUDA or OpenMP to ease the computational load this implementation demands of the NVIDIA Jetson on-board computer. 

Codebase
This work has been built with Robot Operating System 2, the PX4 software toolchain (which includes Gazebo and a library of simulation worlds and robots), including the XRCE agent for interaction with ROS 2.. Installation guides for both can be found here: 
and here: 

Drone Modelling and Data Streams 
As described in the paper, FAST-LIO 2 requires two main data streams from the robot, the PointCloud data produced by the 3D LiDAR and the vehicle's odometry, in particular linear acceleration and angular velocity. A .sdf model of the robot needs to be created to be used in simulation, any starting model works, provided it contains a gyroscope to measure angular velocity and an accelerometer. To this basic model a gpu_lidar sensor must be added which will produce the PointCloud data, in this repository there is an example of a quadricopter model complete with all necessary sensors, in the LiDAR specifications it is ideal to replicate the settings of the real LiDAR to be used for in the field testing to guarantee maximum realism. In addition to the technical specifications of the sensor, the name of the Gazebo topic on which the data will be published must be specified, this is important so that the data from the simulation can be received in the ROS 2 environment. To this end you can find in the launch_test package the configuration of the ROS 2-gz bridge that converts the LiDAR topic in Gazebo into the ROS 2 topic /lidar/points, ready to be used by FAST-LIO 2.
In the launch_test package you can also find instruction for the robot_state_publisher node which will publish the static transforms between the robot's components, in this case these are taken directly from the model file of the drone. These transforms are necessary so that FAST-LIO 2 can compute the extrinsics between the LiDAR's frame and the main robot frame.  
Using the PX4 toolchain allows easy access to the Inertial Measurement Units data (angular velocity and linear acceleration) through the μXRCE agent which acts as an intermediary between the μORB topics used by the controller and ROS 2 topics. To bring together the necessary data from the various topics produced by the μXRCE agent the odom_converter package has been created, it will publish all the data in a single topic called /imu. This node will also take care of the conversion of the data from the Forward-Right-Down (FRD) frame used by Px4 to the Forward-Left-Up (FLU) standard for ROS 2.
xF RD = xF LU
yF RD = −yF LU
zF RD = −zF LU

Hardware-In-the-Loop System 
At this point the two necessary data streams, plus the static transforms, are available as ROS 2 topics. The next step is ensuring the time synchronization of all the nodes with the /clock topic generated from Gazebo, this is also handled through the ROS 2-gz bridge, configured as specified in the launch_test package. Within the spark-fast-lio package the  


