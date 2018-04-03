import threading


class Dummy_Interrupter:

    def __init__(self, callback_function, str, data):
        self.register(callback_function, str, data)

    def register(self, callback_function, str, data):
        callback_function(str, data)
        threading.Timer(0.02, self.register, [callback_function, str, data]).start()
