from Camera import *
from Hardware import *
from Lights import *
from Manipulator import *
from Motion import *
from PostOffice import *
from communication.LowLevelCommunicator import *
from communication.TcpCommunication import *
# from communication.Interrupts import *
from SensorClass import *
from Sensors import *


class ROVMANSY:
    def __init__(self):
        ip = "0.0.0.0"
        port = 8082
        self.highLevelCommunicator = TcpCommunicator(ip, port, bind=True)
        self.lowLevelCommunicator = I2cCommunicator() #sendTo(), readFrom()
        self.hardwareSensors = Hardware(self.lowLevelCommunicator)
        self.avrAddress = 1
        self.hardwareSensors.addAVR(self.avrAddress)
        self.highLevelCommunicator._mainLoop()




