class PostOffice:
    def __init__(self):
        self._eventListeners={}
        self._mail_map={}
    def registerEventListner(self,eventName,eventListner):
        if(self._eventListeners.get(eventName) is None): #New Event
            list=[eventListner]
            self._eventListeners[eventName]=list
        else:                                            #Adding a listner to an old event
            self._eventListeners[eventName].append(eventListner)

    def deleteEventListner(self,eventName):
            del(self._eventListeners[eventName])

    def triggerEvent(self,*args):
        eventName=args[0]
        for listner in self._eventListeners[eventName]:
            listner(*args)



        # for listner in self._eventListeners[eventName]:
        #     if eventName is "I2C":
        #         try:
        #          listner(eventName)
        #         except Exception as e:
        #             print("Error in the post office... Calling to the Event Listener Failed",e)
        #     if eventName == "TCP":
        #         listner(eventName,args[1])
        #     if eventName == "Sensors":
        #         listner(args[1],self.triggerEvent)
        #     if eventName =='TCP ERROR':
        #         listner(eventName,args[1])

