import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TeleopPublisher(Node):

    def __init__(self):
        super().__init__('teleop_publisher')

        self.publisher_ = self.create_publisher(
            String,
            '/drone_cmd',
            10
        )

        self.get_logger().info("Teleop Started")

        self.run()

    def run(self):

        while rclpy.ok():

            cmd = input(
                "\n[w] Forward\n"
                "[s] Backward\n"
                "[a] Yaw Left\n"
                "[d] Yaw Right\n"
                "[q] Up\n"
                "[e] Down\n"
                "[j] Left\n"
                "[l] Right\n"
                "[o] Circle Path\n\n"
                "Command: "
            )

            msg = String()

            if cmd == 'w':
                msg.data = "FORWARD"

            elif cmd == 's':
                msg.data = "BACKWARD"

            elif cmd == 'j':
                msg.data = "LEFT"

            elif cmd == 'l':
                msg.data = "RIGHT"

            elif cmd == 'q':
                msg.data = "UP"

            elif cmd == 'e':
                msg.data = "DOWN"

            elif cmd == 'a':
                msg.data = "YAW_LEFT"

            elif cmd == 'd':
                msg.data = "YAW_RIGHT"

            elif cmd == 'o':
                msg.data = "CIRCLE"

            else:
                continue

            self.publisher_.publish(msg)

            self.get_logger().info(
                f"Published: {msg.data}"
            )


def main():

    rclpy.init()

    node = TeleopPublisher()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()

