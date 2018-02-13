from drivers.Adafruit_PWM_Servo_Driver import PWM


class Hat:
    def __init__(self, address, frequency):
        self._address = address
        self._devices = {}
        self._devicesBaseValue = {}
        print("address: ", address)
        self._hat = PWM(0x40, debug=True)
        self._hat.setPWMFreq(frequency)

    def _setPWM(self, channel, value):
        self._hat.setPWM(channel,0,value)

    def _setAllPWM(self, value):
        self._hat.setAllPWM(0, value)

    def _updatePWM(self):
        for device in self._devices:
            self._setPWM(self._devices[device]["channel"],self._devices[device]["current"])
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
        if event_name == "I2C":
            self._updatePWM()
