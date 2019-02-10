##############################################################################
# cls_DashBoard.py
#
# this is the GUI for Reefberry Pi.  This implementation is written 
# using tKinter and is a native application to run on the
# Raspberry Pi
#
# Written by ReefSpy for the ReefBerry Pi, (c) 2019
# www.youtube.com/reefspy
##############################################################################

import tkinter as tk
from tkinter import * 
from tkinter import ttk
from tkinter import messagebox


class SplashPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        
        logocanvas=Canvas(self,width=250,height=250)
        logocanvas.pack()

        self.img=PhotoImage(file="images/reefberrypi_logo2.gif")
        logocanvas.create_image(0,0,image=self.img, anchor=NW)
