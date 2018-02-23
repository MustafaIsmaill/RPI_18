from Component import *


class Motion(Component):
    def __init__(self, hardware, identifiers):
        super().__init__(hardware, identifiers)

        self._eventCallBack = None

        # ===========CONSTANTS========
        self.PWMNORMAL = 305
        self.PWMRANGE = 124

        self.prev_value = self.PWMNORMAL

        # =========VARIABLES==========
        self._verticalMotors = {}
        self._horizontalMotors = {}

        # ========SET MOTORS TO DEFAULTS=====
        self._stopHorizontalMotors()
        self._stopVerticalMotors()
        self._setFromMyLocalToDevice()

    def _calculateHorizontalMotors(self):
        _x = self._valueMap['x']
        _y = self._valueMap['y']
        _r = self._valueMap['r'] * 0.4

        n = (abs(_x) + abs(_y)) / 100.0
        # n = (abs(self._valueMap['x']) + abs(self._valueMap['y']) + abs(self._valueMap['r'])) / 100.0

        if n < 1:
            n = 1

        right_front_thruster_value = self.PWMNORMAL + self.PWMRANGE * (
                float(_x / -100) + float(_y / 100) + float(_r / -100)) * (1.0 / n)
        left_front_thruster_value = self.PWMNORMAL + self.PWMRANGE * (float(_x / 100)
                                                                      + float(_y / 100) + float(_r / 100)) * (1.0 / n)
        right_rear_thruster_value = self.PWMNORMAL + self.PWMRANGE * (float(_x / 100)
                                                                      + float(_y / 100) + float(_r / -100)) * (1.0 / n)
        left_rear_thruster_value = self.PWMNORMAL + self.PWMRANGE * (float(_x / -100)
                                                                     + float(_y / 100) + float(_r / 100)) * (1.0 / n)

        self._horizontalMotors["right_front_thruster"] = int(right_front_thruster_value)
        self._horizontalMotors["left_front_thruster"] = int(left_front_thruster_value)
        self._horizontalMotors["right_rear_thruster"] = int(right_rear_thruster_value)
        self._horizontalMotors["left_rear_thruster"] = int(left_rear_thruster_value)

    def _calculateVerticalMotors(self):
        if self._valueMap['up']:
            top_front_thruster_value = int(self.PWMNORMAL + (self._valueMap['z'] * (self.PWMRANGE/100)))
            top_rear_thruster_value = int(self.PWMNORMAL + (self._valueMap['z'] * (self.PWMRANGE/100)))
        elif self._valueMap['down']:
            top_front_thruster_value = int(self.PWMNORMAL - (self._valueMap['z'] * (self.PWMRANGE/100)))
            top_rear_thruster_value = int(self.PWMNORMAL - (self._valueMap['z'] * (self.PWMRANGE/100)))
        self._verticalMotors["top_front_thruster"] = int(top_front_thruster_value)
        self._verticalMotors["top_rear_thruster"] = int(top_rear_thruster_value)

    def _stopVerticalMotors(self):
        self._verticalMotors["top_front_thruster"] = self._hardware.getDeviceBaseValue("top_front_thruster")
        self._verticalMotors["top_rear_thruster"] = self._hardware.getDeviceBaseValue("top_rear_thruster")

    def _stopHorizontalMotors(self):
        self._horizontalMotors["right_front_thruster"] = self._hardware.getDeviceBaseValue("right_front_thruster")
        self._horizontalMotors["left_front_thruster"] = self._hardware.getDeviceBaseValue("left_front_thruster")
        self._horizontalMotors["right_rear_thruster"] = self._hardware.getDeviceBaseValue("right_rear_thruster")
        self._horizontalMotors["left_rear_thruster"] = self._hardware.getDeviceBaseValue("left_rear_thruster")

    def _printPWMValues(self):
        for motor in self._horizontalMotors:
            print(motor, " pwm: ", self._horizontalMotors[motor])
        for motor in self._verticalMotors:
            print(motor, " pwm: ", self._verticalMotors[motor])

    def _setFromMyLocalToDevice(self):
        self._hardware.setDeviceValue("right_front_thruster", self._horizontalMotors["right_front_thruster"])
        self._hardware.setDeviceValue("left_front_thruster", self._horizontalMotors["left_front_thruster"])
        self._hardware.setDeviceValue("right_rear_thruster", self._horizontalMotors["right_rear_thruster"])
        self._hardware.setDeviceValue("left_rear_thruster", self._horizontalMotors["left_rear_thruster"])
        self._hardware.setDeviceValue("top_front_thruster", self._verticalMotors["top_front_thruster"])
        self._hardware.setDeviceValue("top_rear_thruster", self._verticalMotors["top_rear_thruster"])

    def registerCallBack(self, callback):
        self._eventCallBack = callback

    def update(self, event, mail_map=None):

        if event == "TCP ERROR":
            self._stopHorizontalMotors()
            self._stopVerticalMotors()
            self._setFromMyLocalToDevice()
            self._printPWMValues()


        if event is "TCP":
            self._valueMap = mail_map

            for key in self._valueMap:
                self._valueMap[key] = float(self._valueMap[key])

            print("TCP Event")

            if self._valueMap["up"] == 1 or self._valueMap["down"] == 1:
                print("calculating vertical motors")
                self._stopHorizontalMotors()
                self._calculateVerticalMotors()
            else:
                print("calculating horizontal motors")
                self._stopVerticalMotors()
                self._calculateHorizontalMotors()

            self._setFromMyLocalToDevice()
            # self._printPWMValues()

            if self._eventCallBack is not None:
                self._eventCallBack("HAT")

        # PWM Clock Interrupter Event Listener (deprecated)
        # if event == "CLOCK":
        #     # print("PWM UPDATE")
        #     self._setFromMyLocalToDevice()
        #     self._eventcallback("HAT")
