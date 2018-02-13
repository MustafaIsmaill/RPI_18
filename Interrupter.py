import threading


class Interrupter:

    def __init__(self, callback_function, *args):
        self.register(callback_function, *args)

    def register(self, callback_function, *args):
        callback_function(*args)
        threading.Timer(0.1, self.register).start()
