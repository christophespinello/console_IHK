#!/usr/bin/python3
# -*- coding: utf8 -*-

import time
from ihk_serial import IHK_Serial

import json
from test_loop import test_loop

#SOFTWARE_VERSION = '1.0.21'
with open ("VERSION", "r") as myfile:
    SOFTWARE_VERSION=myfile.readline()
    
JSON_FILENAME = "./ihk_tests.json"

DEBUG = 0

class ConsoleIHK(object):

    def __init__(self) :
        
        self.console_serial = IHK_Serial()
        self.ptr_sequencer = 'SEQ_INIT'
        self.running = True
        self.test_loop = test_loop(interface=self.console_serial, json_filename=JSON_FILENAME)
        self.sequencer(self.ptr_sequencer)
            
    def seq_init(self):
        print("=========================================")
        print("         console ZEHNDER IHK")
        print("                                  v" + SOFTWARE_VERSION)
        print("=========================================")
        if (DEBUG == 1) :
            self.ptr_sequencer = 'SEQ_LOOP'
        else :
            self.ptr_sequencer = 'SEQ_CONFIGURE_CONNECTION'

    def seq_configure_connection(self):
        self.console_serial.configure()
        self.ptr_sequencer = 'SEQ_CONNECT'
        
    def seq_connect(self):
        self.console_serial.connect()
        self.ptr_sequencer = 'SEQ_CONFIGURE_PRODUCT'

    def seq_configure_product(self):
        self.ptr_sequencer = 'SEQ_LOOP'
            
    def seq_idle(self):
        self.ptr_sequencer = 'SEQ_IDLE'

    def seq_loop(self):
        self.test_loop.main()
        self.ptr_sequencer = 'SEQ_LOOP'
            
    def sequencer(self, argument) :
        self.ptr_sequencer = argument
        while self.running:
            func = self.steps_sequencer.get(self.ptr_sequencer, "nothing")
            func(self)
        
    steps_sequencer = {
        'SEQ_INIT' : seq_init,
        'SEQ_CONFIGURE_CONNECTION' : seq_configure_connection,
        'SEQ_CONNECT' : seq_connect,
        'SEQ_CONFIGURE_PRODUCT' : seq_configure_product,
        'SEQ_IDLE' : seq_idle,
        'SEQ_LOOP' : seq_loop
        }
        
    
if __name__ == "__main__":
    ConsoleIHK()
