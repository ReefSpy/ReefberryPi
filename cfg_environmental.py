import tkinter as tk
from tkinter import *
from tkinter import ttk
import cfg_common

LARGE_FONT= ("Verdana", 12)

class PageEnvironmental(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Environmental Sensors", font=LARGE_FONT)
        label.grid(row=0, column=0, pady=10, sticky=W)

        # top frame for toolbar
        #self.frame_toolbar = LabelFrame(self, relief= FLAT)
        #self.frame_toolbar.pack(fill=X, side=TOP)
        
        # save button
        self.saveimg=PhotoImage(file="images/save-blue-24.png")
        self.btn_save = Button(self, text="Save", image=self.saveimg,
                               compound='left', relief=RAISED, command=self.saveChanges)
        self.btn_save.grid(row=1, column=0, sticky=W)

        # dht11/22 
        self.dhtframe = LabelFrame(self, text="DHT11/22 Temperature and Humidity Sensor", relief=GROOVE)
        self.dhtframe.grid(row=2, column=0, pady=10)

        # enable sensor
        self.dhtEnabled = IntVar()
        self.chk_dhtenable = Checkbutton(self.dhtframe,text="Enable Sensor",
                                         variable=self.dhtEnabled, command=self.enableControls)
        self.chk_dhtenable.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        
        # temperature
        self.lbl_dhttemp = Label(self.dhtframe,text="Temperature Sensor Name:")
        self.lbl_dhttemp.grid(row=1, column=0, sticky=E, padx=10, pady=5)
        self.txt_dhttemp = Entry(self.dhtframe)
        self.txt_dhttemp.grid(row=1, column=1, padx=10, pady=5)

        # humidity
        self.lbl_dhthum = Label(self.dhtframe,text="Humidity Sensor Name:")
        self.lbl_dhthum.grid(row=2, column=0, sticky=E, padx=10, pady=5)
        self.txt_dhthum = Entry(self.dhtframe)
        self.txt_dhthum.grid(row=2, column=1, padx=10, pady=5)

        # read values from config file
        enabledht = cfg_common.readINIfile("dht11/22", "enabled", "False")
        if str(enabledht) == "True":
            self.chk_dhtenable.select()
        else:
            self.chk_dhtenable.deselect()

        tempname = cfg_common.readINIfile("dht11/22", "temperature_name", "Ambient Temperature")
        self.txt_dhttemp.delete(0,END)
        self.txt_dhttemp.insert(0,tempname)
       
        humname = cfg_common.readINIfile("dht11/22", "humidity_name", "Humidity")
        self.txt_dhthum.delete(0,END)
        self.txt_dhthum.insert(0,humname)

        # enable/disable controls
        self.enableControls()
        
    def enableControls(self):
        #print('dhtEnabled = ' + str(self.dhtEnabled.get()))
        if self.dhtEnabled.get() == True:
            self.lbl_dhttemp.config(state='normal')
            self.txt_dhttemp.config(state='normal')
            self.lbl_dhthum.config(state='normal')
            self.txt_dhthum.config(state='normal')
        else:
            self.lbl_dhttemp.config(state='disabled')
            self.txt_dhttemp.config(state='disabled')
            self.lbl_dhthum.config(state='disabled')
            self.txt_dhthum.config(state='disabled')
            
            
            

    def saveChanges(self):
        # enabled setting
        if self.dhtEnabled.get() == True:
            chkstate = "True"
        else:
            chkstate = "False"
            
        if cfg_common.writeINIfile('dht11/22', 'enabled', str(chkstate)) != True:
           messagebox.showerror("Environmental Settings",
                                 "Error: Could not save changes! \nNew configuration not saved.")
        # temperature name
        if cfg_common.writeINIfile('dht11/22', 'temperature_name', str(self.txt_dhttemp.get())) != True:
             messagebox.showerror("Environmental Settings",
                                 "Error: Could not save changes! \nNew configuration not saved.")
            
        # humidity name 
        if cfg_common.writeINIfile('dht11/22', 'humidity_name', str(self.txt_dhthum.get())) != True:
            messagebox.showerror("Environmental Settings",
                                 "Error: Could not save changes! \nNew configuration not saved.")
        
        
        

