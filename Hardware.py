class Avr:

    def __init__(self,address,communicator):
        self._address=address
        self._devices={}
        self._devicesBaseValue={}
        self.communicator=communicator


    def addDevice(self,name,baseValue,BytesNo):
        self._devices[name] = {"base": baseValue, "current": baseValue, "numberOfBytes":BytesNo, "previous":baseValue}

    def mail(self,eventName,data=None):
        if eventName=="I2C":
            DataToBeSent=[]
            IndexOfSingleBytes=[]
            for index, devicename in enumerate(self._devices):
                device=self._devices[devicename]
                if device["numberOfBytes"]==1:
                    IndexOfSingleBytes.append(index)
                DataToBeSent.append(device["current"])
                device["previous"]=device["current"]
                if device["previous"]-device["current"]>200:
                    print ("Sudden Change error")
            self.communicator.sendTo(self._address,DataToBeSent,IndexOfSingleBytes)

class Hardware:
    def __init__(self,communicator):
        self._communicator=communicator
        self._avrList=[]


    def addAVR(self,address):
        avr=Avr(address,self._communicator)
        self._avrList.append(avr)

    def getDeviceBaseValue(self,deviceName):
        for avr in self._avrList:
            for device in avr._devices:
                if device == deviceName:
                    return avr._devices[device]["base"]

    def getDeviceValue(self,deviceName):
        for avr in self._avrList:
            for device in avr._devices:
                if device == deviceName:
                    return avr._devices[device]["current"]

    def getDevicePreviousValue(self,deviceName):
        for avr in self._avrList:
            for device in avr._devices:
                if device == deviceName:
                    return avr._devices[device]["previous"]

    def setDeviceValue(self,deviceName,value):
        for avr in self._avrList:
            for device in avr._devices:
                if device == deviceName:
                    avr._devices[device]["current"]=value

    def getAvrContainingDevice(self,deviceName):
        for avr in self._avrList:
            for device in avr._devices:
                if device== deviceName:
                    return avr
