<h1 align="center">HIL-SLAM: Hardware-In-The-Loop 3D LiDAR SLAM with FAST-LIO 2 and PX4</h1>

<p align="center">
  <a href="https://docs.ros.org/en/jazzy/"><img alt="ROS 2 Jazzy" src="https://img.shields.io/badge/ROS_2-Jazzy-22314E?logo=ros&logoColor=white"></a>
  <a href="https://docs.px4.io/"><img alt="PX4" src="https://img.shields.io/badge/PX4-Autopilot-1D2951?logo=px4&logoColor=white"></a>
  <a href="https://gazebosim.org/"><img alt="Gazebo" src="https://img.shields.io/badge/Gazebo-Simulation-F58113"></a>
  <a href="https://github.com/MIT-SPARK/spark-fast-lio"><img alt="FAST-LIO 2" src="https://img.shields.io/badge/FAST--LIO_2-3D_SLAM-8A2BE2"></a>
  <img alt="LiDAR" src="https://img.shields.io/badge/LiDAR-3D_Point_Clouds-0A7BBB">
  <a href="https://developer.nvidia.com/embedded/jetson-modules"><img alt="NVIDIA Jetson" src="https://img.shields.io/badge/NVIDIA-Jetson-76B900?logo=nvidia&logoColor=white"></a>
  <img alt="C++" src="https://img.shields.io/badge/C++-00599C?logo=cplusplus&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white">
</p>

<p align="center">
  A Hardware-In-The-Loop system to perform 3-dimensional Simultaneous Localization and Mapping (SLAM) using FAST-LIO 2 and the PX4 controller.
</p>

https://github.com/user-attachments/assets/f9c53bc0-b842-4c4d-bcaa-70fb8c3c75a0

---

## Table of Contents

- [Problem Overview](#problem-overview)
- [References](#references)
- [Codebase](#codebase)
- [Drone Modelling and Data Streams](#drone-modelling-and-data-streams)
- [Hardware-In-The-Loop System](#hardware-in-the-loop-system)
- [Startup Guide](#startup-guide)
  - [1. Preparation](#1-preparation)
  - [2. PX4 ↔ ROS 2 Communication](#2-setting-up-px4--ros-2-communication)
  - [3. System Startup](#3-system-startup)
  - [4. Optional: KISS-Matcher Node](#4-optional-kiss-matcher-node)

---

## Problem Overview

The testing phase of mobile autonomous systems often cannot be done in a completely simulated environment, nor can it always be performed "in the field", especially in the early phases of development of novel and experimental technologies. The concept of Hardware-In-The-Loop (HIL) was introduced to overcome these obstacles: it uses the real robot's on-board computer to handle the high-level tasks (such as autonomous trajectory estimation) while receiving realistic inputs from a simulation of the physical robot running on a different computer. With this configuration, tests are realistic while the risk of damage, and the consequent economic loss that can result from real-world testing, is eliminated.

The objective of this work is to create a testing Hardware-In-The-Loop environment that uses the FAST-LIO 2 algorithm to build a 3-dimensional map of a Gazebo simulation environment with a UAV controlled via the PX4 controller.

<p align="center">
  <img width="600" alt="HIL system overview" src="https://github.com/user-attachments/assets/22ec6e12-e10a-4026-a120-acacc273e913" />
</p>

---

## References

This work is based on the FAST-LIO 2 LiDAR-based SLAM algorithm, as described in this paper:

> W. Xu, Y. Cai, D. He, J. Lin and F. Zhang, *FAST-LIO2: Fast Direct LiDAR-Inertial Odometry*, IEEE Transactions on Robotics, vol. 38, no. 4, pp. 2053–2073, 2022.

The FAST-LIO 2 implementation used in this system is taken from [MIT-SPARK/spark-fast-lio](https://github.com/MIT-SPARK/spark-fast-lio).

In the future I plan to develop a parallel implementation of this algorithm, either with CUDA or OpenMP, to ease the computational load that this implementation places on the NVIDIA Jetson on-board computer.

---

## Codebase

This work has been built with Robot Operating System 2 (ROS 2) and the PX4 software toolchain, which includes Gazebo and a library of simulation worlds and robots, as well as the XRCE agent for interaction with ROS 2. Installation guides can be found here:

| Tool | Guide |
|---|---|
| **ROS 2 Jazzy** | [ROS 2 Jazzy installation guide](https://docs.ros.org/en/jazzy/Installation.html) |
| **PX4** | [PX4 development environment setup](https://docs.px4.io/main/en/dev_setup/dev_env.html) |
| **PX4 + ROS 2** | [PX4 ROS 2 user guide](https://docs.px4.io/main/en/ros2/user_guide.html) |
| **Micro XRCE-DDS** | [PX4 uXRCE-DDS (PX4-ROS 2/DDS bridge)](https://docs.px4.io/main/en/middleware/uxrce_dds.html) |

---

## Drone Modelling and Data Streams

As described in the paper, FAST-LIO 2 requires two main data streams from the robot: the point cloud produced by the 3D LiDAR, and the vehicle's inertial data, in particular linear acceleration and angular velocity.

A `.sdf` model of the robot needs to be created for the simulation. Any starting model works, provided it contains a gyroscope to measure angular velocity and an accelerometer. To this basic model a `gpu_lidar` sensor must be added, which will produce the point cloud data. This repository contains an example of a quadcopter model complete with all the necessary sensors. In the LiDAR specifications it is ideal to replicate the settings of the real LiDAR to be used for field testing, to guarantee maximum realism. In addition to the technical specifications of the sensor, the name of the Gazebo topic on which the data will be published must be specified, so that the data from the simulation can be received in the ROS 2 environment. To this end, the `launch_test` package contains the configuration of the ROS 2–Gazebo bridge that converts the LiDAR topic in Gazebo into the ROS 2 topic `/lidar/points`, ready to be used by FAST-LIO 2.

<p align="center">
  <img width="520" alt="Drone model with LiDAR in Gazebo" src="https://github.com/user-attachments/assets/0b84b53b-4964-4a3f-90ff-d722e91cd613" />
</p>

The `launch_test` package also contains the instructions for the `robot_state_publisher` node, which publishes the static transforms between the robot's components; in this case they are taken directly from the drone's model file. These transforms are necessary so that FAST-LIO 2 can compute the extrinsics between the LiDAR frame and the main robot frame.

Using the PX4 toolchain allows easy access to the Inertial Measurement Unit (IMU) data (angular velocity and linear acceleration) through the μXRCE agent, which acts as an intermediary between the μORB topics used by the controller and ROS 2 topics. To bring together the necessary data from the various topics produced by the μXRCE agent, the `odom_converter` package has been created; it publishes all the data in a single topic called `/imu`. This node also takes care of converting the data from the Forward-Right-Down (FRD) frame used by PX4 to the Forward-Left-Up (FLU) standard of ROS 2:

<p align="center">
  <b>x</b><sub>FRD</sub> = <b>x</b><sub>FLU</sub><br>
  <b>y</b><sub>FRD</sub> = −<b>y</b><sub>FLU</sub><br>
  <b>z</b><sub>FRD</sub> = −<b>z</b><sub>FLU</sub>
</p>

---

## Hardware-In-The-Loop System

At this point the two necessary data streams, plus the static transforms, are available as ROS 2 topics. The next step is ensuring the time synchronization of all the nodes with the `/clock` topic generated by Gazebo; this is also handled through the ROS 2–Gazebo bridge, configured as specified in the `launch_test` package. The configuration of the FAST-LIO 2 algorithm can be set and modified within the `spark-fast-lio` package.

---

## Startup Guide

This section describes how to prepare and start the HIL system, which consists of a **workstation** (PX4 simulation and visualization) and a **Jetson** (XRCE agent and SLAM with FAST-LIO 2).

### 1. Preparation

#### 1.1 ROS 2 Packages

From the files in the OneDrive folder containing the code, download and import the following packages into the respective ROS 2 workspaces:

| Device | Packages to import |
|---|---|
| **Jetson** | `odom_converter`, `spark-fast-lio`, `launch_test` |
| **Workstation** | `launch_test` |

The `odom_converter` package collects the IMU data coming from the XRCE agent, which is spread across several topics, into a single topic for the node that handles SLAM, namely `spark-fast-lio`. `launch_test` is simply a container for the system startup configurations on the workstation and the Jetson, intended to simplify launching the auxiliary nodes the system needs to work.

### 2. Setting up PX4 ↔ ROS 2 Communication

After modifying the drone model, start a PX4 simulation on the workstation and set the following parameters from the simulation console:

```
param set UXRCE_DDS_SYNCT 0
param set UXRCE_DDS_AG_IP [Jetson IP converted to an integer]
```

- `UXRCE_DDS_SYNCT 0` is used for time synchronization with ROS 2.
- `UXRCE_DDS_AG_IP` connects the PX4 console to the XRCE agent running on the Jetson.

> [!IMPORTANT]
> After changing the parameters, the simulation must be restarted, otherwise the changes will not take effect.

#### Verification

Shut down and restart the simulation, then start the Micro XRCE agent on the Jetson:

```bash
MicroXRCEAgent udp4 -p 8888
```

If the agent console on the Jetson shows the output described in the [official PX4 guide](https://docs.px4.io/main/en/middleware/uxrce_dds.html), the connection was successful.

### 3. System Startup

#### 3.1 ROS 2 Environment Configuration

On both the **Jetson** and the **workstation**, the ROS 2 environment must be set up before launching the nodes:

```bash
ros2 daemon stop
export FASTDDS_BUILTIN_TRANSPORTS=LARGE_DATA
export RMW_FASTRTPS_PUBLICATION_MODE=SYNCHRONOUS
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
ros2 daemon start
```

These commands set a transport protocol mode suited to the large data volumes transmitted by the LiDAR.

> [!NOTE]
> These commands must be run in **every** terminal used to launch ROS 2 nodes. The whole system therefore requires **2 terminals on the workstation** and **2 terminals on the Jetson** configured this way.

#### 3.2 Workstation

First, start the **QGroundControl** app, which allows you to control the drone. Then run the following commands.

**Terminal 1**: starts the PX4 simulation and the bridges needed for the system to work:

```bash
ros2 launch launch_test test_ws.launch.py
```

**Terminal 2**: starts RViz to visualize the LiDAR output and the robot's odometry:

```bash
ros2 launch spark_fast_lio rviz.launch.yaml
```

#### 3.3 Jetson

**Terminal 1**: starts the XRCE agent and the auxiliary nodes needed for the system to work:

```bash
ros2 launch launch_test test.launch.py
```

**Terminal 2**: starts FAST-LIO 2:

```bash
ros2 launch spark_fast_lio custom.launch.yaml start_rviz:=false
```

#### 3.4 Verifying Correct Operation

If startup was successful, the output of the SLAM algorithm should be visible in RViz 2 on the workstation.

### 4. Optional: KISS-Matcher Node

To add the KISS-Matcher node to the system, run the following on the **workstation**:

```bash
ros2 launch kiss_matcher_ros rviz.launch.yaml odom_topic:=/odometry scan_topic:=/cloud_registered
```

> [!WARNING]
> Running KISS-Matcher on the Jetson causes the system to crash, because the Jetson's computational resources are not sufficient to run the SLAM node and the KISS-Matcher node together.
