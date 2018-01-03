from flexx import app,event,ui,dialite
from protocol import ProbeProtocol
import uart,os
import struct,threading
from flexx.util.getresource import get_resource


for asset_name in ('buttons.css',):
    dest = os.path.abspath(os.path.join(__file__, '..','resources'))
    path = os.path.join(dest,asset_name)
    code = open(path,'rb').read().decode()
    app.assets.associate_asset(__name__, asset_name, code)

class DeviceItem(ui.PinboardLayout):
    def init(self):
        self.style="background:#f00;color:#0f0;min-height:150px"
        with self:
            ui.Label(flex=0,text="设备名称1：",pos=(10,10),base_size=(100,32))
            ui.Label(flex=0,text="设备名称2：",pos=(10,30),base_size=(100,32))

class DeviceItem1(ui.PinboardLayout):
    def init(self):
        self.style="background:#f50;color:#0f0;min-height:100px"
        with self:
            ui.Label(flex=0,text="设备名称3：",pos=(10,10),base_size=(100,32))
            ui.Label(flex=0,text="设备名称4：",pos=(10,30),base_size=(100,32))    

class LeftMenuUi(ui.VBoxPanel):
    def init(self):
        ui.Button(text="功能1")
        ui.Button(text='功能2')

class HistoryListUi(ui.Widget):

    def init(self):
        self.mDevList = ui.VBoxPanel(flex=1,parent = self)
        with self.mDevList:
            for i in range(2):
                DeviceItem(flex=0)

    def append(self):
        with self.mDevList:
            DeviceItem1(flex=0)

    def openother(self):
        self.children.remove(self.mDevList)
        with self:
            with ui.VBoxPanel(flex=1):
                for i in range(5):
                    ui.Label(flex=0,text="设备名称1113：",pos=(10,10),base_size=(100,32))
            


class SerialConfView(ui.VBoxPanel):
    """ 串口配置 """
    def __init__(self, portCallback, *init_args, **kwargs):
        super().__init__(*init_args, **kwargs)
        self.callback = portCallback

    def init(self):
        self.btnArray = []
        self.portMap = {}
        self.style="min-height:150px"
        udr = uart.UartDriver()
        comInfoList = udr.findAllUartDev()
        with ui.HBox(flex=0,padding=10,base_size=52,style='background:#ddd'):
            if len(comInfoList) <= 0:
                 ui.Label(flex=1,text="没有发现任何可用串口设备！",base_size=(400,32))
            else:
                for iPort in comInfoList:
                    str = "串口名称：%s ----- 端口：%s " % (iPort.description, iPort.device)
                    ui.Label(flex=0,text=str,style='height:32px;line-height:32px')
                    ui.Widget(flex=1)
                    btn = ui.Button(flex=0,text="打开串口",css_class="button button-primary button-rounded button-small", base_size=(100,32))
                    self.btnArray.append(btn)
                    self.portMap[btn.id] = iPort

                self.connect(self.__openserial_clicked,'btnArray*.mouse_click')
        ui.Widget(flex=1)  
                
    #@event.connect('btnArray*.mouse_click')
    def __openserial_clicked(self,*events):
        evt = events[-1]
        if isinstance(evt,list):
            selBtn = evt[0]['source']
        else:
            selBtn = evt['source']
        port = self.portMap[selBtn.id]
        if self.callback(port) == True:
            selBtn.text = "关闭串口"
        else:
            selBtn.text = "打开串口"

class Cev485Protocol:
    """中电485协议实现"""
    def __init__(self,uartfd):
        self.uartFD = uartfd

    def _crcsum(self,data):
        checksum = 0
        for d in data:
            checksum = checksum ^ d
        return checksum


    def _crcsum_with_convert(self,data):
        checksum = self._crcsum(data)
        if checksum == 0x7e:
            d=[0x7d,0x01]
        elif checksum == 0x7f:
            d=[0x7d,0x02]
        elif checksum == 0x7d:
            d=[0x7d,0x03]
        else:
            d=[checksum]
        return d

    def MQF(self,devaddr):
        crc = self._crcsum_with_convert([devaddr,0x92])
        
        if len(crc) > 1:
            package = bytes([0x7e,0x80,0xd0,crc[0],crc[1],devaddr,0x92,0x7f])
        else:
            package = bytes([0x7e,0x80,0xd0,crc[0],devaddr,0x92,0x7f])
        return package

    def send(self,package):
        count = 5
        while (self.uartFD.write(package) < len(package)) and count > 0: count -= 1
        if count == 0:
            raise Exception("uart send error")
        return package

    def _read_data(self):
        da = self.uartFD.read()
        if len(da) > 0:
            if da[0] == 0x7d:
                da = self.uartFD.read()
                if len(da) > 0:
                    if da[0] == 0x01:
                        return 0x7e
                    elif da[0] == 0x02:
                        return 0x7f
                    elif da[0] == 0x03:
                        return 0x7d
                else:
                    raise Exception('数据包接收转换错误')
            else:
                return da[0]   
        raise Exception('数据包接收转换错误')
            

    def _type_to_name(self,ftype):
        if ftype == 0x90:
            return "MDF"
        elif ftype == 0x91:
            return "SDF"
        elif ftype == 0x92:
            return "MQF"
        elif ftype == 0x93:
            return "SRF"
        elif ftype == 0x94:
            return "MRF"
        else:
            return "ERR"


    def recv_frame(self):
        state = 0
        crc = 0
        count = 2
        rxbuf = []
        databuf = []
        while(True):
            try:
                if state == 0:
                    da = self.uartFD.read()
                    if (len(da) > 0):
                        if da[0] == 0x7e:
                            rxbuf.append(da[0])
                            state = 1
                    else:
                        count -= 1
                        if count <= 0:
                            return (self._type_to_name(0),0,[],False,"超时")

                elif state == 1:
                    da = self._read_data()
                    rxbuf.append(da)
                    da = self._read_data()
                    rxbuf.append(da)
                    state = 2
            
                elif state == 2:
                    crc = self._read_data()
                    rxbuf.append(crc)
                    state = 3

                elif state == 3:
                    addr = self._read_data()
                    databuf.append(addr)
                    state = 4
            
                elif state == 4:
                    ftype = self._read_data()
                    databuf.append(ftype)
                    state = 5

                elif state == 5:
                    da = self._read_data()
                    if da == 0x7f:
                        rcrc = self._crcsum(databuf)
                        if crc != rcrc:
                            raise Exception('CRC校检错误')
                        rxbuf.extend(databuf)
                        rxbuf.append(da)
                        return (self._type_to_name(ftype),addr,rxbuf,True,"正常")
                    else:
                        databuf.append(da)

            except Exception as ex:
                return (self._type_to_name(0),0,[],False,ex.args[0])
                
            
class ClientCEV485View(ui.Widget):
    """中电485从设备模拟"""
    def __init__(self, uartfd, *init_args, **kwargs):
        super().__init__(*init_args, **kwargs)
        self.uartFD = uartfd
        self.isThreadStarted = False
        self.recvThread = None

    def init(self):
        with ui.HBox(flex=1):
            with ui.Widget(flex=1,style="overflow-y:scroll"):
                with ui.VBoxPanel(flex=0) as self.leftView:
                    with ui.HBox(flex=0,style="background:#ee0;min-height:40px;max-height:40px"):
                        ui.Label(text="<b>主设备</b>")
                        ui.Label(text="<b>从设备</b>")
            with ui.VBox(flex=0,padding=6,style="background:#eee;color:#000;min-width:200px"):
                self.listenMode = ui.RadioButton(text="CEV485监听模式",checked=True)
                self.simuAllClient = ui.RadioButton(text="模拟所有客户端响应")
                self.simuOneKeyModClient = ui.RadioButton(text="模拟一键报警")
                self.btnStart = ui.Button(text="模拟启动",css_class="button button-primary button-rounded button-small",pos=(10,10),base_size=(160,32))
                ui.Widget(flex=1)


    def _get_addrcolor(self,addr):
        dev=('#cea09d','未知')
        if addr == 0x0:
            dev = ('#ffec97','主设备')
        elif addr == 0x1:
            dev = ('#60a65f','一键报警')
        elif addr == 0x2:
            dev = ('#247065','语音模块')
        elif addr == 0x3:
            dev = ('#2b3d54','电源管理')
        elif addr == 0x4:
            dev = ('#2c5b61','状态指示')
        elif addr == 0x5:
            dev = ('#cea09d','保留')
        elif addr == 0x6:
            dev = ('#cea09d','保留')
        elif addr == 0x7:
            dev = ('#cea09d','保留')
        elif addr == 0x8:
            dev = ('#cea09d','保留')
        elif addr == 0x9:
            dev = ('#cea09d','保留')
        elif addr == 0xa:
            dev = ('#cea09d','保留')
        elif addr == 0xb:
            dev = ('#cea09d','保留')
        elif addr == 0xc:
            dev = ('#cea09d','保留')
        elif addr == 0xd:
            dev = ('#cea09d','保留')
        elif addr == 0xe:
            dev = ('#cea09d','保留')
        elif addr == 0xf:
            dev = ('#b27f7a','广播')
        return dev

    def packView(self,name,addr,package,msg,isDev):
        srcaddr = (addr & 0xf0)>>4
        destaddr = (addr & 0x0f)
        if len(package) > 100:
            style_str = "background:#fff;min-height:%s;max-height:%s" % ('160px','160px')
        else:
            style_str = "background:#fff;min-height:%s;max-height:%s" % ('100px','100px')

        with ui.Widget(flex=0,style=style_str):
            with ui.HBox(flex=1,padding=6):
                if isDev:
                    ui.Widget(flex=1)
                style_str = "background:%s;min-width:300px;max-width:500px" % self._get_addrcolor(srcaddr)[0]
                with ui.VBox(flex=0,padding=6,style=style_str):
                    ui.Label(flex=0,text="<b>%s -- S[%d]%s  D[%d]%s (%s)</b>" % (name,srcaddr ,self._get_addrcolor(srcaddr)[1], destaddr,self._get_addrcolor(destaddr)[1], msg),style="min-height:32px;max-height:32px")
                    #strs = [hex(x) for x in package]
                    strs = ''
                    for b in package:strs += "%02X " % int(b)
                    ui.Label(flex=1,text=strs,wrap=2,style="background:#eee;overflow-y:scroll")

                if not isDev:
                    ui.Widget(flex=1)

    def _doListenRS485(self,args):
        sdf = args;
        while self.isThreadStarted:
            proto = Cev485Protocol(uartfd = sdf)
            #(fname,addr,pk,ret,msg) = proto.recv_frame()
            ret = proto.recv_frame()
            self.emit('updateview',dict(value=ret))
            
    
    @event.connect('updateview')
    def _update_packview(self,*events):
        ev = events[-1]
        (fname,addr,pk,ret,msg) = ev['value']
        if ret:
            with self.leftView:
                try:
                    if addr & 0xf0 == 0:
                        self.packView(fname,addr,pk,msg,False)
                    else:
                        self.packView(fname,addr,pk,msg,True)
                except Exception as e:
                    self.packView("未知包",0x0,[],"错误的数据包",True)


    @event.connect('btnStart.mouse_click')
    def _start_botton_evthandler(self,*events):
        if self.listenMode.checked and self.isThreadStarted == False:
            self.isThreadStarted = True
            self.btnStart.text = "模拟结束"
            self.recvThread = threading.Thread(target=self._doListenRS485,args=(self.uartFD,))
            self.recvThread.setDaemon(True)
            self.recvThread.start()
        elif self.listenMode.checked and self.isThreadStarted:
            self.isThreadStarted = False
            self.recvThread.join()
            dialite.inform(title="模拟工作状态",message="模拟工作结束")
            self.btnStart.text = "模拟启动"


class MainCEV485View(ui.Widget):
    """中电485主设备模拟 """
    def __init__(self, uartfd, *init_args, **kwargs):
        super().__init__(*init_args, **kwargs)
        self.uartFD = uartfd

    def init(self):
        with ui.HBox(flex=1):
            with ui.Widget(flex=1,style="overflow-y:scroll"):
                with ui.VBoxPanel(flex=0) as self.leftView:
                    with ui.HBox(flex=0,style="background:#ee0;min-height:40px;max-height:40px"):
                        ui.Label(text="<b>主设备</b>")
                        ui.Label(text="<b>从设备</b>")
            with ui.PinboardLayout(flex=0,style="background:#eee;color:#000;min-width:200px"):
                self.btnStartPolling = ui.Button(flex=0,text="发起一次轮询",css_class="button button-primary button-rounded button-small",pos=(10,10),base_size=(160,32))

    def _get_addrcolor(self,addr):
        if addr == 0x0:
            dev = ('#ffec97','主设备')
        elif addr == 0x1:
            dev = ('#60a65f','一键报警')
        elif addr == 0x2:
            dev = ('#247065','语音模块')
        elif addr == 0x3:
            dev = ('#2b3d54','电源管理')
        elif addr == 0x4:
            dev = ('#2c5b61','状态指示')
        elif addr == 0x5:
            dev = ('#cea09d','保留')
        elif addr == 0x6:
            dev = ('#cea09d','保留')
        elif addr == 0x7:
            dev = ('#cea09d','保留')
        elif addr == 0x8:
            dev = ('#cea09d','保留')
        elif addr == 0x9:
            dev = ('#cea09d','保留')
        elif addr == 0xa:
            dev = ('#cea09d','保留')
        elif addr == 0xb:
            dev = ('#cea09d','保留')
        elif addr == 0xc:
            dev = ('#cea09d','保留')
        elif addr == 0xd:
            dev = ('#cea09d','保留')
        elif addr == 0xe:
            dev = ('#cea09d','保留')
        elif addr == 0xf:
            dev = ('#b27f7a','广播')
        return dev

    def packView(self,name,addr,package,msg,isDev):
        srcaddr = (addr & 0xf0)>>4
        destaddr = (addr & 0x0f)
        if len(package) > 100:
            style_str = "background:#fff;min-height:%s;max-height:%s" % ('160px','160px')
        else:
            style_str = "background:#fff;min-height:%s;max-height:%s" % ('100px','100px')

        with ui.Widget(flex=0,style=style_str):
            with ui.HBox(flex=1,padding=6):
                if isDev:
                    ui.Widget(flex=1)

                with ui.VBox(flex=0,padding=6,style="background:%s;min-width:300px;max-width:500px" % self._get_addrcolor(srcaddr)[0]):
                    mainaddr = (addr & 0xf0)>>4
                    devaddr = (addr & 0x0f)
                    ui.Label(flex=0,text="<b>%s -- S[%d]%s  D[%d]%s (%s)</b>" % (name, srcaddr ,self._get_addrcolor(srcaddr)[1], destaddr,self._get_addrcolor(destaddr)[1],msg),style="min-height:32px;max-height:32px")
                    #strs = [hex(x) for x in package]
                    strs = ''
                    for b in package:strs += "%02X " % int(b)
                    ui.Label(flex=1,text=strs,wrap=2,style="background:#eee;overflow-y:scroll")

                if not isDev:
                    ui.Widget(flex=1)



    @event.connect("btnStartPolling.mouse_click")
    def btnStartPollingEvent(self,*events):
        proto = Cev485Protocol(uartfd = self.uartFD)
        for devaddr in range(1,13):
            devaddr = 0x0f & devaddr
            p = proto.MQF(devaddr)
            with self.leftView:
                try:
                    proto.send(p)
                    self.packView("MQF",devaddr,p,"主设备发送完成",False)
                except Exception as e:
                    print(e)
                    self.packView("MQF",devaddr,p,"主设备发送错误",False)
                else:
                    (fname,addr,pk,ret,msg) = proto.recv_frame()
                    if ret:
                        self.packView(fname,addr,pk,msg,True)
                    else:
                        self.packView("无回应",devaddr,[],msg,True)
                

class MenuBarView(ui.Widget):
    """ 主菜单 """
    def __init__(self, menuBtnFunc, *init_args, **kwargs):
        super().__init__(*init_args, **kwargs)
        self.evthandler = menuBtnFunc

    def init(self):
        self.buttonNames = ["打开串口","中电485主机协议测试","中电485客户机协议测试"]
        self.menuButtons=[]
        with ui.HBox(flex=0,base_size=60,style='background:#eee;color:#000;min-height:60px'):
            for btnName in self.buttonNames:
                btnObj = ui.Button(flex=0,text=btnName,css_class="button button-tiny")
                self.menuButtons.append(btnObj)
            ui.Widget(flex=1)

    def getMenuItemIndex(self,btnid):
        i=0
        for btn in self.menuButtons:
            if btn.id == btnid:
                return i
            else:
                i += 1
        return -1

    
    @event.connect('menuButtons*.mouse_click')
    def _menuButtonEventHandler(self,*events):
        self.evthandler(events)

class MainView(ui.Widget):
    """ 主视图 """
    def init(self):
        self.udr = uart.UartDriver()
        self.uartfd = None
        self.mDevList = []
        with ui.VBoxPanel() as self.vboxs:
            with ui.PinboardLayout(flex = 0,base_size=100,style="background:#777;color:#0ff"):
                self.mDevNameLab = ui.Label(flex=0,text="目前没有打开的串口",pos=(10,10),base_size=(600,32))
                self.mDevTypeLab = ui.Label(flex=0,text="设备规格：",pos=(10,40),base_size=(600,32))
            self.mMenuBar = MenuBarView(flex=0,menuBtnFunc=self._menuBtnHandler)
            self.mBottomArea = ui.Widget(flex=1)

    def setSerialInfo(self,msg):
        self.mDevNameLab.text = "串口%s已打开" % msg
   

    def _menuBtnHandler(self,*events):
        """主菜单事件处理"""
        evt = events[-1]
        btn = evt[0]['source']
        mindex = self.mMenuBar.getMenuItemIndex(btn.id)
        print(mindex)
        if mindex == 0:
            with self.mBottomArea:
                self.mBottomArea.children=[]
                SerialConfView(flex =0,portCallback=self.openPortCallback)
        elif mindex == 1:
            self.showMainCEV485View()
        elif mindex == 2:
            self.showClientCEV485View()


    def openPortCallback(self,port):
        """ 串口打开处理 """
        self.uartfd = self.udr.createHandler(port)
        if (self.uartfd != None):
            dialite.inform(title="串口信息",message="串口%s已打开" % port.device)
            self.setSerialInfo(port.device)
            return True
        dialite.inform(title="串口信息",message="串口%s打开失败" % port.device)
        return False

    def button_clicked(self,*events):
        self.showDeviceListUi()

    def showSerialView(self):
        self.mBottomArea.children=[]
        with self.mBottomArea:
            with ui.PinboardLayout(flex = 0,base_size=100,style="background:#f00;color:#0f0"):
                ui.Label(flex=0,text="设备名称1113：",pos=(10,10),base_size=(100,32))

    def showClientCEV485View(self):
        self.mBottomArea.children = []
        if self.uartfd == None:
            dialite.inform(title="串口信息",message="串口没有打开！")
            return
        with self.mBottomArea:
            ClientCEV485View(uartfd=self.uartfd,flex=1)

    def showMainCEV485View(self):
        self.mBottomArea.children=[]
        if self.uartfd == None:
            dialite.inform(title="串口信息",message="串口没有打开！")
            return

        with self.mBottomArea:
            MainCEV485View(uartfd=self.uartfd,flex=1)

    def showDeviceListUi(self):
        self.mBottomArea.children=[]
        with self.mBottomArea:
            with ui.HBoxPanel(flex=1):
                with ui.VBoxPanel(flex=0,base_size=200,style='background:#aaa;color:#0f0;min-width:200px'):
                    self.b1 = ui.Button(text="功能1")
                    self.b2 = ui.Button(text='功能2')
                self.hist = HistoryListUi(flex=1,style="overflow-y:scroll")
 


    