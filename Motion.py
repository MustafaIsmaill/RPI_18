import math
from Component import *


class Motion(Component):
    def __init__(self, hardware, identifiers):
        super().__init__(hardware, identifiers)

        # ===========CONSTANTS========
        self.ANGLE45 = 0.785398  # 45 deg to rad
        self.ANGLE90 = 1.5708  # 90 deg to rad
        self.FULL_PWM_RANGE_COEFFICIENT = 8.1  # self.PWMRANGE/10
        self.MOTORS_BASE_PWM = self._hardware.getDeviceBaseValue("right_front_thruster")
        self.FULL_ROTATION_COEFFICIENT = 0.4 * 8.1
        self.MAXIMUMPWMCHANGE = 200
        self.PWMNORMAL = 305
        self.PWMRANGE = 330
        self.SWORDFISHCOEFFICIENT = 0.25
        self.RETURNCOEFFICIENT = 0.25

        # =========VARIABLES==========
        self._futureStepsForSuddenChange = {"right_front_thruster": [None, 0], "left_front_thruster": [None, 0],
                                            "right_rear_thruster": [None, 0], "left_rear_thruster": [None, 0],
                                            "top_front_thruster": [None, 0], "top_rear_thruster": [None, 0]}
        self._motors = {}
        self._setMyDevicesToDefaults()

    def _calculateHorizontalMotors(self):
        theta = math.atan2(self._valueMap['x'], self._valueMap['y'])
        circle_factor = max(abs(math.cos(theta)), abs(math.sin(theta)))
        resultant = math.hypot(self._valueMap['x'], self._valueMap['y']) * circle_factor

        # alfa = 45 deg - theta
        alfa = self.ANGLE45 - theta
        maximum_factor = 1 / (math.cos(self.ANGLE45 - abs(theta) + (int(abs(theta) / self.ANGLE90) * self.ANGLE90)))
        RightComponent = resultant * math.cos(alfa) * maximum_factor
        LeftComponent = resultant * math.sin(alfa) * maximum_factor

        right_front_thruster_value = int(self.MOTORS_BASE_PWM + (LeftComponent * self.FULL_PWM_RANGE_COEFFICIENT))
        left_front_thruster_value = int(self.MOTORS_BASE_PWM + (RightComponent * self.FULL_PWM_RANGE_COEFFICIENT))
        right_rear_thruster_value = int(self.MOTORS_BASE_PWM + (RightComponent * self.FULL_PWM_RANGE_COEFFICIENT))
        left_rear_thruster_value = int(self.MOTORS_BASE_PWM + (LeftComponent * self.FULL_PWM_RANGE_COEFFICIENT))

        right_front_thruster_value += self._valueMap['r'] * self.FULL_ROTATION_COEFFICIENT
        left_front_thruster_value -= self._valueMap['r'] * self.FULL_ROTATION_COEFFICIENT

        if (self._valueMap['currentmode'] > 0):
            r = self._valueMap['r']
            pwm_difference = min(
                self.sign(r) * (self.PWMNORMAL + (self.sign(r) * self.PWMRANGE) - right_front_thruster_value),
                self.sign(r) * (- self.PWMNORMAL + (self.sign(r) * self.PWMRANGE) + left_front_thruster_value))
            pwm_difference_normalized = self.normalize(pwm_difference)

            right_front_thruster_value -= self.sign(RightComponent) * pwm_difference_normalized
            left_front_thruster_value -= self.sign(RightComponent) * pwm_difference_normalized
            left_rear_thruster_value -= self.sign(RightComponent) * pwm_difference_normalized
            right_rear_thruster_value -= self.sign(RightComponent) * pwm_difference_normalized

        self._motors["right_front_thruster"] = right_front_thruster_value
        self._motors["left_front_thruster"] = left_front_thruster_value
        self._motors["right_rear_thruster"] = right_rear_thruster_value
        self._motors["left_rear_thruster"] = left_rear_thruster_value

    def normalize(self, x):
        if (x < 0):
            return -x
        else:
            return 0

    def sign(self, x):
        if (x < 0):
            return -1
        else:
            return 1

    def _inverse(self, pwm):
        print("PWM: %d Inverse: %d" % (pwm, 2 * self.PWMNORMAL - pwm))
        return 2 * self.PWMNORMAL - pwm

    def _calculateVerticalMotors(self):
        top_front_thruster_value = int(self.MOTORS_BASE_PWM + (self._valueMap['z'] * self.FULL_PWM_RANGE_COEFFICIENT))
        top_rear_thruster_value = int(self.MOTORS_BASE_PWM + (self._valueMap['z'] * self.FULL_PWM_RANGE_COEFFICIENT))

        self._motors["top_front_thruster"] = top_front_thruster_value
        self._motors["top_rear_thruster"] = top_rear_thruster_value

    def _limit(self):
        if (self._valueMap['currentmode'] == 0):
            self.limitations_normal_mode()
        elif (self._valueMap['currentmode'] == 1):
            self.limitations_swordfish_mode()
        elif (self._valueMap['currentmode'] == 2):
            self.limitations_return_mode()
        return

    def limitations_normal_mode(self):
        self._motors["right_front_thruster"] = 0.5 * (
                self._motors["right_front_thruster"] - self.PWMNORMAL) + self.PWMNORMAL
        self._motors["left_front_thruster"] = 0.5 * (
                self._motors["left_front_thruster"] - self.PWMNORMAL) + self.PWMNORMAL
        self._motors["right_rear_thruster"] = 0.5 * (
                self._motors["right_rear_thruster"] - self.PWMNORMAL) + self.PWMNORMAL
        self._motors["left_rear_thruster"] = 0.5 * (
                self._motors["left_rear_thruster"] - self.PWMNORMAL) + self.PWMNORMAL
        self._motors["top_front_thruster"] = 0.5 * (self._motors["top_front_thruster"] - self.PWMNORMAL) + self.PWMNORMAL
        self._motors["top_rear_thruster"] = 0.5 * (self._motors["top_rear_thruster"] - self.PWMNORMAL) + self.PWMNORMAL
        return

    def limitations_swordfish_mode(self):
        Zsteps = (self._motors["top_front_thruster"] - self.PWMNORMAL) * self.SWORDFISHCOEFFICIENT
        Hsteps = (self.PWMRANGE - abs(Zsteps)) * ((self._motors["left_rear_thruster"] - self.PWMNORMAL) / self.PWMRANGE)
        self._motors["top_front_thruster"] = self.PWMNORMAL + Zsteps
        self._motors["top_rear_thruster"] = self.PWMNORMAL + Zsteps
        self._motors["right_rear_thruster"] = self.PWMNORMAL + Hsteps
        self._motors["left_rear_thruster"] = self.PWMNORMAL + Hsteps
        return

    def limitations_return_mode(self):
        Hsteps = (self._motors["right_rear_thruster"] - self.PWMNORMAL) * self.RETURNCOEFFICIENT
        Zsteps = (self._motors["top_front_thruster"] - self.PWMNORMAL) * 0.75
        self._motors["top_front_thruster"] = self.PWMNORMAL + Zsteps
        self._motors["top_rear_thruster"] = self.PWMNORMAL + Zsteps
        self._motors["right_rear_thruster"] = self.PWMNORMAL + Hsteps
        self._motors["left_rear_thruster"] = self.PWMNORMAL + Hsteps
        return

    def _checkForZeroCrossing(self, previousPwm, currentPwm):
        PWMZERO = self.PWMNORMAL
        if ((previousPwm - PWMZERO) * (currentPwm - PWMZERO) < 0):
            return True
        else:
            return False

    def _zeroCrossing(self, previousPwm, currentPwm, motorname):
        zeroCrossing = self._checkForZeroCrossing(previousPwm, currentPwm)
        NUMBER_OF_ZERO_CYCLES = 3  # how many times we send pwmnormal to the avr when zero crossing occurs.

        if (zeroCrossing):
            print("Zero Crossing Occured from ", motorname, " previous: ", previousPwm, " target: ", currentPwm)
            self._futureStepsForSuddenChange[motorname] = [currentPwm, NUMBER_OF_ZERO_CYCLES]
            self._motors[motorname] = self.PWMNORMAL

    def _checkForMaximumDifference(self, previousPwm, currentPwm):
        MAXIMUMDIFFERENCE = self.MAXIMUMPWMCHANGE
        difference = abs(currentPwm - previousPwm)
        if difference > MAXIMUMDIFFERENCE:
            return True
        else:
            return False

    def _setMyDevicesToDefaults(self):

        # self._motors["right_front_thruster"]=  self._hardware.getDeviceBaseValue("right_front_thruster")
        # self._motors["left_front_thruster"]=   self._hardware.getDeviceBaseValue("left_front_thruster")
        # self._motors["right_rear_thruster"]=   self._hardware.getDeviceBaseValue("right_rear_thruster")
        # self._motors["left_rear_thruster"]=    self._hardware.getDeviceBaseValue("left_rear_thruster")
        # self._motors["top_front_thruster"] =    self._hardware.getDeviceBaseValue("top_front_thruster")
        # self._motors["top_rear_thruster"]  =    self._hardware.getDeviceBaseValue("top_rear_thruster")
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
        # print("right_front_thruster pwm: ", self._motors["right_front_thruster"])
        # print("left_front_thruster pwm: ", self._motors["left_front_thruster"])
        # print("right_rear_thruster pwm: ", self._motors["right_rear_thruster"])
        # print("left_rear_thruster pwm: ", self._motors["left_rear_thruster"])
        # print("top_front_thruster pwm: ", self._motors["top_front_thruster"])
        # print("top_rear_thruster pwm: ", self._motors["top_rear_thruster"])

        self._hardware.setDeviceValue("right_front_thruster", self._motors["right_front_thruster"])
        self._hardware.setDeviceValue("left_front_thruster", self._motors["left_front_thruster"])
        self._hardware.setDeviceValue("right_rear_thruster", self._motors["right_rear_thruster"])
        self._hardware.setDeviceValue("left_rear_thruster", self._motors["left_rear_thruster"])
        self._hardware.setDeviceValue("top_front_thruster", self._motors["top_front_thruster"])
        self._hardware.setDeviceValue("top_rear_thruster", self._motors["top_rear_thruster"])

    def update(self, event, mail_map=None):
        if event == "TCP ERROR":
            self._setMyDevicesToDefaults()
        if event is "TCP":

            print("TCP Event")
            if super().mail(event, mail_map):
                # change values to floats
                for key in self._valueMap:
                    self._valueMap[key] = float(self._valueMap[key])

                if self._valueMap["currentmode"] > 0:
                    self._valueMap["x"] = 0

                self._calculateHorizontalMotors()
                self._calculateVerticalMotors()
                self._limit()

                self._hardware.setDeviceValue("right_front_thruster", self._motors["right_front_thruster"])
                self._hardware.setDeviceValue("left_front_thruster", (self._motors["left_front_thruster"]))
                self._hardware.setDeviceValue("right_rear_thruster", self._motors["right_rear_thruster"])
                self._hardware.setDeviceValue("left_rear_thruster", self._inverse(self._motors["left_rear_thruster"]))
                self._hardware.setDeviceValue("top_front_thruster", self._motors["top_front_thruster"])
                self._hardware.setDeviceValue("top_rear_thruster", (self._motors["top_rear_thruster"]))

                print(self._hardware.getDeviceValue("right_front_thruster"))
                print(self._hardware.getDeviceValue("left_front_thruster"))
                print(self._hardware.getDeviceValue("right_rear_thruster"))
                print(self._hardware.getDeviceValue("left_rear_thruster"))
                print(self._hardware.getDeviceValue("top_front_thruster"))
                print(self._hardware.getDeviceValue("top_rear_thruster"))

        if event == "I2C":
            self._setFromMyLocalToDevice()
