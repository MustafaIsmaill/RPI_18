from multiprocessing import Process
import threading
import time

class SensorRegistry:
    def __init__(self):
        self._pokeInterval=1
        self._sensors=[]
        self._timerWakeUpCall=None
        # self.eventTimer=Timer(self._pokeInterval,self._trigger)
        # self.eventTimer.start()
        self.thread=threading.Thread(target=self.timer)
        self.thread.start()
        # self.process=Process(target=self.timer)
        # self.process.start()
    def timer(self):
        while True:
            time.sleep(self._pokeInterval)
            self._trigger()

    def registerSensor(self,sensorClass):
        newSensor=sensorClass()
        self._sensors.append(newSensor)

    def _trigger(self):
        dictToBeSent=self.mail()
        strToBeSent=""
        for key in dictToBeSent:
            strToBeSent+=(str(key)+" "+str(dictToBeSent[key])+";")
        if self._timerWakeUpCall != None :
           self._timerWakeUpCall("Sensors",strToBeSent)
        # self.eventTimer.run()

    def registerCallBack(self,callback):
        self._timerWakeUpCall=callback

    def mail(self):
        receivedDictionaries={}
        for sensor in self._sensors:
            receivedDictionary=sensor.update()
            receivedDictionaries.update(receivedDictionary)
        return receivedDictionaries
