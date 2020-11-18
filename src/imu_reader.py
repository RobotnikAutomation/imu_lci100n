#! /usr/bin/env python3
import serial
import time

import rospy
from sensor_msgs.msg import Imu


class IMUTest:
    def __init__(self):
        
        rospy.init_node('imu')

        self.port = rospy.get_param('~port', '/dev/ttyUSB0')
        self.baudrate = rospy.get_param('~baudrate', 460800)
        self.parity = rospy.get_param('~parity', serial.PARITY_NONE)
        self.stopbits = rospy.get_param('~stopbits', 1)
        self.bytesize = rospy.get_param('~bytesize', 8)
        self.timeout = rospy.get_param('~timeout', 0.1)
        
        self.pub = rospy.Publisher('~data_raw', Imu, queue_size=10)
        self.message = Imu()
        self.serial_device = serial.Serial(
            port= self.port,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stopbits,
            bytesize=self.bytesize,
            timeout=self.timeout,
            xonxoff=False,
            dsrdtr=False,
            rtscts=False
        )

    def start(self):
        found = False
        
        while not rospy.is_shutdown():
            read = self.serial_device.read(1)
            try:
                if read == bytes("N", 'utf-8'):
                    read = self.serial_device.read(1)
                    if read == bytes("L", 'utf-8'):
                        
                        read = self.serial_device.read(100)

                        self.quaternion_0 = int.from_bytes(read[4:8], 'big', signed= True) * 2**-30
                        self.quaternion_1 = int.from_bytes(read[8:12], 'big', signed= True) * 2**-30
                        self.quaternion_2 = int.from_bytes(read[12:16], 'big', signed= True) * 2**-30
                        self.quaternion_3 = int.from_bytes(read[16:20], 'big', signed= True) * 2**-30
                        
                        #Nos da la informacion en diferencial angular (rad), de aquí tenemos que sacar la velocidad angular
                        #Velocidad angular = rad / s
                        self.message.angular_velocity.x = int.from_bytes(read[44:48]    , 'big',  signed= True) * 1.0e-9
                        self.message.angular_velocity.y = int.from_bytes(read[48:52]    , 'big',  signed= True) * 1.0e-9
                        self.message.angular_velocity.z = int.from_bytes(read[52:56]    , 'big',  signed= True) * 1.0e-9

                        #Nos da la informacion en incrementos de velocidad (m/s), de aquí tenemos que sacar la aceleracion lineal
                        #Aceleracion lineal = m/s²
                        self.message.linear_acceleration.x = int.from_bytes(read[60:64]    , 'big',  signed= True) * 2.0e-8
                        self.message.linear_acceleration.y = int.from_bytes(read[64:68]    , 'big',  signed= True) * 2.0e-8
                        self.message.linear_acceleration.z = int.from_bytes(read[68:72]    , 'big',  signed= True) * 2.0e-8
                        
                        #Tiempo para calculos del giroscopio
                        gyro_time = int.from_bytes(read[76:78]    , 'big',  signed= False) * 0.5 * 1.0e-6
                        #Tiempo para calculos del acelerometro
                        acel_time = int.from_bytes(read[78:80]    , 'big',  signed= False) * 0.5 * 1.0e-6

                        # ROS MESSAGE
                        self.message.header.stamp = rospy.Time.now()
                        self.message.header.frame_id = "imu_link"

                        self.message.orientation.x = self.quaternion_1
                        self.message.orientation.y = self.quaternion_2
                        self.message.orientation.z = self.quaternion_3
                        self.message.orientation.w = self.quaternion_0

                        #Calculo de velocidad angular a partir de los incrementos de radianes
                        self.message.angular_velocity.x = self.message.angular_velocity.x / gyro_time
                        self.message.angular_velocity.y = self.message.angular_velocity.y / gyro_time
                        self.message.angular_velocity.z = self.message.angular_velocity.z / gyro_time

                        self.message.linear_acceleration.x = self.message.linear_acceleration.x / acel_time
                        self.message.linear_acceleration.y = self.message.linear_acceleration.y / acel_time
                        self.message.linear_acceleration.z = self.message.linear_acceleration.z / acel_time

                        self.pub.publish(self.message)

            except Exception as e:
                print(e)
            time.sleep(0.001)

if __name__ == '__main__':
    imu_test = IMUTest()
    imu_test.start()

