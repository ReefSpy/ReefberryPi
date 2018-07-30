import tkinter as tk
from tkinter import *
from tkinter import ttk
import glob

LARGE_FONT= ("Verdana", 12)

class PageTempProbes(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # create dictionary to hold assigned probes
        self.probeDict = {}

        label = tk.Label(self, text="Temperature Probes", font=LARGE_FONT)
        label.pack(side=TOP, pady=10, anchor=W)

        ###########################################################################
        # frame temperature probes
        ###########################################################################
        self.frame_DS18B20 = LabelFrame(self, text="DS18B20 Temperature Probes", relief= RAISED)
        self.frame_DS18B20.pack(fill=X, side=TOP)

        # probe
        self.unassignedprobeframe = LabelFrame(self.frame_DS18B20, relief= FLAT)
        self.unassignedprobeframe.pack(fill=X, side=TOP)
        self.lbl_probe = Label(self.unassignedprobeframe,text="Unassigned Probes:")
        self.lbl_probe.pack(side=TOP, anchor=W, padx=10)

        # listbox to display connected probes
        self.lst_probes = Listbox(self.unassignedprobeframe,  height=5)
        self.lst_probes.pack(side=TOP, anchor=W, padx=10)

        # button to activate probe
        self.btn_activateprobe = Button(self.unassignedprobeframe,text="Activate Probe",
                                   command=self.displayProbe)
        self.btn_activateprobe.pack(side=TOP, anchor=W, padx=10, pady=10)

        self.getProbes()
        
    def getProbes(self):
        try:
            base_dir = '/sys/bus/w1/devices/' 
            device_folder = glob.glob(base_dir + '28*')

            # we need to clear widget so we can refresh with current list
            # first grab current selection to it is still highlited after refresh
            selection = self.lst_probes.curselection()
            self.lst_probes.delete(0, END)
            
            for d in device_folder:
                #print(d.split("/")[-1])
                self.lst_probes.insert(END, d.split("/")[-1])
            # set back to what was slected
            self.lst_probes.activate(selection)
            self.lst_probes.selection_set(selection)
        except:
            #print("Exception getProbes(self):")
            pass
        
        self.after(2000,self.getProbes)

    def displayProbe(self):
        self.probeDict[self.lst_probes.get(ACTIVE)]=self.lst_probes.get(ACTIVE)
        print (self.probeDict)
        # probe frame
        self.probeframe = LabelFrame(self.frame_DS18B20, relief= SUNKEN)
        self.probeframe.pack(fill=X, side=TOP)
        self.lbl_probeSN = Label(self.probeframe,text="ID: " + self.lst_probes.get(ACTIVE))
        self.lbl_probeSN.pack(side=TOP, anchor=W, padx=10)
        self.probenameframe = LabelFrame(self.probeframe, relief= FLAT)
        self.probenameframe.pack(fill=X, side=TOP)
        self.lbl_probename = Label(self.probenameframe,text="Name:")
        self.lbl_probename.pack(side=LEFT, anchor=W, padx=10)
        self.txt_probename = Entry(self.probenameframe)
        self.txt_probename.pack(side=LEFT, anchor=W, padx=10)
        self.probestateframe = LabelFrame(self.probeframe, relief= FLAT)
        self.probestateframe.pack(fill=X, side=TOP)
        self.lbl_probestate = Label(self.probestateframe,text="State:")
        self.lbl_probestate.pack(side=LEFT, anchor=W, padx=10)
        self.lbl_probestatecur = Label(self.probestateframe, text="{testing} Connected", foreground='GREEN')
        self.lbl_probestatecur.pack(side=LEFT, anchor=W, padx=10)
        
    #def readExistingProbes(self):
        
