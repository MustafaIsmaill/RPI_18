from Component import *
class Manipulator(Component):
    def    __init__(self,hardware,identifier_defaultvalues):
        super().__init__(hardware,identifier_defaultvalues)
        # self._interuptor=interuptor
        # self._interuptor.register()
        #========constants

        self.LEFT = 0b00000101
        self.RIGHT = 0b00000110
        self.NOTHING = 0

        self.HALFCYCLEFLAG=1
        self.THREECYCLESFLAG=2



    def _foundGrip(self, value):

        # Direction
        if value > 0:
            self._hardware.setDeviceValue("DC",self.LEFT)
        elif value < 0:
            self._hardware.setDeviceValue("DC",self.RIGHT)
        else:
            self._hardware.setDeviceValue("DC",self.NOTHING)
        # Cycles
        # if value in [0.5, -0.5]:
        #     self._hardware.setDeviceValue("Cycle_Flag",self.HALFCYCLEFLAG)
        # elif value in [3.5, -3.5]:
        #     self._hardware.setDeviceValue("Cycle_Flag",self.THREECYCLESFLAG)
        # else:
        #     self._hardware.setDeviceValue("Cycle_Flag",self.NOTHING)

    def _readAndHandleResponse(self,response):
        myCycleFlag=self._hardware.getDeviceValue("Cycle_Flag")
        if (response == myCycleFlag) and  (myCycleFlag is not 0):  # Cycle Complete
            self._hardware.setDeviceValue("DC",self.NOTHING)
            self._hardware.setDeviceValue("Cycle_Flag",self.NOTHING)

    def _setMyDevicesToDefaults(self):
        self._hardware.setDeviceValue("DC", self._hardware.getDeviceBaseValue("DC"))
        self._hardware.setDeviceValue("Cycle_Flag", self._hardware.getDeviceBaseValue("Cycle_Flag"))

    def mail(self, event, mail_map=None):
        if event == "TCP ERROR":
            self._setMyDevicesToDefaults()

        if event=="TCP":
            if(super().mail(event,mail_map)):
                for key in self._valueMap:
                    self._valueMap[key]=float(self._valueMap[key])
                gripValue=self._valueMap["grip"]
                self._foundGrip(gripValue)
        elif event=="I2C":
            avr=self._hardware.getAvrContainingDevice("DC")
            # print ("I am GRIPPER,Suppose to read from avr with address ",avr._address) #TODO REMOVE
            #response=int(avr._communicator.readFrom(avr._address)) #TODO:ACTIVATE
            # print ("Assumed the response was = 0")
            response=0              #TODO REMOVE
            self._readAndHandleResponse(response)
