import pigpio

class Interrupt:

    def __init__(self):
        self._pi = pigpio.pi()
    
    def register(self, pin_number, rising_falling, callbackfunction,*args):
        def callback(gpio, level, tick):
            #print("Interrupt!")
            callbackfunction(*args)

        self._pi.callback(pin_number, pigpio.FALLING_EDGE, callback)
    #     if rising_falling:
    #         GPIO_PUD=pigpio.PUD_DOWN
    #         GPIO_RISING_FALLING=GPIO.RISING
    #     else:
    #         GPIO_PUD=GPIO.PUD_UP
    #         GPIO_RISING_FALLING=GPIO.FALLING
    #
    #     pigpio.callback(pin_number, GPIO.IN, pull_up_down=GPIO_PUD)
    #
    #     def callback(channel):
    #         #EVENT DETECTED
    #         callbackfunction(args)
    #
    #     GPIO.add_event_detect(pin_number,GPIO_RISING_FALLING,callback=callback,bouncetime=0)
    #     except KeyboardInterrupt:
    #         GPIO.cleanup()
    #     GPIO.cleanup()
    # #

