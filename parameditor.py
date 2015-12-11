#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Parameter editor window & stuff

# ParamEditor - main class for all data types
# StringParamEditor - class for editing string subparameters
# IntRangeParamEditor - class for editing interger subparameters which have a range of valid values (ex: from 0 to 10)
# IntItemsParamEditor - class for editing interger subparameters which can have a some valid values (ex: 0 or 1)
import pygtk
pygtk.require('2.0')
import gtk, gobject
import gettext

from storage import *
        

class ParamEditor:
    cur_value = ""
    old_value = ""
    dirPath = None
    listPath = None
    paramstorage = None
    new_value = None


    def __init__(self, paramstorage, editor_widget, gettext):
        self.gettext=gettext
        _=gettext.gettext
        self.paramstorage = paramstorage
        self.editParamWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.editParamWindow.set_position(gtk.WIN_POS_CENTER)
        editParamVBox = gtk.VBox(False,10)
        editParamFrame = gtk.Frame(_("New value"))

        infoFrame = gtk.Frame(_("Info"))
        self.infoText = gtk.Label()
        self.infoText.set_alignment(0, 0)
        self.infoText.set_padding(2, 2)
        self.infoText.set_line_wrap(True)
        self.infoText.set_width_chars(65)
        infoScroll = gtk.ScrolledWindow()
        infoScroll.set_border_width(5)
        infoScroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        infoScroll.add_with_viewport(self.infoText)
        infoScroll.set_shadow_type(gtk.SHADOW_NONE)
        infoFrame.add(infoScroll)         

        editParamVBox.pack_start(infoFrame,True,True,0)

        editParamVBox.pack_start(editParamFrame,False,False,0)
        
        editParamButtonBox = gtk.HBox(True,10)
        saveButton = gtk.Button(_("Save value and exit"))
        restoreButton = gtk.Button(_("Restore value"))            
        exitButton = gtk.Button(_("Exit"))
        editParamButtonBox.pack_start(saveButton,True,True,0)
        editParamButtonBox.pack_start(restoreButton,True,True,0)
        editParamButtonBox.pack_start(exitButton,True,True,0)

        editParamVBox.pack_start(editParamButtonBox,False,True,0)        

        self.editor_widget = editor_widget
        editParamFrame.add(editor_widget)
        self.editParamWindow.set_modal(True)
        self.editParamWindow.set_border_width(10)
        
        self.editParamWindow.add(editParamVBox)
        self.editParamWindow.set_size_request(500,300)

        saveButton.connect("clicked", self.saveClick)
        restoreButton.connect("clicked", self.restoreClick)
        exitButton.connect("clicked", self.exitClick)

        self.editParamWindow.connect("delete_event", self.Quit)
        
        
    def edit_parameter(self, fs_path, old_val, dirPath, listPath, paramview,
                       descParser, subparam_index):
        _=self.gettext.gettext
        self.editParamWindow.set_title(_("edit parameter ") + fs_path)
        self.fs_path=fs_path
        self.listPath = listPath
        self.dirPath = dirPath
        self.old_value = old_val
        self.paramview = paramview
        self.subparam_index = subparam_index
        self.attrs={}
        try:
            subattrs = descParser.getSubParamsAttr(self.fs_path)
            for s in subattrs:
                if int(s['index'])==subparam_index:
                    self.attrs=s
                    break            
        except TypeError:
            self.attrs['index']='0'
            self.attrs['name']=''
            self.attrs['type']='string'
            self.attrs['maxlen']='0'
        itext = descParser.getSubParamInfo(fs_path, subparam_index)
        if itext==None:
            itext = descParser.getInfo(fs_path)
            if itext==None:
                itext = ''
        self.infoText.set_text(itext)
        self.editParamWindow.show_all()        

    def saveClick(self, button,text):
        selection = self.paramview.get_selection()
        (model, Iter) = selection.get_selected()
        
        filename=self.paramstorage.retrieve_filename(self.dirPath, self.listPath)
        if filename==None:
            filename = model.get_value(Iter, 0)            
        if self.old_value!=text:
            self.paramstorage.add(self.dirPath, self.listPath,text,self.subparam_index,
                                  filename)
        else:
            model.set_value(Iter, 0, filename)
            self.paramstorage.remove(self.dirPath, self.listPath, self.subparam_index)
        self.editParamWindow.hide_all()

        paramselection = self.paramview.get_selection()
        (model, listIter) = paramselection.get_selected()
        filename = self.paramstorage.retrieve_filename(
            self.dirPath, self.listPath)
        if filename!=None:
            model.set_value(listIter, 0, '<span foreground="blue"><b>' +
                                      filename
                                      + '</b></span>')      
        self.paramview.emit("cursor-changed")

    def restoreClick(self, button):
        self.paramText.set_text(self.old_value)

    def exitClick(self, button):
        self.Quit(self.editParamWindow, "delete_event")

    def Quit(self, widget, event):        
        self.editParamWindow.hide_all()
        self.paramview.emit("cursor-changed")
        return True
    
    def showError(self, text):
        msg_error=gtk.MessageDialog(self.editParamWindow,gtk.DIALOG_MODAL |
                                    gtk.DIALOG_DESTROY_WITH_PARENT,
                                    gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, text)
        msg_error.show()
        msg_error.connect("response", self.error_response)
        
    def error_response(self, dlg, response_id):
        dlg.destroy()        


        
class StringParamEditor(ParamEditor):
    def __init__(self,paramstorage, gettext):
        self.subparamvalue = gtk.Entry()
        ParamEditor.__init__(self, paramstorage, self.subparamvalue, gettext)

    def saveClick(self, button):
        _=gettext.gettext
        text = self.subparamvalue.get_text()
        try:
            maxlen = int(self.attrs['maxlen'])
        except KeyError:
            maxlen=0
        if maxlen<len(text) and maxlen!=0:
            self.showError(_("Maximum length for this string value is: ") + str(maxlen) +
                                    _("\nPress \"Settings\" button on main form if you want to change it."))
            return
            
        ParamEditor.saveClick(self, button,text)

    def restoreClick(self, button):
        self.subparamvalue.set_text(self.old_value)
        
    def edit_parameter(self, fs_path, old_val, dirPath, listPath, paramview,
                       subparam_index, descParser):    
        self.new_value = self.paramstorage.retrieve(dirPath, listPath)
        if self.new_value != None:
            try:
                self.subparamvalue.set_text(self.new_value[subparam_index])
            except TypeError:
                self.subparamvalue.set_text(old_val)
            except IndexError:
                self.subparamvalue.set_text(old_val)                
        else:
            self.subparamvalue.set_text(old_val)
            
        ParamEditor.edit_parameter(self, fs_path, old_val, dirPath, listPath,
                                   paramview, descParser, subparam_index)            

class IntRangeParamEditor(ParamEditor):
    def __init__(self,paramstorage, gettext):
        self.subparam_spin = gtk.SpinButton()
        ParamEditor.__init__(self, paramstorage, self.subparam_spin, gettext)        


    def edit_parameter(self, fs_path, old_val, dirPath, listPath, paramview,
                       subparam_index, descParser):
        ParamEditor.edit_parameter(self, fs_path, old_val, dirPath, listPath,
                                   paramview, descParser, subparam_index)
        
        self.new_value = self.paramstorage.retrieve(dirPath, listPath)
        if self.new_value != None:
            try:
                adj_value=self.new_value[subparam_index]
            except TypeError:
                adj_value=old_val
            except IndexError:
                adj_value=old_val
        else:
            adj_value=old_val

        if adj_value==None:
            adj_value=old_val
        adjustment = gtk.Adjustment(int(adj_value), int(self.attrs['min']),
                                    int(self.attrs['max']),
                                    step_incr=1, page_incr=10, page_size=0)
        self.subparam_spin.configure(adjustment, 0.4, 0)
        self.subparam_spin.set_numeric(True)        

    def saveClick(self, button):
        spin_value = self.subparam_spin.get_value_as_int()
        maxval = int(self.attrs['max'])
        minval = int(self.attrs['min'])
        if spin_value>maxval or spin_value<minval:
            self.showError(_("Value for this parameter must be between ") + minval + _(" and ")
                           + minval + _(".\nPress \"Settings\" button on main form if you want to change it's range."))
            return
            
        ParamEditor.saveClick(self, button,str(spin_value))

    def restoreClick(self, button):
        self.subparam_spin.set_value(int(self.old_value))        

class IntItemsParamEditor(ParamEditor):
    def __init__(self,paramstorage, gettext):
        
        self.comboStore = gtk.ListStore(gobject.TYPE_STRING)
        self.valueCombo = gtk.ComboBox(self.comboStore)
        cell = gtk.CellRendererText()
        self.valueCombo.pack_start(cell, True)
        self.valueCombo.add_attribute(cell, 'text', 0)        
        self.items = []
        ParamEditor.__init__(self, paramstorage, self.valueCombo, gettext)


    def edit_parameter(self, fs_path, old_val, dirPath, listPath, paramview,
                       subparam_index, descParser):
        self.comboStore.clear()
        old_val = old_val.split(" : ")[0]
        ParamEditor.edit_parameter(self, fs_path, old_val, dirPath, listPath,
                                   paramview, descParser, subparam_index)
        self.items=descParser.getSubParamNumberItems(fs_path,subparam_index)
        self.dp = descParser
        for i in self.items:
            self.valueCombo.append_text(i['value'] + " : " + i['description'])

        self.new_value = self.paramstorage.retrieve(dirPath, listPath)
        try:
            if self.new_value != None:
                try:
                    index = self.items.index({'value':self.new_value[subparam_index],'description':descParser.getItemDescription(fs_path, subparam_index, self.new_value[subparam_index])})
                                              
                except TypeError:
                    index = self.items.index({'value':old_val,'description':descParser.getItemDescription(fs_path, subparam_index, old_val)})
                except IndexError:
                    index = self.items.index({'value':old_val,'description':descParser.getItemDescription(fs_path, subparam_index, old_val)})
            else:
                index = self.items.index({'value':old_val,'description':descParser.getItemDescription(fs_path, subparam_index, old_val)})
        except ValueError:
            index = 0
        self.valueCombo.set_active(index)            

    def saveClick(self, button):
        ParamEditor.saveClick(self, button,self.items[self.valueCombo.get_active()]['value'])


    def restoreClick(self, button):        
        index = self.items.index({'value':self.old_value,
                                  'description':self.dp.getItemDescription(self.fs_path, self.subparam_index, self.old_value)})
        self.valueCombo.set_active(index)
