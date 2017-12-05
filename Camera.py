from Component import *
class Camera(Component):
    def __init__(self,hardware,identifiers):
        super().__init__(hardware,identifiers)
        self._minAngle=-45
        self._maxAngle=45
        self._minServoPwm=1000
        self._maxServoPwm=2000
        #========Constants===========
    def calculateNewValues(self):
        angle = -1 * self._valueMap["cam"]
        angleRange = self._maxAngle - self._minAngle
        pwmRange = self._maxServoPwm - self._minServoPwm
        value = (((angle - self._minAngle) / (angleRange)) * (pwmRange)) + self._minServoPwm
        self._hardware.setDeviceValue("Camera_Servo", value)

    def _setMyDevicesToDefaults(self):
        self._hardware.setDeviceValue("Camera_Servo", self._hardware.getDeviceBaseValue("Camera_Servo"))

    def mail(self,mailtype,mail_map):
        if mailtype == "TCP ERROR":
            self._setMyDevicesToDefaults()

        if super().mail(mailtype,mail_map):
            for key in (self._valueMap):
                self._valueMap[key]=float(self._valueMap[key])
            self.calculateNewValues()
            #interpolation using the formulae           angle-minangle             value-minpwm
            #                                           -----------------     =    -------------
            #                                           maxangle-minangle          maxpwm-minpwm

