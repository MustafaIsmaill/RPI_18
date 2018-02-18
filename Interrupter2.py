import threading


class Interrupter:

    def __init__(self, callback_function, *args):
        self.register(callback_function, *args)

    def register(self, callback_function, *args):
        callback_function(*args)
        print("Calling")
        threading.Timer(1, self.register, callback_function, *args).start()
