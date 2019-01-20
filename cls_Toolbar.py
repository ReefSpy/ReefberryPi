##############################################################################
# cls_Toolbar.py
#
# toolbar implentation for RaspBerry Pi GUI app
#
# Written by ReefSpy for the ReefBerry Pi, (c) 2019
# www.youtube.com/reefspy
##############################################################################

import tkinter as tk
from tkinter import * 
from tkinter import ttk
import cls_DashBoard
import cls_GraphPage

class Toolbar(tk.Frame):

    def __init__(self, controller):
        
        #create toolbar frame
        frame_toolbar = tk.LabelFrame(controller, relief = tk.FLAT)
        frame_toolbar.pack(side=tk.TOP, fill=tk.X)

        self.img_dashboard = PhotoImage(file="images/dashboard-64.png")
        btn_DashBoard = ttk.Button(frame_toolbar, text="Dashboard", image=self.img_dashboard, 
                            compound=TOP, command=lambda: controller.show_frame(cls_DashBoard.DashBoard))
        btn_DashBoard.pack(side=LEFT)

##        self.img_alarm = PhotoImage(file="images/notification-64.png")
##        button = ttk.Button(frame_toolbar, text="Alarm Log", image=self.img_alarm,
##                            compound=TOP, command=lambda: controller.show_frame(PageOne))
##        button.pack(side=LEFT)
##
##        self.img_testlog = PhotoImage(file="images/test-tube-64.png")
##        button2 = ttk.Button(frame_toolbar, text="Test Log", image=self.img_testlog,
##                            compound=TOP, command=lambda: controller.show_frame(PageTwo))
##        button2.pack(side=LEFT)

        self.img_graph = PhotoImage(file="images/line-chart-64.png")
        button3 = ttk.Button(frame_toolbar, text="Graphs", image=self.img_graph,
                            compound=TOP, command=lambda: controller.show_frame(cls_GraphPage.GraphPage))
        button3.pack(side=LEFT)
