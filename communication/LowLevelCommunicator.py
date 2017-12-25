"""import pigpio

class I2cCommunicator:
    def __init__(self):
        # self._pi=pigpio.pi()
        return
    # def readFrom(self,device_adress):
        # handler=self._pi.i2c_open()
        # data=self._pi.i2c_read_byte(handler)
        # self._pi.i2c_close(handler)
        # return data

    def sendTo(self,device_adress,valuestobesent,indexofsinglebytes):
        # handler=self._pi.i2c_open()
        DataArray=[]
        for i in range(len(valuestobesent)):
            value = int(valuestobesent[i])
            if i in indexofsinglebytes:  # if the value I want to send is 1 byte
                DataArray.append(valuestobesent[i])
            else:
                value*=2
                mostsignificant=(value >> 8) & 0xff
                leastsignificant=value & 0xff
                DataArray.append(mostsignificant)
                DataArray.append(leastsignificant)
        #
        # self._pi.i2c_write_device(handler,DataArray)
        # self._pi.i2c_close(handler)
        print ("Values before dividing",valuestobesent)
        #print ("Values after dividing",DataArray) #DEBUGGING"""


# ===================================================Raspberry pi=======================================================
# import pigpio
#
class I2cCommunicator:
    def __init__(self):
        print()
        # self._pi=pigpio.pi()

    def readFrom(self, device_address):
        handler = self._pi.i2c_open(1, device_address)
        data = self._pi.i2c_read_byte(handler)
        self._pi.i2c_close(handler)
        return data

    def sendTo(self, device_adress, valuestobesent, indexofsinglebytes):
        try:
            handler = self._pi.i2c_open(1, device_adress)
        except Exception as e:
            print("Caught an exception in I2C send: ", e)
            return
        DataArray = []
        for i in range(len(valuestobesent)):
            value = int(valuestobesent[i])
            if i in indexofsinglebytes:  # if the value I want to send is 1 byte
                DataArray.append(valuestobesent[i])
            else:
                value *= 2
                mostsignificant = (value >> 8) & 0xff
                leastsignificant = value & 0xff
                DataArray.append(mostsignificant)
                DataArray.append(leastsignificant)
        #
        try:
            self._pi.i2c_write_device(handler, DataArray)
            self._pi.i2c_close(handler)
        except Exception as e:
            print("Caught an exception in I2C send: ", e)
            self._pi.i2c_close(handler)
        print("Values before dividing", valuestobesent)
        # print ("Values after dividing",DataArray) #DEBUGGING
