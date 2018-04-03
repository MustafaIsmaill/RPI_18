from Component import *

class Lift_Bag_Communicator(Component):
    def __init__(self, identifiers):
        super().__init__(None, identifiers)
        self._eventCallBack = None

    def registerCallBack(self, callback):
        self._eventCallBack = callback

    def update(self, event, mail_map=None):
        if event is "TCP":
            self._valueMap = mail_map

            if self._valueMap['bag'] == 1:
                if self._eventCallBack is not None:
                    self._eventCallBack("BAG", 'a')

            print("BAG Event")

