
# -*- coding: utf-8 -*-
import uart,struct
from crc16pure import crc16xmodem

class Protocol:
    Command = {'SOH':0x01,'STX':0x02,'EOT':0x04,'ACK':0x06,'NAK':0x15,'CAN':0x18,'CRC16':0x43}

    def __init__(self,sfd):
        if (sfd.is_open == False): sfd.open()
        self.uartDrv = sfd

    def recvReady(self):
        rbuff = self.uartDrv.readline()
        if (len(rbuff)>0):
            r1 = rbuff.decode()
            print(r1,end='')
            if (r1 == "@#ready#@\r\n"):
                return True
        return False

    def recvCmdSOH(self,timeout):
        rbuff = self.uartDrv.read(128+3+2)
        if(len(rbuff) < 128+3+2):
            return None,None,False
        
        cmd,num,nnum,data128,crc16 = struct.unpack("!ccc128sH",rbuff)

        #print()
        #print("CRC 0x%x   crc16:0x%x" % (crc16xmodem(data128),crc16))

        if ((cmd[0] != self.Command['SOH']) or (num[0] != nnum[0] ^ 0xff) or (crc16xmodem(data128) != crc16)):
            return None,None,False

        print("Receive SOH package is right !")
        return num[0],data128,True

    def recvEOT(self):
        cmd = self.uartDrv.read(1)
        if (cmd == self.Command['EOT']):
            return True
        return False

    def reset(self):
        self.uartDrv.reset_input_buffer()
        self.uartDrv.reset_output_buffer()

    def sendCmdR(self):
        self.uartDrv.write("R".encode('utf-8'))
        self.uartDrv.flushOutput()

    def sendCmdACK(self):
        self.uartDrv.write(self.Command['ACK'])

    def sendCmdCAN(self):
        self.uartDrv.write(self.Command['CAN'])

    def sendCmdNACK(self):
        self.uartDrv.write(self.Command['NAK'])


class ProbeProtocol(Protocol):
    mRcvNum = 0 
    mCurrNum = 0

    def __init__(self,sfd):
        Protocol.__init__(self,sfd)
        self.mTerminal={}
        self.mStateMap={"Begin":self.state0,"DevInfoProc":self.state1,"CloseSession":self.state2,"ReqReSend":self.state3,"ErrorProc":self.state4}
        self.mData128 = bytes()
        
    
    def doExec(self):
        sta = 'Begin'
        while(sta != "End"):
            try:
                sta = self.mStateMap[sta]()
            except KeyError:
                return None
        return self.mTerminal

    def state0(self):
        #发送R命令，并等待接收SOH包
        count = 500
        tout = 300
        while(count>0):
            if (tout > 0):
                while(self.recvReady() == False and tout > 0):
                    tout = tout -1

            self.reset()
            print("send R command \n")
            self.sendCmdR()
            timeout = 1  # 1 second
            self.mRcvNum,self.mData128,ret = self.recvCmdSOH(timeout)
            if (ret == True):
                if (self.mData128 != None):
                    self.mCurrNum = self.mRcvNum
                    self.sendCmdACK()
                    return "DevInfoProc"
            self.sendCmdNACK()
            count = count - 1
        return "ErrorProc"

    def showParames(self):
        print("====== Device Information =========================================")
        print("MID:",end='')
        for c in self.mTerminal['MID']:
            print("%x " % c,end='')
        print()
        mv = (self.mTerminal['IAPVER'] & 0xff00) >> 8
        sv = self.mTerminal['IAPVER'] & 0x00ff
        print("Bootloader Version: V%x:%x" % (mv,sv))
        mv = (self.mTerminal['FWVER'] & 0xff00) >> 8
        sv = self.mTerminal['FWVER'] & 0x00ff
        print("Frameware Version: V%x:%x" % (mv,sv))
        year,month,day = struct.unpack("@2s2s2s",self.mTerminal['UPDATE'])
        print("Frameware Updatetime: 20%s-%s-%s" % (bytes.decode(year),bytes.decode(month),bytes.decode(day)))
        print("Device ID:",end='')
        for c in self.mTerminal['ID']:
            print("%x " % c,end='')
        print()
        print("==================================================================")
        print()

    def state1(self):
        #对SOH的数据包部分进行解释及处理
        #print(type(self.mData128))
        #print(len(self.mData128))
        mid,iapver,fwver,update,id=struct.unpack("@32sHH6s8s",self.mData128[0:50])
        self.mTerminal['MID']=mid
        self.mTerminal['IAPVER']=iapver
        self.mTerminal['FWVER']=fwver
        self.mTerminal['UPDATE']=update
        self.mTerminal['ID']=id
        self.showParames()
        return "CloseSession"

    def state2(self):
        #正确接收到数据，通知终端结束会话
        if (self.recvEOT()):
            self.sendCmdACK()
        return "End"

    def state3(self):
        #重发SOH数据处理
        self.sendCmdNACK()
        timeOut = 1000  # 1 second
        mRcvNum,mData128,ret = recvCmdSOH(timeOut)
        if (mData128 != None):
            return "DevInfoProc"
        return "ErrorProc"

    def state4(self):
        #进行错误处理
        self.mTerminal = None
        print("found a error!\n")
        return "End"

          

