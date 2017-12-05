import math
from Component import *
class Motion(Component):
    def __init__(self,hardware,identifiers):
        super().__init__(hardware,identifiers)

        # self._functionMap={
        #     "normal":self.limitations_normal_mode(),
        #     "swordfish":self.limitations_swordfish_mode(),
        #     "return":self.limitations_return_mode()}

        #===========CONSTANTS========
        self.ANGLE45 = 0.785398  # 45 deg to rad
        self.ANGLE90 = 1.5708    # 90 deg to rad
        self.FULL_PWM_RANGE_COEFFICIENT=8.1 #self.PWMRANGE/10
        self.MOTORS_BASE_PWM = self._hardware.getDeviceBaseValue("Front_Right_Thruster")
        self.FULL_ROTATION_COEFFICIENT=0.4*8.1
        self.MAXIMUMPWMCHANGE=200
        self.PWMNORMAL=1440
        self.PWMRANGE=810
        self.SWORDFISHCOEFFICIENT=0.25
        self.RETURNCOEFFICIENT=0.25
        #=========VARIABLES==========
        self._futureStepsForSuddenChange={"Front_Right_Thruster":[None,0],"Front_Left_Thruster":[None,0],
                                         "Back_Right_Thruster":[None,0],"Back_Left_Thruster":[None,0],
                                         "Up_Front_Thruster":[None,0],"Up_Back_Thruster":[None,0]}
        self._motors={}
        self._setMyDevicesToDefaults()

    def _calculateHorizontalMotors(self):
        theta = math.atan2(self._valueMap['x'], self._valueMap['y'])
        circle_factor = max(abs(math.cos(theta)),abs(math.sin(theta)))
        resultant = math.hypot(self._valueMap['x'], self._valueMap['y']) * circle_factor

        # alfa = 45 deg - theta
        alfa = self.ANGLE45 - theta
        maximum_factor = 1 / (math.cos(self.ANGLE45 - abs(theta) + (int(abs(theta) / self.ANGLE90) * self.ANGLE90)))
        RightComponent = resultant * math.cos(alfa) * maximum_factor
        LeftComponent  = resultant * math.sin(alfa) * maximum_factor

        front_right_thruster_value = int(self.MOTORS_BASE_PWM + (LeftComponent * self.FULL_PWM_RANGE_COEFFICIENT))
        front_left_thruster_value  = int(self.MOTORS_BASE_PWM + (RightComponent * self.FULL_PWM_RANGE_COEFFICIENT))
        back_right_thruster_value  = int(self.MOTORS_BASE_PWM + (RightComponent * self.FULL_PWM_RANGE_COEFFICIENT))
        back_left_thruster_value   = int(self.MOTORS_BASE_PWM + (LeftComponent * self.FULL_PWM_RANGE_COEFFICIENT))

        front_right_thruster_value += self._valueMap['r'] * self.FULL_ROTATION_COEFFICIENT
        front_left_thruster_value  -= self._valueMap['r'] * self.FULL_ROTATION_COEFFICIENT

        if (self._valueMap['currentmode'] > 0):
            r=self._valueMap['r']
            pwm_difference = min( self.sign(r) * (self.PWMNORMAL + ( self.sign(r) * self.PWMRANGE) - front_right_thruster_value), self.sign(r) * ( - self.PWMNORMAL + ( self.sign(r) * self.PWMRANGE) + front_left_thruster_value) )
            pwm_difference_normalized = self.normalize(pwm_difference)

            front_right_thruster_value -= self.sign(RightComponent) * pwm_difference_normalized
            front_left_thruster_value  -= self.sign(RightComponent) * pwm_difference_normalized
            back_left_thruster_value   -= self.sign(RightComponent) * pwm_difference_normalized
            back_right_thruster_value  -= self.sign(RightComponent) * pwm_difference_normalized

        self._motors["Front_Right_Thruster"]= front_right_thruster_value
        self._motors["Front_Left_Thruster"]= front_left_thruster_value
        self._motors["Back_Right_Thruster"]= back_right_thruster_value
        self._motors["Back_Left_Thruster"]= back_left_thruster_value

    def normalize(self,x):
        if ( x < 0 ):
            return -x
        else:
            return 0

    def sign(self,x):
        if ( x < 0 ):
            return -1
        else:
            return 1

    def _inverse(self, pwm):
        print("PWM: %d Inverse: %d" % (pwm, 2*self.PWMNORMAL - pwm))
        return 2 * self.PWMNORMAL - pwm

    def _calculateVerticalMotors(self):
        up_front_thruster_value = int(self.MOTORS_BASE_PWM + (self._valueMap['z'] * self.FULL_PWM_RANGE_COEFFICIENT))
        up_back_thruster_value  = int(self.MOTORS_BASE_PWM + (self._valueMap['z'] * self.FULL_PWM_RANGE_COEFFICIENT))

        self._motors["Up_Front_Thruster"]=up_front_thruster_value
        self._motors["Up_Back_Thruster"]=up_back_thruster_value

    def _limit(self):
        if (self._valueMap['currentmode'] == 0):
            self.limitations_normal_mode()
        elif (self._valueMap['currentmode'] == 1):
            self.limitations_swordfish_mode()
        elif (self._valueMap['currentmode'] == 2):
            self.limitations_return_mode()
        return

    def limitations_normal_mode(self):
        self._motors["Front_Right_Thruster"]=0.5 * (self._motors["Front_Right_Thruster"]-self.PWMNORMAL) + self.PWMNORMAL
        self._motors["Front_Left_Thruster"]=0.5 * (self._motors["Front_Left_Thruster"]-self.PWMNORMAL) + self.PWMNORMAL
        self._motors["Back_Right_Thruster"]=0.5 * (self._motors["Back_Right_Thruster"]-self.PWMNORMAL) + self.PWMNORMAL
        self._motors["Back_Left_Thruster"]=0.5 * (self._motors["Back_Left_Thruster"]-self.PWMNORMAL) + self.PWMNORMAL
        self._motors["Up_Front_Thruster"]=0.5 * (self._motors["Up_Front_Thruster"]-self.PWMNORMAL) + self.PWMNORMAL
        self._motors["Up_Back_Thruster"]=0.5 * (self._motors["Up_Back_Thruster"]-self.PWMNORMAL) + self.PWMNORMAL
        return

    def limitations_swordfish_mode(self):
        Zsteps = (self._motors["Up_Front_Thruster"]- self.PWMNORMAL) * self.SWORDFISHCOEFFICIENT
        Hsteps = (self.PWMRANGE - abs(Zsteps)) * ((self._motors["Back_Left_Thruster"] - self.PWMNORMAL) / self.PWMRANGE)
        self._motors["Up_Front_Thruster"]=self.PWMNORMAL + Zsteps
        self._motors["Up_Back_Thruster"]=self.PWMNORMAL + Zsteps
        self._motors["Back_Right_Thruster"]=self.PWMNORMAL + Hsteps
        self._motors["Back_Left_Thruster"]=self.PWMNORMAL + Hsteps
        return

    def limitations_return_mode(self):
       Hsteps = (self._motors["Back_Right_Thruster"] - self.PWMNORMAL) * self.RETURNCOEFFICIENT
       Zsteps = (self._motors["Up_Front_Thruster"] - self.PWMNORMAL) * 0.75
       self._motors["Up_Front_Thruster"]=self.PWMNORMAL + Zsteps
       self._motors["Up_Back_Thruster"]=self.PWMNORMAL + Zsteps
       self._motors["Back_Right_Thruster"]=self.PWMNORMAL + Hsteps
       self._motors["Back_Left_Thruster"]=self.PWMNORMAL + Hsteps
       return

    def _checkForZeroCrossing(self, previousPwm, currentPwm):
        PWMZERO=self.PWMNORMAL
        if ((previousPwm - PWMZERO) * (currentPwm - PWMZERO)< 0 ):
            return True
        else:
            return False

    def _zeroCrossing(self,previousPwm,currentPwm,motorname):
        zeroCrossing = self._checkForZeroCrossing(previousPwm, currentPwm)
        NUMBER_OF_ZERO_CYCLES = 3  # how many times we send pwmnormal to the avr when zero crossing occurs.

        if (zeroCrossing):
            print("Zero Crossing Occured from ",motorname," previous: ",previousPwm," target: ",currentPwm)
            self._futureStepsForSuddenChange[motorname]=[currentPwm,NUMBER_OF_ZERO_CYCLES]
            self._motors[motorname]=self.PWMNORMAL


    def _checkForMaximumDifference(self,previousPwm, currentPwm):
        MAXIMUMDIFFERENCE=self.MAXIMUMPWMCHANGE
        difference = abs(currentPwm - previousPwm)
        if difference > MAXIMUMDIFFERENCE:
            return True
        else:
            return False

    def _checkForSuddenChange(self,motorname):
        MAXIMUMDIFFERENCE=self.MAXIMUMPWMCHANGE
        previousPwm=float(self._hardware.getDevicePreviousValue(motorname))
        currentPwm=float(self._motors[motorname])
        self._zeroCrossing(previousPwm,currentPwm,motorname)
        # difference = self._checkForMaximumDifference(previousPwm, currentPwm)
        # if (difference):
                    # currentPwm[i]=ZeroPwm
                # print("Sudden Change Occured current PWM: ", currentPwm , " Previous: ", previousPwm ,end=" ")
                # unitVector = (currentPwm - previousPwm) / (abs(currentPwm - previousPwm))
                # newCurrentPwm = previousPwm + (MAXIMUMDIFFERENCE * unitVector)
                # print("Current Pwm Set To: ", newCurrentPwm)
                # self._futureStepsForSuddenChange[motorname]=currentPwm
                # self._motors[motorname]=newCurrentPwm


    def _setMyDevicesToDefaults(self):

        # self._motors["Front_Right_Thruster"]=  self._hardware.getDeviceBaseValue("Front_Right_Thruster")
        # self._motors["Front_Left_Thruster"]=   self._hardware.getDeviceBaseValue("Front_Left_Thruster")
        # self._motors["Back_Right_Thruster"]=   self._hardware.getDeviceBaseValue("Back_Right_Thruster")
        # self._motors["Back_Left_Thruster"]=    self._hardware.getDeviceBaseValue("Back_Left_Thruster")
        # self._motors["Up_Front_Thruster"] =    self._hardware.getDeviceBaseValue("Up_Front_Thruster")
        # self._motors["Up_Back_Thruster"]  =    self._hardware.getDeviceBaseValue("Up_Back_Thruster")
        self._motors["Front_Right_Thruster"] =  self.PWMNORMAL
        self._motors["Front_Left_Thruster"] =   self.PWMNORMAL
        self._motors["Back_Right_Thruster"] =   self.PWMNORMAL
        self._motors["Back_Left_Thruster"] =    self.PWMNORMAL
        self._motors["Up_Front_Thruster"] =     self.PWMNORMAL
        self._motors["Up_Back_Thruster"] =      self.PWMNORMAL

        self._hardware.setDeviceValue("Front_Right_Thruster",   self._hardware.getDeviceBaseValue("Front_Right_Thruster"))
        self._hardware.setDeviceValue("Front_Left_Thruster",self._hardware.getDeviceBaseValue("Front_Left_Thruster"))
        self._hardware.setDeviceValue("Back_Right_Thruster",self._hardware.getDeviceBaseValue("Back_Right_Thruster"))
        self._hardware.setDeviceValue("Back_Left_Thruster",self._hardware.getDeviceBaseValue("Back_Left_Thruster"))
        self._hardware.setDeviceValue("Up_Front_Thruster",self._hardware.getDeviceBaseValue("Up_Front_Thruster"))
        self._hardware.setDeviceValue("Up_Back_Thruster", self._hardware.getDeviceBaseValue("Up_Back_Thruster"))

        for key in self._futureStepsForSuddenChange:
            self._futureStepsForSuddenChange[key]=[None,0]


    def _setFromMyLocalToDevice(self):
        self._hardware.setDeviceValue("Front_Right_Thruster", self._motors["Front_Right_Thruster"])
        self._hardware.setDeviceValue("Front_Left_Thruster",self._motors["Front_Left_Thruster"])
        self._hardware.setDeviceValue("Back_Right_Thruster",self._motors["Back_Right_Thruster"])
        self._hardware.setDeviceValue("Back_Left_Thruster",self._motors["Back_Left_Thruster"])
        self._hardware.setDeviceValue("Up_Front_Thruster",self._motors["Up_Front_Thruster"])
        self._hardware.setDeviceValue("Up_Back_Thruster", self._motors["Up_Back_Thruster"])

    def mail(self, event, mail_map=None):
        if event == "TCP ERROR":
            self._setMyDevicesToDefaults()
        if event is "TCP":
            if(super().mail(event,mail_map)):
                for key in self._valueMap:
                    self._valueMap[key]=float(self._valueMap[key])
                #change values to floats
                for key in self._futureStepsForSuddenChange:
                    self._futureStepsForSuddenChange[key][0]=None

                if self._valueMap["currentmode"] > 0:
                    self._valueMap["x"]=0
                self._calculateHorizontalMotors()
                self._calculateVerticalMotors()
                self._limit()

                self._checkForSuddenChange("Front_Right_Thruster")
                self._checkForSuddenChange("Front_Left_Thruster")
                self._checkForSuddenChange("Back_Right_Thruster")
                self._checkForSuddenChange("Back_Left_Thruster")
                self._checkForSuddenChange("Up_Front_Thruster")
                self._checkForSuddenChange("Up_Back_Thruster")

                self._hardware.setDeviceValue("Front_Right_Thruster",self._motors["Front_Right_Thruster"])
                self._hardware.setDeviceValue("Front_Left_Thruster",(self._motors["Front_Left_Thruster"]))
                self._hardware.setDeviceValue("Back_Right_Thruster",self._motors["Back_Right_Thruster"])
                self._hardware.setDeviceValue("Back_Left_Thruster",self._inverse(self._motors["Back_Left_Thruster"]))
                self._hardware.setDeviceValue("Up_Front_Thruster",self._motors["Up_Front_Thruster"])
                self._hardware.setDeviceValue("Up_Back_Thruster",(self._motors["Up_Back_Thruster"]))
                
                #self._hardware.setDeviceValue("Front_Right_Thruster", 1845)
                #self._hardware.setDeviceValue("Front_Left_Thruster",1845)
                #self._hardware.setDeviceValue("Back_Right_Thruster",1845)
                #self._hardware.setDeviceValue("Back_Left_Thruster",1035)
                #self._hardware.setDeviceValue("Up_Front_Thruster",1845)
                #self._hardware.setDeviceValue("Up_Back_Thruster",1845)
                #
                # print(self._hardware.getDeviceValue("Front_Right_Thruster"))
                # print(self._hardware.getDeviceValue("Front_Left_Thruster"))
                # print(self._hardware.getDeviceValue("Back_Right_Thruster"))
                # print(self._hardware.getDeviceValue("Back_Left_Thruster"))
                # print(self._hardware.getDeviceValue("Up_Front_Thruster"))
                # print(self._hardware.getDeviceValue("Up_Back_Thruster"))


        if event == "I2C":
            futursteps=False
            for key in self._futureStepsForSuddenChange:
                if self._futureStepsForSuddenChange[key][0] != None :

                    if(self._futureStepsForSuddenChange[key][1]==0):
                        self._motors[key]=self._futureStepsForSuddenChange[key][0]
                        self._futureStepsForSuddenChange[key][0]=None

                    if (self._futureStepsForSuddenChange[key][1] > 0):
                        futursteps = True
                        self._futureStepsForSuddenChange[key][1] -= 1
                        # self._checkForSuddenChange(key)
            if (futursteps):
                max_number_of_steps=0
                for key in self._futureStepsForSuddenChange:
                    if(self._futureStepsForSuddenChange[key][1]>max_number_of_steps):
                        max_number_of_steps=self._futureStepsForSuddenChange[key][1]
                for key in self._futureStepsForSuddenChange:
                    if (self._futureStepsForSuddenChange[key][0]==None):
                        self._futureStepsForSuddenChange[key][0]=self._motors[key]
                        self._motors[key]=self.PWMNORMAL
                        self._futureStepsForSuddenChange[key][1]=max_number_of_steps
                    elif(self._futureStepsForSuddenChange[key][1]<max_number_of_steps):
                        self._futureStepsForSuddenChange[key][1] = max_number_of_steps

            self._setFromMyLocalToDevice()