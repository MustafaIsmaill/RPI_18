from Component import *
import math


class Motion(Component):
    def __init__(self, hardware, identifiers):
        super().__init__(hardware, identifiers)

        self._eventCallBack = None

        # ===========CONSTANTS========
        self.PWMNORMAL = 305
        self.PWMRANGE = 165
        self.ANGLE45 = 0.785398  # 45 deg to rad
        self.ANGLE90 = 1.5708  # 90 deg to rad
        self.ANGLE225 = 3.92699  # 225 deg to rad
        self.FULL_PWM_RANGE_COEFFICIENT = self.PWMRANGE / 100.0  # PWMRANGE/100
        self.MOTORS_BASE_PWM = 305
        self.FULL_ROTATION_COEFFICIENT = 0.4 * 1.65
        self.MAXTHRUST = 0.4

        self.prev_value = self.PWMNORMAL

        # =========VARIABLES==========
        self._verticalMotors = {}
        self._horizontalMotors = {}
        self._servos = {}
        self._lights = {}

        # ========SET MOTORS TO DEFAULTS=====
        self._stopHorizontalMotors()
        self._stopVerticalMotors()
        self._setCamToNormalPosition()
        self._turnLightOff()
        self._setFromMyLocalToDevice()

    def _calculateHorizontalMotors_Mustafa(self):
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

    def _calculateHorizontalMotors_17(self):
        _x = self._valueMap['x']
        _y = self._valueMap['y']
        _r = self._valueMap['r']

        self.right_factor = ( (0.72 * _y) / 200 ) + 0.36
        self.left_factor = ( (-0.5 * _y) / 200 ) + 0.25

        theta = math.atan2(_x, _y)
        circle_factor = max(abs(math.cos(theta)), abs(math.sin(theta)))
        resultant = math.hypot(_x, _y) * circle_factor

        # alpha = 45 deg - theta
        # alpha = theta - self.ANGLE225
        alpha = self.ANGLE45 - theta
        maximum_factor = 1 / (math.cos(self.ANGLE45 - abs(theta) + (int(abs(theta) / self.ANGLE90) * self.ANGLE90)))
        RightComponent = resultant * math.cos(alpha ) * maximum_factor
        LeftComponent = resultant * math.sin(alpha ) * maximum_factor

        front_right_thruster_value = int(self.MOTORS_BASE_PWM + (LeftComponent * self.FULL_PWM_RANGE_COEFFICIENT) * self.right_factor)
        front_left_thruster_value = int(self.MOTORS_BASE_PWM - (RightComponent * self.FULL_PWM_RANGE_COEFFICIENT) * self.left_factor )
        back_right_thruster_value = int(self.MOTORS_BASE_PWM + (RightComponent * self.FULL_PWM_RANGE_COEFFICIENT) * self.right_factor)
        back_left_thruster_value = int(self.MOTORS_BASE_PWM - (LeftComponent * self.FULL_PWM_RANGE_COEFFICIENT) * self.left_factor )

        front_right_thruster_value -= _r * self.FULL_ROTATION_COEFFICIENT
        front_left_thruster_value += _r * self.FULL_ROTATION_COEFFICIENT
        back_left_thruster_value += _r * self.FULL_ROTATION_COEFFICIENT
        back_right_thruster_value -= _r * self.FULL_ROTATION_COEFFICIENT

        right_front_thruster_value = self.MAXTHRUST * (front_right_thruster_value - self.PWMNORMAL) + self.PWMNORMAL
        left_front_thruster_value = self.MAXTHRUST * (front_left_thruster_value - self.PWMNORMAL) + self.PWMNORMAL
        right_rear_thruster_value = self.MAXTHRUST * (back_right_thruster_value - self.PWMNORMAL) + self.PWMNORMAL
        left_rear_thruster_value = self.MAXTHRUST * (back_left_thruster_value - self.PWMNORMAL) + self.PWMNORMAL

        self._horizontalMotors["right_front_thruster"] = int(right_front_thruster_value)
        self._horizontalMotors["left_front_thruster"] = int(left_front_thruster_value)
        self._horizontalMotors["right_rear_thruster"] = int(right_rear_thruster_value)
        self._horizontalMotors["left_rear_thruster"] = int(left_rear_thruster_value)

    def _calculateHorizontalMotors_Local(self):
        _x = self._valueMap['x']
        _y = self._valueMap['y']
        _r = self._valueMap['r']

        if abs(_y) > abs(_x) and _y > 0:
            front_right_thruster_value = 352
            front_left_thruster_value = 239
            back_right_thruster_value = 352
            back_left_thruster_value = 239

        elif abs(_x) > abs(_y) and _y < 0:
            front_right_thruster_value = 239
            front_left_thruster_value = 352
            back_right_thruster_value = 239
            back_left_thruster_value = 352

        else:
            back_right_thruster_value = self.PWMNORMAL
            back_left_thruster_value = self.PWMNORMAL
            front_right_thruster_value = self.PWMNORMAL
            front_left_thruster_value = self.PWMNORMAL

        front_right_thruster_value -= _r * self.FULL_ROTATION_COEFFICIENT
        front_left_thruster_value += _r * self.FULL_ROTATION_COEFFICIENT
        back_left_thruster_value += _r * self.FULL_ROTATION_COEFFICIENT
        back_right_thruster_value -= _r * self.FULL_ROTATION_COEFFICIENT

        right_front_thruster_value = self.MAXTHRUST * (front_right_thruster_value - self.PWMNORMAL) + self.PWMNORMAL
        left_front_thruster_value = self.MAXTHRUST * (front_left_thruster_value - self.PWMNORMAL) + self.PWMNORMAL
        right_rear_thruster_value = self.MAXTHRUST * (back_right_thruster_value - self.PWMNORMAL) + self.PWMNORMAL
        left_rear_thruster_value = self.MAXTHRUST * (back_left_thruster_value - self.PWMNORMAL) + self.PWMNORMAL

        self._horizontalMotors["right_front_thruster"] = int(right_front_thruster_value)
        self._horizontalMotors["left_front_thruster"] = int(left_front_thruster_value)
        self._horizontalMotors["right_rear_thruster"] = int(right_rear_thruster_value)
        self._horizontalMotors["left_rear_thruster"] = int(left_rear_thruster_value)

    def _calculateVerticalMotors_NormalMode(self):
        # top_front_thruster_value = self._hardware.getDeviceValue('top_front_thruster')
        # top_rear_thruster_value = self._hardware.getDeviceValue('top_rear_thruster')
        if self._valueMap['up']:
            top_front_thruster_value = int(self.PWMNORMAL + (self._valueMap['z']*self.MAXTHRUST*(self.PWMRANGE/100)))
            top_rear_thruster_value = int(self.PWMNORMAL + (self._valueMap['z']*self.MAXTHRUST*(self.PWMRANGE/100)))
        elif self._valueMap['down']:
            top_front_thruster_value = int(self.PWMNORMAL - (self._valueMap['z']*self.MAXTHRUST*(self.PWMRANGE/100)))
            top_rear_thruster_value = int(self.PWMNORMAL - (self._valueMap['z']*self.MAXTHRUST*(self.PWMRANGE/100)))
        self._verticalMotors["top_front_thruster"] = int(top_front_thruster_value)
        self._verticalMotors["top_rear_thruster"] = int(top_rear_thruster_value)

    def _calculateVerticalMotors_HomeMode(self):
        # top_front_thruster_value = self._hardware.getDeviceValue('top_front_thruster')
        # top_rear_thruster_value = self._hardware.getDeviceValue('top_rear_thruster')
        if self._valueMap['up']:
            top_front_thruster_value = int(self.PWMNORMAL + (self._valueMap['z']*(self.PWMRANGE/100)))
            top_rear_thruster_value = int(self.PWMNORMAL + (self._valueMap['z']*(self.PWMRANGE/100)))
        elif self._valueMap['down']:
            top_front_thruster_value = int(self.PWMNORMAL - (self._valueMap['z']*(self.PWMRANGE/100)))
            top_rear_thruster_value = int(self.PWMNORMAL - (self._valueMap['z']*(self.PWMRANGE/100)))
        self._verticalMotors["top_front_thruster"] = int(top_front_thruster_value)
        self._verticalMotors["top_rear_thruster"] = int(top_rear_thruster_value)

    def _stopVerticalMotors(self):
        self._verticalMotors["top_front_thruster"] = self._hardware.getDeviceBaseValue("top_front_thruster")
        self._verticalMotors["top_rear_thruster"] = self._hardware.getDeviceBaseValue("top_rear_thruster")

    def _setCamToNormalPosition(self):
        self._servos["camera_servo"] = self._hardware.getDeviceBaseValue("camera_servo")

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

    def _turnLightOff(self):
        self._lights['light'] = 0

    def _moveCamera(self):
        camera_servo_value = self._hardware.getDeviceValue('camera_servo')

        if self._valueMap['cam_up'] and camera_servo_value <= 480:
            camera_servo_value = camera_servo_value + 20

        elif self._valueMap['cam_down'] and camera_servo_value >= 320:
            camera_servo_value = camera_servo_value - 20

        self._servos["camera_servo"] = camera_servo_value

    def _light(self):
        light_pwm_value = self._hardware.getDeviceValue('light')
        if light_pwm_value < 1800:
            light_pwm_value = light_pwm_value + 500
        else:
            light_pwm_value = 0
        self._lights["light"] = light_pwm_value

    def _setFromMyLocalToDevice(self):
        self._hardware.setDeviceValue("right_front_thruster", self._horizontalMotors["right_front_thruster"])
        self._hardware.setDeviceValue("left_front_thruster", self._horizontalMotors["left_front_thruster"])
        self._hardware.setDeviceValue("right_rear_thruster", self._horizontalMotors["right_rear_thruster"])
        self._hardware.setDeviceValue("left_rear_thruster", self._horizontalMotors["left_rear_thruster"])
        self._hardware.setDeviceValue("top_front_thruster", self._verticalMotors["top_front_thruster"])
        self._hardware.setDeviceValue("top_rear_thruster", self._verticalMotors["top_rear_thruster"])
        self._hardware.setDeviceValue("top_rear_thruster", self._verticalMotors["top_rear_thruster"])
        self._hardware.setDeviceValue("camera_servo", self._servos["camera_servo"])
        self._hardware.setDeviceValue("light", self._lights["light"])

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

            if self._valueMap['mode'] == 0:

                if self._valueMap["up"] == 1 or self._valueMap["down"] == 1:
                    print("calculating vertical motors")
                    self._calculateVerticalMotors_NormalMode()

                else:
                    self._stopVerticalMotors()

                if self._valueMap["cam_up"] == 1 or self._valueMap["cam_down"]:
                    print("moving camera")
                    self._moveCamera()

                if self._valueMap['l'] == 1:
                    print("light event")
                    self._light()

                print("calculating horizontal motors")
                self._calculateHorizontalMotors_Local()

            elif self._valueMap['mode'] == 1:

                if self._valueMap["up"] == 1 or self._valueMap["down"] == 1:
                    print("calculating vertical motors")
                    self._stopHorizontalMotors()
                    self._calculateVerticalMotors_HomeMode()

                else:
                    print("calculating horizontal motors")
                    self._stopVerticalMotors()
                    self._calculateHorizontalMotors_Local()

                if self._valueMap["cam_up"] == 1 or self._valueMap["cam_down"]:
                    print("moving camera")
                    self._moveCamera()

                if self._valueMap['l'] == 1:
                    print("light event")
                    self._light()

            self._setFromMyLocalToDevice()
            # self._printPWMValues()

            if self._eventCallBack is not None:
                self._eventCallBack("HAT")

        # PWM Clock Interrupter Event Listener (deprecated)
        # if event == "CLOCK":
        #     # print("PWM UPDATE")
        #     self._setFromMyLocalToDevice()
        #     self._eventcallback("HAT")
