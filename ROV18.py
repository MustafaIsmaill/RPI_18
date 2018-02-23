from communication.TcpCommunication import *
from Interrupter import *
from Publisher import *
from Motion import *

# import the Hat module (comment for testing)
from Hat import *

from Dummy_Hat import *


class ROV18:
    def __init__(self):
        # initialize tcp_communicator for communicating with QT via TCP

        # pi ip address (comment for testing)
        ip = "10.0.1.55"

        # local ip address (uncomment for testing)
        # ip = "0.0.0.0"

        tcpPort = 9005

        # streaming enable or disable
        streamingEnable = False

        # streaming attributes
        streamingIP = "10.0.1.54"
        streamingPort1 = "1234"
        streamingPort2 = "5678"

        # initialize tcp communicator
        self.tcp_communicator = TcpCommunicator(ip, tcpPort , streamingIP, streamingPort1, streamingPort2, streamingEnable, bind=True)

        # initialize hat with default address and frequency (comment when testing)
        hat_address = 0x40
        frequency = 50
        self.hat = Hat(hat_address, frequency)

        # initialize dummy hat for testing without the pi
        # self.hat = Dummy_Hat()

        # adding devices to hat -- args: (device name, channel, base pwm)
        thruster_base_pwm = 305
        self.hat.addDevice("top_rear_thruster", 0, thruster_base_pwm)
        self.hat.addDevice("top_front_thruster", 1, thruster_base_pwm)
        self.hat.addDevice("left_rear_thruster", 2, thruster_base_pwm)
        self.hat.addDevice("right_rear_thruster", 3, thruster_base_pwm)
        self.hat.addDevice("left_front_thruster", 4, thruster_base_pwm)
        self.hat.addDevice("right_front_thruster", 5, thruster_base_pwm)

        # list of system components
        components = []

        # motion equation component -- args (hat, angle zeros)
        self.motion = Motion(self.hat, {"x": 0, "y": 0, "z": 0, "r": 0, "up": 0, "down": 0})
        components.append(self.motion)

        # publisher
        self.publisher = Publisher()

        # bind component listeners to TCP and I2C events in publisher
        for component in components:
            self.publisher.registerEventListener("TCP", component.update)
            self.publisher.registerEventListener("TCP ERROR", component.update)

        self.publisher.registerEventListener("CLOCK", self.motion.update)
        self.publisher.registerEventListener("CLOCK", self.hat.update)

        self.publisher.registerEventListener("HAT", self.hat.update)

        self.tcp_communicator.registerCallBack(self.publisher.trigger_event)
        self.motion.registerCallBack(self.publisher.trigger_event)

        # create interrupter and bind to I2C event trigger callback
        # (when commented, pwms are only updated in the hat on change)
        # self.interrupter = Interrupter(self.publisher.trigger_event, "CLOCK")

        # Main loop
        self.tcp_communicator.mainLoop()