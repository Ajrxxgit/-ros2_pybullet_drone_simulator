
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import pybullet as p
import pybullet_data

import math


class DroneSimulator(Node):

    def __init__(self):

        super().__init__('drone_simulator')

        # Subscriber
        self.subscription = self.create_subscription(
            String,
            '/drone_cmd',
            self.command_callback,
            10
        )

        # IMU Publisher
        self.imu_pub = self.create_publisher(
            String,
            '/imu',
            10
        )

        self.get_logger().info("Subscriber Started")

        # PyBullet Setup
        p.connect(p.GUI)

        p.setAdditionalSearchPath(
            pybullet_data.getDataPath()
        )

        p.loadURDF("plane.urdf")

        self.drone = p.loadURDF(
            "cf2x.urdf",
            [0, 0, 1]
        )

        # Position
        self.x = 0.0
        self.y = 0.0
        self.z = 1.0

        # Velocity
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0

        # Rotation
        self.yaw = 0.0
        self.yaw_rate = 0.0

        # Limits
        self.MAX_SPEED = 0.05
        self.MAX_VZ = 0.02
        self.MAX_YAW_RATE = 2.0

        # Circle mode
        self.circle_mode = False
        self.circle_angle = 0.0
        self.circle_radius = 2.0
        self.circle_speed = 0.003
        self.circle_center_x = 0.0
        self.circle_center_y = 0.0

        # Simulation Timer
        self.timer = self.create_timer(
            1.0 / 240.0,
            self.update_simulation
        )

    def command_callback(self, msg):

        command = msg.data

        self.get_logger().info(
            f"Received: {command}"
        )

        if command == "FORWARD":
            self.vy += 0.01

        elif command == "BACKWARD":
            self.vy -= 0.01

        elif command == "LEFT":
            self.vx -= 0.01

        elif command == "RIGHT":
            self.vx += 0.01

        elif command == "UP":
            self.vz += 0.005

        elif command == "DOWN":
            self.vz -= 0.005

        elif command == "YAW_LEFT":
            self.yaw_rate += 0.2

        elif command == "YAW_RIGHT":
            self.yaw_rate -= 0.2

        elif command == "CIRCLE":

            self.circle_mode = True
            self.circle_angle = 0.0

            self.circle_center_x = self.x
            self.circle_center_y = self.y

            self.get_logger().info(
                "Starting Circular Motion"
            )

    def update_simulation(self):

        self.vx = max(
            -self.MAX_SPEED,
            min(self.MAX_SPEED, self.vx)
        )

        self.vy = max(
            -self.MAX_SPEED,
            min(self.MAX_SPEED, self.vy)
        )

        self.vz = max(
            -self.MAX_VZ,
            min(self.MAX_VZ, self.vz)
        )

        self.yaw_rate = max(
            -self.MAX_YAW_RATE,
            min(self.MAX_YAW_RATE, self.yaw_rate)
        )

        # Circular motion
        if self.circle_mode:

            self.circle_angle += self.circle_speed

            self.x = (
                self.circle_center_x +
                self.circle_radius *
                math.cos(self.circle_angle)
            )

            self.y = (
                self.circle_center_y +
                self.circle_radius *
                math.sin(self.circle_angle)
            )

            self.yaw += 0.1

        else:

            self.x += self.vx
            self.y += self.vy

        # Allow UP/DOWN even in circle mode
        self.z += self.vz

        if self.z < 0.1:
            self.z = 0.1

        # Manual yaw control
        self.yaw += self.yaw_rate

        orientation = p.getQuaternionFromEuler(
            [0, 0, math.radians(self.yaw)]
        )

        p.resetBasePositionAndOrientation(
            self.drone,
            [self.x, self.y, self.z],
            orientation
        )

        # Damping
        self.vx *= 0.98
        self.vy *= 0.98
        self.vz *= 0.98
        self.yaw_rate *= 0.95

        # IMU Data
        position, orientation = p.getBasePositionAndOrientation(
            self.drone
        )

        linear_vel, angular_vel = p.getBaseVelocity(
            self.drone
        )

        imu_msg = String()

        imu_msg.data = (
            f"Position={position}, "
            f"LinearVel={linear_vel}, "
            f"AngularVel={angular_vel}"
        )

        self.imu_pub.publish(imu_msg)

        p.stepSimulation()


def main():

    rclpy.init()

    node = DroneSimulator()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
