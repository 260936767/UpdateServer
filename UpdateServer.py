#
#
#
#

import uart
import sys
import threading
from protocol import ProbeProtocol
from flexx import app
from mainview import MainView

def doTest(args):
    print("In thread")

def doCommunication(args):
    sfd = args
    while(True):
        print("Communication thread [%s] start ..." % sfd.name)
        probe = ProbeProtocol(sfd)
        td = probe.doExec()
        sfd.close()
        if (td == None):
            print("Cannot be found in the %s" % sfd.name)
            return
        print(">> Found a terminal in %s port." % sfd.name)
        '''
        print("Hardware ID:%s",td["MID"])
        print("Config ID:%s",td["ID"])
        print("IAP Program Ver:%s",td["IAPVER"])
        print("Firmware Program Ver:%s",td["FWVER"])
        print("Last Update Time:%s",td["UPDATE"])
        '''
    return


if __name__ == '__main__':

    print("=================================================================")
    print("==            Update Server (Ver 0.01)                         ==")
    print("==                                                             ==")
    print("==                   by NickYang（yrmail@163.com）             ==")
    print("=================================================================")
    print("")
    print("finding serial com ... ")

    app.launch(MainView, 'app')
    app.run()


    '''
    udr = uart.UartDriver()
    comInfoList = udr.findAllUartDev()

    commThreads = []

    if len(comInfoList) <= 0:
        print("Cannot found any serial device!")
    else:
        for ci in comInfoList:
            print("Serial port [%s] available." % ci.device)
            print("Desc:%s" % ci.description)
            print("")
            sfd = udr.createHandler(ci)
            if (sfd != None):
                t = threading.Thread(target=doCommunication,args=(sfd,))
                commThreads.append(t)

    for ct in commThreads:
        ct.setDaemon(True)
        ct.start()
        ct.join()
     '''