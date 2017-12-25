from Camera import *
from Hardware import *
from Lights import *
from Manipulator import *
from Motion import *
from PostOffice import *
from communication.LowLevelCommunicator import *
from communication.TcpCommunication import *
from communication.Interrupts import *
from SensorClass import *
from Sensors import *


class ROVREGIONAL:
    def __init__(self):
        ip = "0.0.0.0"
        port = 8005
        self._topcommunicator = TcpCommunicator(ip, port, bind=True)
        self._botcommunicator = I2cCommunicator()
        self._myhardware = Hardware(self._botcommunicator)
        # ===============AVR
        self._Avr1address = 6
        # self._Avr2address = 7

        self._myhardware.addAVR(self._Avr1address)
        # self._myhardware.addAVR(self._Avr2address)

        # ===============Devices
        motorsbasepwm = 1440
        zero = 0
        cameraservobase = 1500
        RGBwhite = 1
        # The last argument is the number of bytes for each device
        self._myhardware._avrList[0].addDevice("Up_Back_Thruster", motorsbasepwm, 2)
        self._myhardware._avrList[0].addDevice("Back_Left_Thruster", motorsbasepwm, 2)
        self._myhardware._avrList[0].addDevice("Back_Right_Thruster", motorsbasepwm, 2)
        self._myhardware._avrList[0].addDevice("Front_Left_Thruster", motorsbasepwm, 2)
        self._myhardware._avrList[0].addDevice("Up_Front_Thruster", motorsbasepwm, 2)
        self._myhardware._avrList[0].addDevice("Front_Right_Thruster", motorsbasepwm, 2)
        self._myhardware._avrList[0].addDevice("Camera_Servo", cameraservobase, 2)
        self._myhardware._avrList[0].addDevice("DC", zero, 1)
        self._myhardware._avrList[0].addDevice("LED", zero, 1)

        # =============Components
        # identifiers must be in the form of a dict  {identifier : Base value}
        self._rovmanipulator = Manipulator(self._myhardware, {"grip": 0})
        self._rovLight = Lights(self._myhardware, {"led1": 0, "led2": 0})
        self._rovCamera = Camera(self._myhardware, {"cam": 0})
        self._rovmotion = Motion(self._myhardware, {"x": 0, "y": 0, "z": 0, "r": 0, "currentmode": 0, "flip": 0})
        modules = [self._rovCamera, self._rovmotion, self._rovmanipulator, self._rovLight]

        # =============PostOffcie

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
