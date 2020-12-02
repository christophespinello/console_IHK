#!/usr/bin/python3

from utils import load_config, save_config
from serial_ports import serial_ports
import serial
import threading
import queue 

CONFIG_FILENAME = './config.yml'

DEBUG_NO_COMM = True

ERR_IHK_SERIAL_OK = 0
ERR_IHK_SERIAL_NO_FRAME = -1

class SerialThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

        self.config = load_config(CONFIG_FILENAME)
        self.port = self.config['comport']
        self.debit = self.config['baudrate']
        self.debug = False
        if (self.config['debug']):
            self.debug = True
        if not DEBUG_NO_COMM :
            self.serialPort = serial.Serial(self.port,self.debit)
        
    def save_configuration(self) :
        self.config['debug'] = False
        if (self.debug) :
            self.config['debug'] = True
        save_config(self.config, CONFIG_FILENAME)
        return("Configuration saved")
        

    def run(self):
#        self.serialPort.write(str.encode('help\n'))
#        time.sleep(0.2)
        while True:
            if not DEBUG_NO_COMM :
                if self.serialPort.inWaiting():
    #                text = self.serialPort.readline(self.serialPort.inWaiting())
                    try:
                        text = self.serialPort.readline(self.serialPort.inWaiting()).decode("utf-8")
                    except :
                        print("Error reading Line\n")
                        continue    
                    text = text.replace("\r","\r\n")
                    self.queue.put(text)
                
    def send_frame(self, s):
        if not DEBUG_NO_COMM :
            self.serialPort.write(str.encode(s + "\n\r"))
        
class IHK_Serial(object):

    def __init__(self) :
        self.config = load_config(CONFIG_FILENAME)
        self.port = self.config['comport']
        self.debit = self.config['baudrate']
        self.debug = False
        if (self.config['debug']):
            self.debug = True

    def save_configuration(self) :
        self.config['debug'] = False
        if (self.debug) :
            self.config['debug'] = True
        save_config(self.config, CONFIG_FILENAME)
        print("Configuration saved")
            
    def configure(self):
        print(".........................................")
        print("Serial port configuration")
        print(".........................................")
        print("List of serial ports ...")
        results = serial_ports()
        config = load_config(CONFIG_FILENAME)
        print("[-] : Do not change (" + config['comport'] + " selected) [Default]")
        for i in (range(1, len(results) + 1)) :
            print("[" + str(i) + '] : ' + results[i - 1])
        try:
            selected = input("Type the Uart port to use and press <Enter> : ")
        except ValueError:
            pass
        if (selected != "0") and (selected != ""):
            self.port = results[int(selected) - 1]
            self.config['comport'] = self.port
            save_config(self.config, CONFIG_FILENAME)
            print("Configuration saved")
            
    def open(self):        
        self.serialPort = serial.Serial(self.port, self.debit, timeout=0)
        
    def read_frame(self):
        ret = dict([('err', ERR_IHK_SERIAL_NO_FRAME), ('str', "")])
        
        ret['err'] = ERR_IHK_SERIAL_NO_FRAME
        line = self.serialPort.read(128)
        for i in range(len(line)) :
            ret['str'] = ret['str'] + chr(line[i])

    def write_frame(self, str):
        self.serialPort.write(str.encode(str + "\n"))
            
    def send_frame(self, str, timeout=0.1, display_received_data = False):
        str_serial = []
        self.serialPort = serial.Serial(self.port, self.debit, timeout=timeout)

        self.serialPort.write((str + '\r\n').encode('utf-8'))
        
        if (self.debug) :
            print(">> Send : " + str)

        err = self.receive_frame()
        if (err['str'] != "") :
            if (self.debug) :
                print("<< Receive : " + err['str'])
            elif (display_received_data) :
                print(err['str'])
        self.serialPort.close()
        return err
        
    def receive_frame(self) :
        ret = dict([('err', ERR_IHK_SERIAL_NO_FRAME), ('str', "")])

        while (True) :
            ret['err'] = ERR_IHK_SERIAL_NO_FRAME
            line = self.serialPort.read(128)
            if (line == b'') :
                return ret
            ret['err'] = ERR_IHK_SERIAL_OK
            for i in range(len(line)) :
                ret['str'] = ret['str'] + chr(line[i])
#            return(ret)
    
    def receive_alive_frame(self) :
        ret = self.send_frame(str = "version",display_received_data = True)

    
    def connect(self) :
        self.m_compteurTickFrames = 0
        print("Connect to the product ...")
        
        self.receive_alive_frame()
        



    
