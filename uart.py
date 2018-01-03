#
#串口库采用 pyserial  API文档参考：https://pyserial.readthedocs.io/en/latest/pyserial_api.html 
#
#
import serial
import serial.tools.list_ports

class UartDriver:
    mTimeOut = 1
    def __init__(self):
        self.mInstance = None#serial.serial_for_url("com1",115200,1,0,0,True)

    def findAllUartDev(self):
        plist = list(serial.tools.list_ports.comports())
        return plist

    def createHandler(self,cominfo):
        try:
            fd = serial.Serial(
                port=cominfo.device, 
                baudrate=4800, 
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                timeout=1,
                write_timeout=1)
            if (fd.is_open == False): fd.open()
        except Exception as e:
            return None
        else:
            if (fd.is_open == False): return None
            fd.reset_input_buffer()
            fd.reset_output_buffer()
            return fd
        

    def readData(self,timeout):
        rbuff = self.mInstance.read(128)
        return rbuff


