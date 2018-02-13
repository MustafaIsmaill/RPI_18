from Camera import *
from Lights import *
from Manipulator import *
from Motion import *
from PostOffice import *
from communication.LowLevelCommunicator import *
from communication.TcpCommunication import *
from communication.Interrupts import *
from SensorClass import *
from Sensors import *
from Hat import *
from Adafruit_PWM_Servo_Driver import PWM


class ROVMANSY:
    def __init__(self):
        ip = "0.0.0.0"
        port = 8005
        self._topcommunicator = TcpCommunicator(ip, port, bind=True)
        self._botcommunicator = I2cCommunicator()

        # ===============Hat
        pwm = PWM(0x40)
        self.hat = Hat(pwm, 50)

        # =============Components
        # identifiers must be in the form of a dict  {identifier : Base value}
        self._rovmotion = Motion(self._myhardware, {"x": 0, "y": 0, "z": 0, "r": 0, "currentmode": 0, "flip": 0})
        modules = [self._rovCamera, self._rovmotion, self._rovmanipulator, self._rovLight]

        # =============PostOffice

        self.mypostoffice = PostOffice()
        for module in modules:
            self.mypostoffice.registerEventListner("TCP", module.mail)
            self.mypostoffice.registerEventListner("TCP ERROR", module.mail)

        self.mypostoffice.registerEventListner("I2C", self._rovmotion.mail)
        self.mypostoffice.registerEventListner("I2C", self._myhardware._avrList[0].mail)

        self.mypostoffice.registerEventListner("Sensors", self._topcommunicator._send)

        self._topcommunicator.registerCallBack(self.mypostoffice.triggerEvent)

        # =============Sensors
        self._mysensors = SensorRegistry()
        self._mysensors.registerSensor(sensor)
        self._mysensors.registerCallBack(self.mypostoffice.triggerEvent)

        # =====interrupts
        self._interruptor = Interrupt()
        self._interruptor.register(23, False, self.mypostoffice.triggerEvent, "I2C")

        self._topcommunicator._mainLoop()
