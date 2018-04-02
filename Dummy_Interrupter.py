import threading


class Dummy_Interrupter:

    def __init__(self, callback_function, str):
        self.register(callback_function, str)

    def register(self, callback_function, str):
        callback_function(str)
        threading.Timer(0.02, self.register, [callback_function, str]).start()
