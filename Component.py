from abc import *


class Component:  # abstract

    def __init__(self, hardware, identifiers):
        self._hardware = hardware
        self._identifiers = identifiers
        self._valueMap = {}
        for identifier in identifiers:
            self._valueMap[identifier] = identifiers[identifier]

    @abstractmethod
    def mail(self, mail_type, mail_map):

        myNewMail = (mail_map.keys() & self._identifiers.keys())
        if len(myNewMail) > 0:
            for newValue in myNewMail:
                self._valueMap[newValue] = mail_map[newValue]
        return len(myNewMail)