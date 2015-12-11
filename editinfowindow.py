#!/usr/bin/env python
# -*- coding: utf-8 -*-
# window for settings edition (displays when user press "Settings" button)

import pygtk
pygtk.require('2.0')
import gtk, gobject
import gettext

from descriptionparser import *

class EditInfoWindow:

    def __init__(self, dp, paramview, gettext):
        self.param_path=None
        self.dp = dp
        self.paramview = paramview
        attrs=None
        _=gettext.gettext
        
        self.editInfoWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.editInfoWindow.set_position(gtk.WIN_POS_CENTER)
        self.editInfoVBox = gtk.VBox(False,10)
        self.editInfoSubVBox = gtk.VBox(False,10)
        self.editInfoHBox = gtk.HBox(False,10)

        # Frame, TextBufferm, TextView and stuff for general info editor
        self.generalInfoFrame = gtk.Frame()
        self.generalInfoText = gtk.TextBuffer()
        self.generalInfoTextView = gtk.TextView(self.generalInfoText)
        self.generalInfoTextView.set_left_margin(2)
        self.generalInfoTextView.set_editable(True)
        self.generalInfoTextView.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.generalInfoScroll = gtk.ScrolledWindow()
        self.generalInfoScroll.set_border_width(5)
        self.generalInfoScroll.set_policy(gtk.POLICY_AUTOMATIC,
                                          gtk.POLICY_AUTOMATIC)
        self.generalInfoScroll.add(self.generalInfoTextView)
        self.generalInfoScroll.set_shadow_type(gtk.SHADOW_NONE)
        self.generalInfoFrame.add(self.generalInfoScroll)
        self.editInfoSubVBox.pack_start(self.generalInfoFrame,True,True,0)

#       checkbox for "locked" attribute
        self.locked = gtk.CheckButton(_("Lock this parameter for editing"))
        self.editInfoSubVBox.pack_start(self.locked,False,False,0)        

        # Frame, TextBufferm, TextView and stuff for subparameter info editor
        self.subparamInfoFrame = gtk.Frame()
        self.subparamInfoText = gtk.TextBuffer()
        self.subparamInfoTextView = gtk.TextView(self.subparamInfoText)
        self.subparamInfoTextView.set_left_margin(2)
        self.subparamInfoTextView.set_editable(True)
        self.subparamInfoScroll = gtk.ScrolledWindow()
        self.subparamInfoScroll.set_border_width(5)
        self.subparamInfoScroll.set_policy(gtk.POLICY_AUTOMATIC,
                                          gtk.POLICY_AUTOMATIC)
        self.subparamInfoScroll.add(self.subparamInfoTextView)
        self.subparamInfoScroll.set_shadow_type(gtk.SHADOW_NONE)
        self.subparamInfoFrame.add(self.subparamInfoScroll)
        self.editInfoSubVBox.pack_start(self.subparamInfoFrame,True,True,0)        

        # Text entry for subparameter name
        self.subparamNameFrame = gtk.Frame(_("Subparameter name:"))
        self.subparamname = gtk.Entry()
        self.subparamNameFrame.add(self.subparamname)
        self.editInfoSubVBox.pack_start(self.subparamNameFrame,True,True,0)
        self.editInfoHBox.pack_start(self.editInfoSubVBox,True,True,0)
        
        # some widgets which set up subparameter data type
        self.subparamAppearFrame = gtk.Frame(_("Edit data type"))
        self.subparamAppearVBox = gtk.VBox(False,10)
        self.subparamAppearFrame.add(self.subparamAppearVBox)
        
        self.stringMode = gtk.RadioButton(None, _("String value"))
        self.subparamAppearVBox.pack_start(self.stringMode,True,True,0)
        
        self.maxlenlabel = gtk.Label(_("Maximum length:"))
        self.maxlenlabel.set_alignment(0, 0)
        self.maxlenlabel.set_padding(2, 2)
        self.subparamAppearVBox.pack_start(self.maxlenlabel,True,True,0)

        self.maxlen = gtk.Entry()
        self.subparamAppearVBox.pack_start(self.maxlen,True,True,0)
        
        self.separator = gtk.HSeparator()
        self.subparamAppearVBox.pack_start(self.separator,True,True,0)
        
        self.intMode = gtk.RadioButton(self.stringMode, _("Integer value"))
        self.subparamAppearVBox.pack_start(self.intMode,True,True,0)
        
        self.intModeCombo = gtk.combo_box_new_text()
        self.intModeCombo.append_text(_("range of numbers"))
        self.intModeCombo.append_text(_("list of number items"))
        self.subparamAppearVBox.pack_start(self.intModeCombo,True,True,0)        
        
        self.minnumlabel = gtk.Label(_("Minimal number value:"))
        self.minnumlabel.set_alignment(0, 0)
        self.minnumlabel.set_padding(2, 2)
        self.subparamAppearVBox.pack_start(self.minnumlabel,True,True,0)
        self.minnum = gtk.Entry()
        
        self.subparamAppearVBox.pack_start(self.minnum,True,True,0)
        self.maxnumlabel = gtk.Label(_("Maximal number value:"))
        self.maxnumlabel.set_alignment(0, 0)
        self.maxnumlabel.set_padding(2, 2)
        self.subparamAppearVBox.pack_start(self.maxnumlabel,True,True,0)
        self.maxnum = gtk.Entry()
        self.subparamAppearVBox.pack_start(self.maxnum,True,True,0)

        self.listvaluestore = gtk.ListStore(gobject.TYPE_INT,
                                            gobject.TYPE_STRING)        
        self.listvaluetreeview = gtk.TreeView(self.listvaluestore)
        self.listvalueselection = self.listvaluetreeview.get_selection()        
        self.listvaluecell_num = gtk.CellRendererText()
        self.listvaluecell_text = gtk.CellRendererText()
        self.listvaluecell_num.set_property('editable', True)
        self.listvaluecell_text.set_property('editable', True)        

        self.listvaluecolumn_num = gtk.TreeViewColumn(_("Value"), self.listvaluecell_num,markup=0)
        self.listvaluecolumn_text = gtk.TreeViewColumn(_("Description"), self.listvaluecell_text,markup=1)
        self.listvaluetreeview.append_column(self.listvaluecolumn_num)
        self.listvaluetreeview.append_column(self.listvaluecolumn_text)
        self.subparamAppearVBox.pack_start(self.listvaluetreeview,True,True,0)
        self.addremoveButtonBox = gtk.HBox(False,10)
        self.addButton = gtk.Button("+")
        self.removeButton = gtk.Button("-")
        self.addremoveButtonBox.pack_start(self.addButton,True,True,0)
        self.addremoveButtonBox.pack_start(self.removeButton,True,True,0)        
        self.subparamAppearVBox.pack_start(self.addremoveButtonBox,True,True,0)                
        
        self.editInfoHBox.pack_start(self.subparamAppearFrame,True,True,0)
        self.editInfoVBox.pack_start(self.editInfoHBox,True,True,0)        
        
        self.editInfoButtonBox = gtk.HBox(True,10)

        # et voila! here is the buttons
        self.saveButton = gtk.Button(_("Save settings"))
        self.editInfoButtonBox.pack_start(self.saveButton,True,True,0)        
        self.closeButton = gtk.Button(_("Close"))
        self.editInfoButtonBox.pack_start(self.closeButton,True,True,0)
        
        self.editInfoVBox.pack_start(self.editInfoButtonBox,False,True,0)        

        self.editInfoWindow.set_modal(True)
        self.editInfoWindow.set_border_width(10)
        self.editInfoWindow.set_size_request(675,475)
        
        self.editInfoWindow.add(self.editInfoVBox)
        self.editInfoWindow.set_title(_("edit info & settings"))        
        
        # define some signal handlers
        self.listvaluecell_num.connect('edited', self.cell_edited, 0)
        self.listvaluecell_text.connect('edited', self.cell_edited, 1)
        self.subparamname.connect("changed", self.name_edited)
        self.intModeCombo.connect("changed", self.intmode_changed)        
        self.intMode.connect("toggled", self.inttype_selected)
        self.stringMode.connect("toggled", self.strtype_selected)        
        self.addButton.connect("clicked", self.addRow)
        self.removeButton.connect("clicked", self.removeRow)

        self.saveButton.connect("clicked", self.saveClick)
        self.closeButton.connect("clicked", self.closeClick)

        self.editInfoWindow.connect("delete_event", self.Quit)        

    def intmode_changed(self, combo, data=None):
        if combo.get_active()==0:
            self.minnumlabel.show()
            self.minnum.show()
            self.maxnumlabel.show()
            self.maxnum.show()
            self.listvaluetreeview.hide()
            self.addButton.set_sensitive(False)
            self.removeButton.set_sensitive(False)              
        if combo.get_active()==1:
            self.listvaluetreeview.show()
            self.minnumlabel.hide()
            self.minnum.hide()
            self.maxnumlabel.hide()
            self.maxnum.hide()
            self.addButton.set_sensitive(True)
            self.removeButton.set_sensitive(True)            

    def name_edited(self, data=None):
        _=gettext.gettext
        self.subparamInfoFrame.set_label(_("Info about selected subparameter \"")
                                        + self.subparamname.get_text() + "\":")

    def strtype_selected(self, widget, data=None):        
        if widget.get_active():
            self.intModeCombo.set_sensitive(False)
            self.minnum.set_sensitive(False)
            self.maxnum.set_sensitive(False)
            self.listvaluetreeview.set_sensitive(False)

            self.maxlen.set_sensitive(True)            

    def inttype_selected(self, widget, data=None):
        if widget.get_active():
            self.maxlen.set_sensitive(False)
            
            self.intModeCombo.set_sensitive(True)
            self.minnum.set_sensitive(True)
            self.maxnum.set_sensitive(True)
            self.listvaluetreeview.set_sensitive(True)            
        
    def edit_info(self, param_path, subparam_name, subparam_index, one=True):
        _=gettext.gettext
        self.subparam_index=subparam_index
        self.param_path=param_path
        self.maxlen.set_text("")
        self.minnum.set_text("")
        self.maxnum.set_text("")
        self.listvaluestore.clear()
        
        self.param_path = param_path
        self.generalInfoFrame.set_label(_("General info about ") + param_path+":")

        param_info = self.dp.getInfo(self.param_path)
        if param_info!=None:
            self.generalInfoText.set_text(param_info)
        else:
            self.generalInfoText.set_text("")

        attrs=None            
        if subparam_name=="" and subparam_index==-1:
            self.subparamInfoFrame.set_no_show_all(True)
            self.subparamNameFrame.set_no_show_all(True)
            self.subparamAppearFrame.set_no_show_all(True)
            self.locked.set_no_show_all(False)
            self.locked.set_active(self.dp.isLocked(param_path))            
        elif subparam_index==0 and one:
            self.subparamInfoFrame.set_no_show_all(True)
            self.subparamNameFrame.set_no_show_all(True)
            self.subparamAppearFrame.set_no_show_all(False)
            self.locked.set_no_show_all(True)
            try:
                attrs = self.dp.getSubParamsAttr(param_path)
            except TypeError:
                attrs=None            
        else:
            self.subparamInfoFrame.set_no_show_all(False)
            self.subparamNameFrame.set_no_show_all(False)
            self.subparamAppearFrame.set_no_show_all(False)
            self.locked.set_no_show_all(True)                                    
            self.subparamInfoFrame.set_label(_("Info about selected subparameter \"")
                                             + subparam_name + "\":")
            subparam_info=self.dp.getSubParamInfo(param_path,subparam_index)
            if subparam_info!=None:
                self.subparamInfoText.set_text(subparam_info)
            else:
                self.subparamInfoText.set_text("")
            try:
                attrs = self.dp.getSubParamsAttr(param_path)
            except TypeError:
                attrs=None
        att=None
        if attrs!=None:
            for a in attrs:
                if int(a['index'])==subparam_index:
                    att=a
                    break
        self.subparamname.set_text(subparam_name)

        self.intModeCombo.set_active(0)        
        if att!=None and attrs!=None:
            if att['type']=='string':
		self.stringMode.set_active(True)
		self.maxlen.set_text(att['maxlen'])
            elif att['type']=='number_range':
		self.intMode.set_active(True)
		self.intModeCombo.set_active(0)
		self.minnum.set_text(att['min'])
		self.maxnum.set_text(att['max'])
            elif att['type']=='number_items':
		self.intMode.set_active(True)
		self.intModeCombo.set_active(1)
                for i in self.dp.getSubParamNumberItems(param_path,
                                                        subparam_index):
                    self.listvaluestore.append([int(i['value']),i['description']])
	else:
	    self.stringMode.set_active(True)
	    self.maxlen.set_text("0")
        combovalue = self.intModeCombo.get_active()
        if combovalue==0:
            self.minnumlabel.set_no_show_all(False)
            self.minnum.set_no_show_all(False)
            self.maxnumlabel.set_no_show_all(False)
            self.maxnum.set_no_show_all(False)                        
            self.listvaluetreeview.set_no_show_all(True)
        if combovalue==1:
            self.listvaluetreeview.set_no_show_all(False)
            self.minnumlabel.set_no_show_all(True)
            self.minnum.set_no_show_all(True)
            self.maxnumlabel.set_no_show_all(True)
            self.maxnum.set_no_show_all(True)                        

        if self.intMode.get_active():
            self.inttype_selected(self.intMode)
        if self.stringMode.get_active():
            self.strtype_selected(self.stringMode)
            
        self.editInfoWindow.show_all()

    def closeClick(self, button):
        self.Quit(self.editInfoWindow, "delete_event")
        
    def Quit(self, widget, event):
        self.editInfoWindow.hide_all()
        self.paramview.emit("cursor-changed")
        return True

    def addRow(self, button):
        row_count=0
        for r in self.listvaluestore:
            row_count=row_count+1
        listIter = self.listvalueselection.get_selected()[1]
        if listIter==None or row_count==0:
            val=[0,'']
        else:
            val=self.listvaluestore.get(listIter, 0, 1)
        self.listvaluestore.append(val)

    def removeRow(self, button):
        row_count=len(self.listvaluestore)
        (model, listIter) = self.listvalueselection.get_selected()
        if listIter==None or row_count==0:
            return
        else:
            self.listvaluestore.remove(listIter)
            if row_count>1:
                self.listvalueselection.select_iter(model.get_iter_first())            

        
    def cell_edited(self, cell, path, new_text, col_num):
        _=gettext.gettext
        model = self.listvaluetreeview.get_model()
        try:
            if col_num==0:
                model[path][col_num]=int(new_text)
            else:
                model[path][col_num]=new_text
        except ValueError:
            msg_error = gtk.MessageDialog(self.editInfoWindow,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                          gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                          _("Invalid value! Only numbers allowed in first column"))
            msg_error.show()
            msg_error.connect("response", self.error_response)
        
        
    def error_response(self, dlg, response_id):
        dlg.destroy()

    def saveClick(self, button):
        _=gettext.gettext
        self.dp.setLocked(self.param_path, self.locked.get_active())
        if self.stringMode.get_active():
            try:
                maxlen=int(self.maxlen.get_text())
            except ValueError:
                msg_error = gtk.MessageDialog(self.editInfoWindow,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                            gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                            _("Invalid value! Only numbers allowed in string length"))
                msg_error.show()
                msg_error.connect("response", self.error_response)
                return

            if self.subparam_index==-1:
                self.dp.setSubParamAttr(self.param_path, 0,
                                         '', 'string',
                                         sub_len='0')                
                
            else:                
                self.dp.setSubParamAttr(self.param_path, self.subparam_index,
                                         self.subparamname.get_text(), 'string',
                                         sub_len=self.maxlen.get_text())
            
        elif self.intMode.get_active() and self.intModeCombo.get_active()==0:
            try:
                minnum = int(self.minnum.get_text())
                maxnum = int(self.maxnum.get_text())
            except ValueError:
                msg_error = gtk.MessageDialog(self.editInfoWindow,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                            gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                            _("Invalid value! Only numbers allowed for minimal and maximal values"))
                msg_error.show()
                msg_error.connect("response", self.error_response)
                return
            self.dp.setSubParamAttr(self.param_path, self.subparam_index,
                                     self.subparamname.get_text(), 'number_range',
                                     sub_min=self.minnum.get_text(),
                                     sub_max=self.maxnum.get_text())            
        elif self.intMode.get_active() and self.intModeCombo.get_active()==1:
            itemstorage=[]
            for row in self.listvaluestore:
                itemstorage.append({'value':row[0], 'description':row[1]})

            for i in itemstorage:
                if itemstorage.count(i)>1:
                    msg_error = gtk.MessageDialog(self.editInfoWindow,
                                                  gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                                  gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                                  _("Invalid value! Only unique numbers allowed"))
                    
                    msg_error.show()
                    msg_error.connect("response", self.error_response)
                    return
            self.dp.setSubParamNumberItems(self.param_path,self.subparam_index,
                                           self.subparamname.get_text(),
                                           itemstorage)

        startiter_subinfo = self.subparamInfoText.get_start_iter()
        enditer_subinfo = self.subparamInfoText.get_end_iter()

        startiter_geninfo = self.generalInfoText.get_start_iter()
        enditer_geninfo = self.generalInfoText.get_end_iter()

        self.subparamInfoText.get_text(startiter_subinfo, enditer_subinfo)
        
        self.dp.setInfo(self.param_path,
                        self.generalInfoText.get_text(startiter_geninfo,
                                                      enditer_geninfo))
        self.dp.setSubParamInfo(self.param_path, self.subparam_index,
                                self.subparamInfoText.get_text(startiter_subinfo,
                                                              enditer_subinfo))
        try:
            self.dp.saveToXML()
        except IOError, (errno, strerror):
            msg_error=gtk.MessageDialog(self.editInfoWindow,gtk.DIALOG_MODAL |
                                        gtk.DIALOG_DESTROY_WITH_PARENT,
                                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                        "I/O Error [" + self.dpfilename + "]: "
                                        + strerror)
            msg_error.show()
            msg_error.connect("response", self.error_response)
            return
            
        msg_saved = gtk.MessageDialog(self.editInfoWindow,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                          gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                          _("Info about ") + self.param_path +_(" successfully saved."))
        msg_saved.show()
        msg_saved.connect("response", self.dlg_ok)


    def dlg_ok(self, dlg, response_id):
        dlg.destroy()        
