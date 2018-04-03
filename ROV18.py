from communication.TcpCommunication import *
from Lift_Bag_Communicator import *
from Interrupter import *
from Publisher import *
from Motion import *
# from Sensor import *

# import the Hat module (comment for testing)
from Hat import *

# from Dummy_Hat import *
from Dummy_Interrupter import *

class ROV18:
    def __init__(self):
        # initialize tcp_communicator for communicating with QT via TCP

        # pi ip address (comment for testing)
        ip = "10.0.1.55"

        # local ip address (uncomment for testing)
        # ip = "0.0.0.0"

        tcpPort = 9005

        # streaming enable or disable
        streamingEnable = True

        # streaming attributes
        streamingIP = "10.0.1.54"
        streamingPort1 = "1234"
        streamingPort2 = "5678"
        streamingPort3 = "4321"
        streamingPort4 = "8765"

        # initialize tcp communicator
        self.tcp_communicator = TcpCommunicator(ip, tcpPort , streamingIP, streamingPort1, streamingPort2, streamingPort3, streamingPort4,  streamingEnable, bind=True)

        # initialize hat with default address and frequency (comment when testing)
        hat_address = 0x40
        frequency = 50
        self.hat = Hat(hat_address, frequency)
        # self.pressureSensor = Sensor()
        self.liftBagCommunicator = Lift_Bag_Communicator({"x": 0, "y": 0, "z": 0, "r": 0, "up": 0, "down": 0, "l": 0, "bag": 0})

        # initialize dummy hat for testing without the pi
        # self.hat = Dummy_Hat()

        thruster_base_pwm = 305
        camera_base_pwm = 400

        # adding devices to hat -- args: (device name, channel, base pwm)
        self.hat.addDevice("top_rear_thruster", 0, thruster_base_pwm)
        self.hat.addDevice("top_front_thruster", 7, thruster_base_pwm)
        self.hat.addDevice("left_rear_thruster", 11, thruster_base_pwm)
        self.hat.addDevice("right_rear_thruster", 5, thruster_base_pwm)
        self.hat.addDevice("left_front_thruster", 9, thruster_base_pwm)
        self.hat.addDevice("right_front_thruster", 3, thruster_base_pwm)
        self.hat.addDevice("camera_servo", 15, camera_base_pwm)
        self.hat.addDevice("light", 13, 0)

        # list of system components
        components = []

        # motion equation component -- args (hat, angle zeros)
        self.motion = Motion(self.hat, {"x": 0, "y": 0, "z": 0, "r": 0, "up": 0, "down": 0, "l": 0, "bag": 0})
        components.append(self.liftBagCommunicator)
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
        self.publisher.registerEventListener("SENSOR", self.tcp_communicator.sendFeedback)
        self.publisher.registerEventListener("BAG", self.tcp_communicator.sendToLiftBag)

        self.tcp_communicator.registerCallBack(self.publisher.trigger_event)
        self.motion.registerCallBack(self.publisher.trigger_event)
        self.liftBagCommunicator.registerCallBack(self.publisher.trigger_event)
        # self.pressureSensor.registerCallBack(self.publisher.trigger_event)

        # create interrupter and bind to I2C event trigger callback
        # (when commented, pwms are only updated in the hat on change)
        # self.interrupter = Interrupter(self.publisher.trigger_event, "SENSOR")
        self.interrupter = Dummy_Interrupter(self.publisher.trigger_event, "SENSOR", 'dummy data')

        # Main loop
        self.tcp_communicator.mainLoop()