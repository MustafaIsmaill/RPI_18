
class Dummy_Hat:
    def __init__(self):
        self._devices = {}
        self._devicesBaseValue = {}

    def _updatePWM(self):
        for device in self._devices:
            print("PWM updated for ", device, " with value ", int(self._devices[device]["current"]))
            self._devices[device]["previous"] = self._devices[device]["current"]

    def addDevice(self, name, channel, baseValue):
        self._devices[name] = {"channel": channel, "base": baseValue, "current": baseValue, "previous": baseValue}

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
            # print("PWM Updated")
            self._updatePWM()
