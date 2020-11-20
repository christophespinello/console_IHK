#!/usr/bin/python3

import tkinter as tk
from ihk_serial import SerialThread
import threading
import queue
import json
import time

JSON_FILENAME = "./ihk_tests.json"

DEBUG = 0

class Console_GUI_IHK(tk.Tk):
    def __init__(self) :
        tk.Tk.__init__(self)
        
#        self.root = tk.Tk() # Création de la fenêtre racine
        self.title('ConsoleGUI')
        self.geometry("720x480")

        self.json_filename = JSON_FILENAME
    
        with open(self.json_filename, 'r') as f:
            self.macros = json.load(f)      
            
#================================================================
# LabelFrame Actions        
#================================================================
        self.l_actions = tk.LabelFrame(self, text="Actions")
        self.l_actions.pack(fill=tk.BOTH, expand=tk.YES)
             
# Vertical (y) Scroll Bar
        self.scroll_actions = tk.Scrollbar(self.l_actions)
        self.scroll_actions.pack(side=tk.RIGHT, fill=tk.Y)
        
# Liste des macros        
        self.listbox = tk.Listbox(self.l_actions)
        self.listbox.pack(fill=tk.X)

        for macro in self.macros :
            self.listbox.insert(tk.END,macro['command'] + "(" + macro['description'] + ")")

#================================================================
# LabelFrame Activite        
#================================================================
        self.l_activite = tk.LabelFrame(self, text="Activite", padx=10, pady=10)
        self.l_activite.pack(fill=tk.X, expand=tk.YES)

#================================================================
# LabelFrame Envoi        
#================================================================
        self.l_envoi = tk.LabelFrame(self.l_activite, text="Envoi", padx=10, pady=10)
        self.l_envoi.pack(fill=tk.X, expand=tk.YES)
        
        self.l_envoi.grid_columnconfigure(0, weight=10)
        self.l_envoi.grid_columnconfigure(1, weight=1)

        #Partie envoi
        self.entry = tk.Entry(self.l_envoi)
        self.entry.grid(row=0, column=0,sticky=tk.W+tk.E)
        #entry.pack(fill=X, expand=YES)
        #entry.pack(fill = BOTH,expand=YES)
        
        self.button_send = tk.Button(self.l_envoi,text="Send",command=self.send)
        self.button_send.grid(row=0, column=1)
        self.bind('<Return>',self.event_key_return)
        #button_send.pack()
        
#================================================================
# LabelFrame Dialogue        
#================================================================
        self.l_traffic = tk.LabelFrame(self.l_activite, text="Dialogue", padx=10, pady=10)
        self.l_traffic.pack(fill=tk.X, expand=tk.YES)
        
        # Vertical (y) Scroll Bar
        self.scroll = tk.Scrollbar(self.l_traffic)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.textzone = tk.Text(self.l_traffic,height=10, yscrollcommand=self.scroll.set)
        self.textzone.pack(fill = tk.BOTH,expand=tk.YES)
        self.textzone.tag_config('send', foreground="blue")
        self.textzone.tag_config('receive', foreground="green")
        self.textzone.tag_config('comment', foreground="black")
        self.textzone.tag_config('error', foreground="red")
        
#================================================================
# LabelFrame Commande        
#================================================================
        self.l_command = tk.LabelFrame(self, text="Commands", padx=10, pady=10)
        self.l_command.pack(fill=tk.X, expand=tk.YES)
        self.l_command.grid_columnconfigure(0, weight=1)
        self.l_command.grid_columnconfigure(1, weight=1)
        self.l_command.grid_columnconfigure(2, weight=1)
        
        self.button_options = tk.Button(self.l_command,text='OPTIONS')
        self.button_options.grid(row=0, column=0,sticky=tk.W+tk.E,padx=20)
        
        self.button_clear = tk.Button(self.l_command,text='CLEAR')
        self.button_clear.grid(row=0, column=1,sticky=tk.W+tk.E,padx=20)

        self.button_quit = tk.Button(self.l_command,text='QUIT')
        self.button_quit.grid(row=0, column=2,sticky=tk.W+tk.E,padx=20)
 
        self.queue = queue.Queue()
        
        self.readThread = SerialThread(self.queue)
        self.readThread.start()
        self.processConsole()  
            
    def processConsole(self) :
        while self.queue.qsize():
            try:
                new=self.queue.get()
                self.textzone.insert(tk.END,new,"receive")
                self.textzone.see(tk.END)
            except queue.Empty:
                pass
        self.after(100, self.processConsole)
      
    def send(self):
        if self.entry.get() == "":
            if len(self.listbox.curselection()) == 0 :
                self.textzone.insert(tk.END,"No command to send" + "\n","error")
            else :
                self.send_macro(self.listbox.curselection()[0])
        else :
            self.readThread.send_frame(self.entry.get())
            self.textzone.insert(tk.END,self.entry.get() + "\n","send")
        self.entry.delete(0, tk.END)
        
    def send_macro(self,index):
        i = 0
        for macro in self.macros :
            if (i == index) :
                self.textzone.insert(tk.END,"Macro " + macro['command'] + "\n","comment")
                for action in macro['action'] :
                    if (action[:5] == "SLEEP") :
                        time.sleep(int(action[6:]))
                        self.textzone.insert(tk.END,action + "\n","comment")
                    else :                                                
                        self.readThread.send_frame(action)
                        self.textzone.insert(tk.END,action + "\n","send")
            i = i+1
        
        
            
    def event_key_return(self,event):
        self.send()
        
if __name__ == '__main__':
    app=Console_GUI_IHK()
    app.mainloop() 
    # Lancement de la boucle principale
