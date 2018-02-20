import threading


class Interrupter:

    def __init__(self, callback_function, str):
        self.register(callback_function)

    def register(self, callback_function):
        callback_function("I2C")
        threading.Timer(0.001, self.register, [callback_function]).start()
