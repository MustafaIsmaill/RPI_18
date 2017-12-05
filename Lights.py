from Component import *
class Lights(Component):

    def __init__(self,hardware,identifiers):

        super().__init__(hardware,identifiers)
        self._colorList={"white":1,
                         "green":4,
                         "red":1,
                         "blue":2}

    def _changeColor(self,):
        try:
            # self._hardware.setDeviceValue("LED",self._colorList[color])
            lightsValue= self._valueMap["led1"] + self._valueMap["led2"]*2
            self._hardware.setDeviceValue("LED",lightsValue)
        except:
            print("No such color found in the LED dictionary.")

    def _setMyDevicesToDefaults(self):
        self._hardware.setDeviceValue("LED", self._hardware.getDeviceBaseValue("LED"))

    def mail(self, mailtype, mail_map):
        if mailtype == "TCP ERROR":
            self._setMyDevicesToDefaults()
        if mailtype is "TCP":
            if(super().mail(mailtype,mail_map)):
                for key in self._valueMap:
                    try:
                        self._valueMap[key]=int(self._valueMap[key])
                    except:
                        print("The Received value of the led is not Integer")
                self._changeColor()

