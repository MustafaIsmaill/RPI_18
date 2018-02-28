# Import the PCA9685 module.
import Adafruit_PCA9685


class Hat:
    def __init__(self, address, frequency):
        self._address = address
        self._devices = {}
        self._devicesBaseValue = {}
        print("Hat address: ", address)
        self._hat = Adafruit_PCA9685.PCA9685()
        self._hat.set_pwm_freq(frequency)

    def _setPWM(self, channel, value):
        self._hat.set_pwm(channel,0,int(value))

#    def _setAllPWM(self, value):
#        self._hat.setAllPWM(0, value)

    def _updatePWM(self):
        for device in self._devices:
            self._hat.set_pwm(self._devices[device]["channel"],0,int(self._devices[device]["current"]))
            self._devices[device]["previous"] = self._devices[device]["current"]

    def addDevice(self, name, channel, baseValue):
        self._devices[name] = {"channel": channel, "base": baseValue, "current": baseValue, "previous": baseValue}
        self._hat.set_pwm(channel, 0, baseValue)

    def getDeviceBaseValue(self, deviceName):
        for device in self._devices:
            if device == deviceName:
                return self._devices[device]["base"]

    def getDeviceValue(self, deviceName):
        for device in self._devices:
            if device == deviceName:
                return self._devices[device]["current"]

    def getDevicePreviousValue(self, deviceName):
        for device in self._devices:
            if device == deviceName:
                return self._devices[device]["previous"]

    def setDeviceValue(self, deviceName, value):
        for device in self._devices:
            if device == deviceName:
                self._devices[device]["current"] = value

    def update(self, event_name, data=None):
        if event_name == "HAT":
            # print("Sent PWM")
            self._updatePWM()
