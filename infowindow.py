#!/usr/bin/env python
# -*- coding: utf-8 -*-
# info window for viewing general info about parameter


import pygtk
pygtk.require('2.0')
import gtk

from storage import *
from descriptionparser import *

class InfoWindow:
    def __init__(self, dpfilename):
        self.dpfilename = dpfilename
        self.param_path=None
        self.dp = DescriptionParser()
        self.dp.setXMLFileName(self.dpfilename)
            
        self.infoWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.infoWindow.set_position(gtk.WIN_POS_CENTER)
        infoVBox = gtk.VBox(False,10)
        infoFrame = gtk.Frame("Info")
        infoVBox.pack_start(infoFrame,True,True,0)

        infoButtonBox = gtk.HBox(True,10)
             
        self.closeButton = gtk.Button("Close")

        infoButtonBox.pack_start(self.closeButton,True,True,0)
        infoVBox.pack_start(infoButtonBox,False,True,0)        
        
        self.infoText = gtk.Label()
        self.infoText.set_alignment(0, 0)
        self.infoText.set_padding(2, 2)

        infoScroll = gtk.ScrolledWindow()
        infoScroll.set_border_width(5)
        infoScroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        infoScroll.add_with_viewport(self.infoText)
        infoScroll.set_shadow_type(gtk.SHADOW_NONE)
        infoFrame.add(infoScroll)                
        
        self.infoWindow.set_modal(True)
        self.infoWindow.set_border_width(10)
        self.infoWindow.set_size_request(610,305)
        self.infoText.set_line_wrap(True)
        self.infoText.set_width_chars(81)
        
        self.infoWindow.add(infoVBox)
        self.closeButton.connect("clicked", self.closeClick)        
        
    def show_info(self, param_path):
        self.param_path = param_path
        self.infoWindow.set_title("info about " + param_path)
        self.setInfoTextFromParam()                       
        self.infoWindow.show_all()               
        
    def closeClick(self, button):
        self.infoWindow.hide_all()
        
    def setInfoTextFromParam(self):
        param_info = self.dp.getInfo(self.param_path)
        if param_info!=None:
            self.infoText.set_text(param_info)
        else:
            self.infoText.set_text("")
