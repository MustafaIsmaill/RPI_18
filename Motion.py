import math
from Component import *


class Motion(Component):
    def __init__(self, hardware, identifiers):
        super().__init__(hardware, identifiers)

        # ===========CONSTANTS========

        self._eventcallback = None

        self.PWMNORMAL = 305
        self.PWMRANGE = 124

        self.prev_value = self.PWMNORMAL

        # =========VARIABLES==========
        self._motors = {}
        self._setMyDevicesToDefaults()

    def _calculateHorizontalMotors(self):

        n = (abs(self._valueMap['x']) + abs(self._valueMap['y']) + abs(self._valueMap['r'])) / 100.0

        right_front_thruster_value = self.PWMNORMAL
        left_front_thruster_value = self.PWMNORMAL
        right_rear_thruster_value = self.PWMNORMAL
        left_rear_thruster_value = self.PWMNORMAL

        if n < 1:
            n = 1

        _x = self._valueMap['x']
        _y = self._valueMap['y']
        # _r = self._valueMap['r']*0.4
        _r = 0

        if n != 0:
            right_front_thruster_value = self.PWMNORMAL + self.PWMRANGE * (
                    float(_x / -100) + float(_y / 100)
                    + float(_r / -100)) * (1.0 / n)
            left_front_thruster_value = self.PWMNORMAL + self.PWMRANGE * (float(_x / 100)
                    + float(_y / 100) + float(_r / 100)) * (1.0 / n)
            right_rear_thruster_value = self.PWMNORMAL + self.PWMRANGE * (float(_x / 100)
                    + float(_y / 100) + float(_r / -100)) * (1.0 / n)
            left_rear_thruster_value = self.PWMNORMAL + self.PWMRANGE * (float(_x / -100)
                    + float(_y / 100) + float(_r / 100)) * (1.0 / n)

        self._motors["right_front_thruster"] = right_front_thruster_value
        self._motors["left_front_thruster"] = left_front_thruster_value
        self._motors["right_rear_thruster"] = right_rear_thruster_value
        self._motors["left_rear_thruster"] = left_rear_thruster_value

        print("right_front_thruster pwm: ", right_front_thruster_value)
        print("left_front_thruster pwm: ", left_front_thruster_value)
        print("right_rear_thruster pwm: ", right_rear_thruster_value)
        print("left_rear_thruster pwm: ", left_rear_thruster_value)

    def _calculateVerticalMotors(self):

        top_front_thruster_value = int(self.PWMNORMAL + (self._valueMap['z'] * self.PWMRANGE))
        top_rear_thruster_value = int(self.PWMNORMAL + (self._valueMap['z'] * self.PWMRANGE))

        self._motors["top_front_thruster"] = top_front_thruster_value
        self._motors["top_rear_thruster"] = top_rear_thruster_value
        print("")
        print("")

    def _setMyDevicesToDefaults(self):

        self._motors["right_front_thruster"] = self.PWMNORMAL
        self._motors["left_front_thruster"] = self.PWMNORMAL
        self._motors["right_rear_thruster"] = self.PWMNORMAL
        self._motors["left_rear_thruster"] = self.PWMNORMAL
        self._motors["top_front_thruster"] = self.PWMNORMAL
        self._motors["top_rear_thruster"] = self.PWMNORMAL

        self._hardware.setDeviceValue("right_front_thruster", self._hardware.getDeviceBaseValue("right_front_thruster"))
        self._hardware.setDeviceValue("left_front_thruster", self._hardware.getDeviceBaseValue("left_front_thruster"))
        self._hardware.setDeviceValue("right_rear_thruster", self._hardware.getDeviceBaseValue("right_rear_thruster"))
        self._hardware.setDeviceValue("left_rear_thruster", self._hardware.getDeviceBaseValue("left_rear_thruster"))
        self._hardware.setDeviceValue("top_front_thruster", self._hardware.getDeviceBaseValue("top_front_thruster"))
        self._hardware.setDeviceValue("top_rear_thruster", self._hardware.getDeviceBaseValue("top_rear_thruster"))

    def _setFromMyLocalToDevice(self):
        self._hardware.setDeviceValue("right_front_thruster", self._motors["right_front_thruster"])
        self._hardware.setDeviceValue("left_front_thruster", self._motors["left_front_thruster"])
        self._hardware.setDeviceValue("right_rear_thruster", self._motors["right_rear_thruster"])
        self._hardware.setDeviceValue("left_rear_thruster", self._motors["left_rear_thruster"])
        self._hardware.setDeviceValue("top_front_thruster", self._motors["top_front_thruster"])
        self._hardware.setDeviceValue("top_rear_thruster", self._motors["top_rear_thruster"])

    def registerCallBack(self, callback):
        self._eventcallback = callback

    def update(self, event, mail_map=None):

        if event == "TCP ERROR":
            self._setMyDevicesToDefaults()

        if event is "TCP":
            self._valueMap = mail_map
            for key in self._valueMap:
                self._valueMap[key] = float(self._valueMap[key])
            print("TCP Event")
            print("calculating horizontal motors")
            self._calculateHorizontalMotors()
            # self._setFromMyLocalToDevice()

        if event == "CLOCK":
            #print("PWM UPDATE")
            self._setFromMyLocalToDevice()
            self._eventcallback("HAT")



