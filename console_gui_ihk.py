#!/usr/bin/python3

from utils import load_config, save_config
import tkinter as tk
from cli_serial import SerialThread
import threading
import queue
import json
import time
import sys
from tkinter import * 
from tkinter.ttk import *

CONFIG_FILENAME = './config.yml'

VERSION = "1.0.4"

DEBUG = 0

class CLI_Console_GUI(tk.Tk):
    def __init__(self) :
        tk.Tk.__init__(self)
        
        self.config = load_config(CONFIG_FILENAME)
        self.port = self.config['comport']
        self.json_filename = self.config['json_filename']
        
        self.title("CLIConsoleGUI - JSON Filename :" + self.json_filename + " - Comport : " + self.port + " Version : " + VERSION)
        self.geometry("800x480")

        with open(self.json_filename, 'r') as f:
            self.macros = json.load(f)      
            
#================================================================
# Construction fenetres principale        
#================================================================
        self.grid_columnconfigure(0, weight=100)
        self.grid_columnconfigure(1, weight=0)

        self.grid_rowconfigure(0, weight=1)
        
        self.l_dialogue = tk.LabelFrame(self, text="Dialog", width = "500")
        self.l_dialogue.grid(row=0, column=0,sticky=tk.N+tk.S+tk.E+tk.W)

        self.l_command = tk.LabelFrame(self, text="Commands", padx=10, pady=10,width = "50")
        self.l_command.grid(row=0, column=1,sticky=tk.N+tk.S+tk.E+tk.W)

#================================================================
# LabelFrame dans dialogue        
#================================================================
 
#================================================================
# LabelFrame Macros        
#================================================================
        self.l_dialogue.grid_columnconfigure(0, weight=1)

        self.l_dialogue.grid_rowconfigure(0, weight=5)
        self.l_dialogue.grid_rowconfigure(1, weight=5)
        self.l_dialogue.grid_rowconfigure(2, weight=1)
        self.l_dialogue.grid_rowconfigure(3, weight=5)

        self.l_macros = tk.LabelFrame(self.l_dialogue, text="Macros",padx=2, pady=2)
        self.l_macros.grid(row=0, column=0,sticky=tk.W+tk.E)
 
# Vertical (y) Scroll Bar
        self.scroll_macros = tk.Scrollbar(self.l_macros)
        self.scroll_macros.pack(side=tk.RIGHT, fill=tk.Y)

        self.l_commentaires = tk.LabelFrame(self.l_dialogue, text="Description",padx=2, pady=2)
        self.l_commentaires.grid(row=1, column=0,sticky=tk.W+tk.E)

#        self.commentaires_textzone = tk.Scrollbar(self.l_commentaires)
#        self.commentaires_textzone.pack(side=tk.RIGHT, fill=tk.Y)
        self.commentaires_textzone = tk.Label(self.l_commentaires,height=2)
        self.commentaires_textzone.pack(side=tk.LEFT) #fill = tk.BOTH,expand=tk.NO)
        self.commentaires_textzone.config(state=tk.DISABLED)         
# Liste des macros        
        self.listbox = tk.Listbox(self.l_macros,yscrollcommand=self.scroll_macros,height=5)
        self.listbox.pack(fill=tk.X)
        self.listbox.bind('<Double-Button-1>',self.event_key_return)
 
        for macro in self.macros :
            self.listbox.insert(tk.END,macro['command'] )
#"(" + macro['description'] + ")" 
        self.scroll_macros.config(command = self.listbox.yview)
        self.listbox.bind('<<ListboxSelect>>',self.event_listbox_click)
         
#================================================================
# LabelFrame Envoi        
#================================================================
        self.l_envoi = tk.LabelFrame(self.l_dialogue, text="Envoi", padx=2, pady=2)
        self.l_envoi.grid(row=2, column=0,sticky=tk.W+tk.E)
         
        #Partie envoi
        self.entry = tk.Entry(self.l_envoi)
        self.entry.pack(fill=tk.BOTH)
         
#================================================================
# LabelFrame Dialogue        
#================================================================
        self.l_traffic = tk.LabelFrame(self.l_dialogue, text="Communication receive")
        self.l_traffic.grid(row=3, column=0,sticky=tk.W+tk.E)
         
        # Vertical (y) Scroll Bar
        self.scroll_textzone = tk.Scrollbar(self.l_traffic)
        self.scroll_textzone.pack(side=tk.RIGHT, fill=tk.Y)
 
        self.textzone = tk.Text(self.l_traffic,height=10,width=self.entry.winfo_width(), yscrollcommand=self.scroll_textzone.set)
        self.textzone.pack(fill = tk.BOTH,expand=tk.YES)
 
        self.textzone.tag_config('send', foreground="blue")
        self.textzone.tag_config('receive', foreground="green")
        self.textzone.tag_config('comment', foreground="black")
        self.textzone.tag_config('error', foreground="red")
        self.textzone.tag_config('macro', foreground="orange")
 
#================================================================
# LabelFrame Commande        
#================================================================
              
        self.l_command.grid_rowconfigure(0, weight=1)
        self.l_command.grid_rowconfigure(1, weight=1)
        self.l_command.grid_rowconfigure(2, weight=1)
        self.l_command.grid_rowconfigure(3, weight=1)
         
        self.button_send = tk.Button(self.l_command,text="SEND", command=self.send, width="20", height="5")
        self.button_send.grid(row=0, column=0,sticky=tk.W+tk.E,padx=1, pady=20)
        self.bind('<Return>',self.event_key_return)
 
#        self.button_options = tk.Button(self.l_command,text='OPTIONS')
#        self.button_options.grid(row=1, column=0,sticky=tk.W+tk.E,padx=20)
         
        self.button_clear = tk.Button(self.l_command,text='CLEAR',command=self.clear)
        self.button_clear.grid(row=1, column=0,sticky=tk.W+tk.E,padx=10, pady=10)
 
        self.button_quit = tk.Button(self.l_command,text='QUIT',command=self.destroy)
        self.button_quit.grid(row=2, column=0,sticky=tk.W+tk.E,padx=10)
 
        self.queue = queue.Queue()
        self.queueSend = queue.Queue()
        
        self.readThread = SerialThread(self.queue)
        self.readThread.start()
        self.processConsole()  
            
    def processConsole(self) :
        while self.queue.qsize():
            try:
                new=self.queue.get()
                self.textzone.insert(tk.END,new,"receive")
                self.textzone.see(tk.END)
                self.textzone.update()
            except self.queue.Empty:
                pass
        if self.queueSend.qsize():
            try:
                new=self.queueSend.get()
                str_cmd = new.split(" ")
                if (str_cmd[0] == "SLEEP") :
                    self.textzone.insert(tk.END,new,"comment")
                    self.textzone.see(tk.END)
                    self.textzone.update()
                    time.sleep(int(str_cmd[1]))
                elif (str_cmd[0] == "GOTO" ):
                    self.send_macro(self.listbox.curselection()[0],str_cmd[1])
                else :
                    self.readThread.send_frame(new)
                    self.textzone.insert(tk.END,new,"send")
                    self.textzone.see(tk.END)
                    self.textzone.update()
            except self.queueSend.Empty:
                pass
        else :
            self.button_send['text'] = "SEND" 
        self.after(100, self.processConsole)
      
    def send(self):
        if (self.button_send['text'] == "STOP") :
            with self.queueSend.mutex :
                self.queueSend.queue.clear()
            self.button_send['text'] = "SEND" 
        else :
            self.button_send['text'] = "STOP" 
            if self.entry.get() == "":
                if len(self.listbox.curselection()) == 0 :
                    self.textzone.insert(tk.END,"No command to send" + "\n","error")
                else :
                    self.send_macro(self.listbox.curselection()[0])
            else :
                self.readThread.send_frame(self.entry.get())
                self.textzone.insert(tk.END,self.entry.get() + "\n","send")
            self.entry.delete(0, tk.END)
        
    def send_macro(self,index,label=""):
        i = 0
        for macro in self.macros :
            if (i == index) :
                if (label == "") :
                    self.textzone.insert(tk.END,"Macro " + macro['command'] + "\n","macro")
                detection_label = False;    
                if (label == "") :
                    detection_label = True;  
                for action in macro['action'] :
                    if ( action[0] == ":") : 
                        if ( not detection_label ) : 
                            if ( action[1:] == label[:len(label)-1] ) :
                                detection_label = True
                    else :            
                        if (detection_label) :
                            self.queueSend.put(action + "\n")                   
            i = i+1
        
    def event_key_return(self,event):
        self.send()

    def event_listbox_click(self,event):
        self.commentaires_textzone.config(state=tk.NORMAL)         

#        self.commentaires_textzone.delete(1.0,tk.END)        
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.commentaires_textzone['text'] = self.macros[index]['description'].encode('utf-8')
#            self.commentaires_textzone.update()
            
        self.commentaires_textzone.config(state=tk.DISABLED)         

    def clear(self) :
        self.textzone.delete(1.0,tk.END)
        
          
if __name__ == '__main__':
    app=CLI_Console_GUI()
    app.mainloop()     # Lancement de la boucle principale
    
