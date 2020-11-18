# Ros Package: imu_lci100n
This is a ROS package for reading the data from the LCI-100N, create a Imu message and public it in the **/imu/data_raw**.
It uses **python3** because of the use of the Integer class to transform the bytes into useable data.

## ROS

### Params

-  **port**: USB port for the IMU (default: /dev/ttyUSB0)

### Topics

#### Publications

- **imu/data_raw**: Publishes the data received from the IMU.
  - type: sensor_msgs/Imu
