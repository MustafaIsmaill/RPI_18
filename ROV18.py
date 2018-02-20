from communication.TcpCommunication import *
from Interrupter import *
from Publisher import *
from Motion import *
from Hat import *


class ROV18:
    def __init__(self):
        # initialize tcp_communicator for communicating with QT via TCP
        ip = "10.0.1.55"
        port = 9005
        self.tcp_communicator = TcpCommunicator(ip, port, bind=True)
        self.udp_communicator = UdpCommunicator(ip,port)

        # initialize hat with default address and frequency
        hat_address = 0x40
        frequency = 50
        self.hat = Hat(hat_address, frequency)

        # adding devices to hat -- args: (device name, channel, base pwm)
        thruster_base_pwm = 305
        self.hat.addDevice("top_rear_thruster", 0, thruster_base_pwm)
        self.hat.addDevice("left_rear_thruster", 1, thruster_base_pwm)
        self.hat.addDevice("right_rear_thruster", 2, thruster_base_pwm)
        self.hat.addDevice("top_front_thruster", 3, thruster_base_pwm)
        self.hat.addDevice("left_front_thruster", 4, thruster_base_pwm)
        self.hat.addDevice("right_front_thruster", 5, thruster_base_pwm)

        # system components
        components = []

        # motion equation component -- args (hat, angle zeros)
        self.motion = Motion(self.hat, {"x": 0, "y": 0, "z": 0, "r": 0})
        components.append(self.motion)

        # publisher
        self.publisher = Publisher()

        # bind component listeners to TCP and I2C events in publisher
        for component in components:
            self.publisher.registerEventListener("TCP", component.update)
            self.publisher.registerEventListener("TCP ERROR", component.update)

        self.publisher.registerEventListener("I2C", self.motion.update)
        self.publisher.registerEventListener("I2C", self.hat.update)

        self.publisher.registerEventListener("HAT", self.hat.update)

        # self.tcp_communicator.registerCallBack(self.publisher.trigger_event)
        self.udp_communicator.registerCallBack(self.publisher.trigger_event)
        self.motion.registerCallBack(self.publisher.trigger_event)

        # create interrupter and bind to I2C event trigger callback
        self.interrupter = Interrupter(self.publisher.trigger_event, "I2C")

        # Main loop
        # self.tcp_communicator.mainLoop()
        self.udp_communicator.mainLoop()



















