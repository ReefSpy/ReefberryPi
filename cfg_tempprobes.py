import tkinter as tk
from tkinter import *
from tkinter import ttk
import glob
import cfg_common
import configparser
from datetime import datetime

LARGE_FONT= ("Verdana", 12)

class PageTempProbes(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # create dictionary to hold assigned probes
        # these are probes that are already saved in config file
        self.probeDict = {}
        # and these are the new unsaved probes
        self.newprobeDict = {}

        label = tk.Label(self, text="Temperature Probes", font=LARGE_FONT)
        label.pack(side=TOP, pady=10, anchor=W)

        # top frame for toolbar
        self.frame_toolbar = LabelFrame(self, relief= FLAT)
        self.frame_toolbar.pack(fill=X, side=TOP)
        # save button
        self.saveimg=PhotoImage(file="images/save-blue-24.png")
        self.btn_save = Button(self.frame_toolbar, text="Save", image=self.saveimg,
                               compound='left', relief=RAISED, command=self.saveChanges)
        self.btn_save.pack(side=TOP, anchor=W, pady=5)

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

        # button to assign probe
        self.btn_assignprobe = Button(self.unassignedprobeframe,text="Assign Probe",
                                   command=self.assignProbe)
        self.btn_assignprobe.pack(side=TOP, anchor=W, padx=10, pady=10)

        self.getConnectedProbes()
        self.readExistingProbes()
        for i in self.probeDict:
            print("Probe dict id: " + str(self.probeDict[i].probeid))
            print("Probe dict name: " + str(self.probeDict[i].probeid))
        
    def getConnectedProbes(self):
        try:
            self.readExistingProbes()
            base_dir = '/sys/bus/w1/devices/' 
            device_folder = glob.glob(base_dir + '28*')

            # we need to clear widget so we can refresh with current list
            # first grab current selection to it is still highlited after refresh
            selection = self.lst_probes.curselection()
            self.lst_probes.delete(0, END)
            addtolist = True
            newprobeID = ""
            for d in device_folder:
                newprobeid = d.split("/")[-1]
                #print("looking to match: " + newprobeid)
                for p in self.probeDict:
                    #print("testing against = " + self.probeDict[p].probeid)
                    if str(d.split("/")[-1]) == str(self.probeDict[p].probeid):
                        addtolist = False
                        #print("addtolist = " + str(addtolist))
                        break
                    else:
                        addtolist = True
                        #print("Match = " + str(addtolist))
                if addtolist == True:
                    #print ("Inserting " + newprobeid + " to list")
                    self.lst_probes.insert(END, newprobeid)

            # set back to what was slected
            try:
                self.lst_probes.activate(selection)
                self.lst_probes.selection_set(selection)
            except:
                #print("Error selecting listbox index")
                pass
        except:
            #print("Exception getProbes(self):")
            pass
        
        self.after(2000,self.getConnectedProbes)

    def assignProbe(self):
        self.probe = ProbeClass()
        self.probe.probeid = self.lst_probes.get(ACTIVE)
        self.probe.name = "Temperature"
        self.newprobeDict[self.lst_probes.get(ACTIVE)]=self.probe
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " +
                      "Assigned probe: " + "ID = " + self.probe.probeid + ", Name = " + self.probe.name)
        print(self.newprobeDict[self.probe.probeid].probeid)
        print(self.newprobeDict[self.probe.probeid].name)
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
        
    def saveChanges(self):
        print("Enter saveChanges")
        print(self.newprobeDict)
        for probe in self.newprobeDict:
            print(self.newprobeDict[probe].probeid)
            #cfg_common.writeINIfile('ds18b20_' + probe, probe, 0)
            if cfg_common.writeINIfile('ds18b20_' + self.newprobeDict[probe].probeid, "name", "1"):
                messagebox.showinfo("Global Settings",
                                "New configuration saved succesfully.")
                # remove this key from unsaved probe list
                del self.newprobeDict[probe]
            else:
                messagebox.showerror("Global Settings",
                                 "Error: Could not save changes! \nNew configuration not saved.")
        
            print(probe)
            print(self.frame_DS18B20.winfo_children())

        

    def readExistingProbes(self):
        # clear out the old probe dictionary
        self.probeDict.clear()
        config = configparser.ConfigParser()
        config.read(cfg_common.CONFIGFILENAME)
        # loop through each section and see if it is a ds18b20 temp probe
        for section in config:
            if section.split("_")[0] == "ds18b20":
                #print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " +
                #      "Read existing temp probe: " + section.split("_")[1])
                #print (section.split("_")[1])
                probe = ProbeClass()
                probe.probeid = section.split("_")[1]
                self.probeDict [section.split("_")[1]] = probe
                #print("probe class id: " + probe.probeid)
                #print("probe class name: " + probe.name)
            
            

class ProbeClass:
    name = ""
    probeid = ""
    
