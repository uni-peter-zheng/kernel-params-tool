#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main application module (displays main window)

import pygtk
pygtk.require('2.0')
import gtk, gobject
import pango
import locale
import gettext

from reader import *
from writer import *
from parameditor import *
from storage import *
from applyrestorewindow import *
from infowindow import *
from editinfowindow import *
from descriptionparser import *
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element


class MainApp:
    dirname = "/proc/sys"
    selected_dir = dirname
    selected_param=""
    selected_dirtreestore_path = None
    dpfilename="/etc/kernel-params-tool/description_en.xml"
    langfilename="/etc/kernel-params-tool/language.xml"
    
    def __init__(self):
        gettext.bindtextdomain("kernel-params-tool","/usr/share/locale/")
        gettext.textdomain("kernel-params-tool")
        _=gettext.gettext

        locale_lang = locale.getdefaultlocale()
        if locale_lang[0] == "zh_CN":
            self.dpfilename = "/etc/kernel-params-tool/description_zh.xml"
        else:
            self.dpfilename = "/etc/kernel-params-tool/description_en.xml"

        self.procReader = Reader()
        self.editedParams = ParamStorage()
        self.procWriter = Writer(self.editedParams)        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_title(_("kernrl params tool"))
        self.window.set_border_width(15)
        self.window.set_size_request(800,550)
        
        self.param_path=None
        # two boxes, first for directory tree (left),
        # second for parameters list (upper right)
        self.treeBox = gtk.VBox(False,0)
        self.paramBox = gtk.VBox(False,0)

        # main box
        self.mainBox = gtk.HBox(False,10)
                    
        # treestore for directory tree
        self.dirstore = gtk.TreeStore(str)

        # read /proc/sys directory structure into treestore
        self.procReader.fillDirStore(self.dirname, self.dirstore)

        # treeview, cellrenderer and columns for directory tree
        self.dirview = gtk.TreeView(self.dirstore)
        self.dircolumn = gtk.TreeViewColumn(self.dirname)
        self.dirview.append_column(self.dircolumn)
        self.dircell = gtk.CellRendererText()
        self.dircolumn.pack_start(self.dircell, True)
        self.dircolumn.add_attribute(self.dircell, 'text', 0)
        self.dirview.set_search_column(0)
        self.dircolumn.set_sort_column_id(0)
        self.dirview.set_reorderable(False)

        # liststore for parameters list
        self.paramstore = gtk.ListStore(str)

        # treeview, cellrenderer and columns for parameters list
        self.paramview = gtk.TreeView(self.paramstore)
        self.paramcell = gtk.CellRendererText()
        self.paramcolumn = gtk.TreeViewColumn(_("Parameters"), self.paramcell, markup=0)
        self.paramview.append_column(self.paramcolumn)

        self.paramcolumn.add_attribute(self.paramcell, 'text', 0)
        self.paramview.set_search_column(0)
        self.paramcolumn.set_sort_column_id(0)
        self.paramview.set_reorderable(False)
        

        # ScrolledWindow for treeBox
        self.treeScroll = gtk.ScrolledWindow()
        self.treeScroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.treeScroll.add_with_viewport(self.treeBox)
        self.treeScroll.set_size_request(160, 0);

        # ScrolledWindow for paramInfo
        self.paramInfoScroll = gtk.ScrolledWindow()
        self.paramInfoScroll.set_border_width(5)
        self.paramInfoScroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        # ScrolledWindow for paramView
        self.paramScroll = gtk.ScrolledWindow()
        self.paramScroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.paramScroll.add(self.paramview)

        self.descParser=DescriptionParser()
        self.descParser.setXMLFileName(self.dpfilename)
        self.eiwindow = EditInfoWindow(self.descParser, self.paramview, gettext)

        # pack directory tree in treeBox and pack scrolledwindow of parameters list
        # in paramBox
        self.treeBox.pack_start(self.dirview, True, True, 0)
        self.paramBox.pack_start(self.paramScroll, True, True, 0)

        # this is frame for view param info
        self.paraminfoframe = gtk.Frame(_("Info:"))
        self.paramBox.pack_start(self.paraminfoframe, True, True, 0)

        # this is frames for viewing values
        self.viewframe = gtk.Frame(_("Selected parameter values:"))
        self.viewinfoframe = gtk.Frame(_("Selected parameter value:"))
        
        self.paramBox.pack_start(self.viewframe,True,True,0)
        self.paramBox.pack_start(self.viewinfoframe,True,True,0)        

        # create a label for param info
        #self.paraminfoview = gtk.Label()
        self.paraminfotext = gtk.TextBuffer()
        self.paraminfoview = gtk.TextView(self.paraminfotext)
        #self.paraminfoview.set_alignment(0, 0)
        #self.paraminfoview.set_padding(2, 2)
        self.paraminfoview.set_editable(False)
        self.paraminfoview.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.paraminfoview.set_can_focus(False)
        self.paramInfoScroll.add_with_viewport(self.paraminfoview)
        self.paraminfoframe.add(self.paramInfoScroll)        

        # create a label for "readonly" params
        self.valueinfoview = gtk.Label()
        self.valueinfoview.set_alignment(0, 0)
        self.valueinfoview.set_padding(2, 2)       

        # create TreeView, ListStore and scrolled window
        # for parameter view
        self.valuestore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING,
                                        gobject.TYPE_BOOLEAN)
        self.valuetreeview = gtk.TreeView(self.valuestore)
        self.valuecell_name = gtk.CellRendererText()
        self.valuecell_current = gtk.CellRendererText()
        self.valuecell_next = gtk.CellRendererText()        
        self.valuecell_restore = gtk.CellRendererToggle()
        self.valuecell_restore.set_property('activatable', True)
        
        self.valuecolumn_name = gtk.TreeViewColumn(_("Subparameter name"), self.valuecell_name)
        self.valuecolumn_current = gtk.TreeViewColumn(_("Current value"), self.valuecell_current)
        self.valuecolumn_next = gtk.TreeViewColumn(_("New value"), self.valuecell_next)
        self.valuecolumn_restore = gtk.TreeViewColumn(_("Restore enabled"), self.valuecell_restore)
        self.valuecell_restore.connect('toggled', self.onToggleRestore, self.valuestore)                
        
        self.valuetreeview.append_column(self.valuecolumn_current)
        self.valuetreeview.append_column(self.valuecolumn_next)

        self.valuecolumn_name.add_attribute(self.valuecell_name, 'text', 0)
        self.valuecolumn_current.add_attribute(self.valuecell_current, 'text', 1)
        self.valuecolumn_next.add_attribute(self.valuecell_next, 'text', 2)
        self.valuecolumn_restore.add_attribute(self.valuecell_restore, "active", 3)
        self.valuetreeview.set_search_column(0)
        self.valuecolumn_name.set_sort_column_id(0)     
        self.valuetreeview.set_reorderable(False)
        
#       ScrolledWindow for usual parameters
        self.valueScroll = gtk.ScrolledWindow()
        self.valueScroll.set_border_width(5)
        self.valueScroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.valueScroll.add(self.valuetreeview)
        self.valueScroll.set_shadow_type(gtk.SHADOW_NONE)

#       ScrolledWindow for readonly parameters
        self.valueInfoScroll = gtk.ScrolledWindow()
        self.valueInfoScroll.set_border_width(5)
        self.valueInfoScroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.valueInfoScroll.add_with_viewport(self.valueinfoview)
        self.valueInfoScroll.set_shadow_type(gtk.SHADOW_NONE)

        self.viewframe.add(self.valueScroll)
        self.viewinfoframe.add(self.valueInfoScroll)        

        self.viewinfoframe.set_no_show_all(True)
        
        
        # buttonbox
        self.buttonBox = gtk.HBox(True,10)
        self.paramBox.pack_end(self.buttonBox, False, True, 5)

        self.applyButton= gtk.Button(_("Apply"))
        self.applyAllButton= gtk.Button(_("Apply_all"))
        self.restoreButton= gtk.Button(_("Restore"))
        self.restoreAllButton= gtk.Button(_("Restore_all"))
        self.editinfoButton = gtk.Button(_("Setting_info"))
        self.quitButton = gtk.Button(_("Quit"))

        self.applyButton.set_sensitive(False)
        self.restoreButton.set_sensitive(False)                
        self.editinfoButton.set_sensitive(False)
        
        self.buttonBox.pack_start(self.applyButton, True, True, 0)
        self.buttonBox.pack_start(self.applyAllButton, True, True, 0)
        self.buttonBox.pack_start(self.restoreButton, True, True, 0)
        self.buttonBox.pack_start(self.restoreAllButton, True, True, 0)
        self.buttonBox.pack_start(self.editinfoButton, True, True, 0)        
        self.buttonBox.pack_start(self.quitButton, True, True, 0)        

        # pack all boxes into mainbox
        self.mainBox.pack_start(self.treeScroll, True, True, 0)
        self.mainBox.pack_start(self.paramBox, True, True, 0)        
        self.window.add(self.mainBox)

        # get selections from treeviews
        self.dirselection = self.dirview.get_selection()
        self.dirselection.set_mode(gtk.SELECTION_SINGLE)
        self.paramselection = self.paramview.get_selection()
        self.paramselection.set_mode(gtk.SELECTION_SINGLE)
        self.subparamselection = self.valuetreeview.get_selection()
        self.subparamselection.set_mode(gtk.SELECTION_SINGLE)        
        
        #print self.paraminfoview.get_parent().get_parent().size_request()
        #print self.paraminfoframe.size_request()
        #self.paraminfoview.set_size_request(67,84)
        
        # signal handlers definitions
        self.dirview.connect("cursor-changed", self.onDirSelect)
        self.paramview.connect("cursor-changed", self.onParamSelect)
        #self.paramview.connect("row-activated", self.onParamInfo)
        self.valuetreeview.connect("row-activated", self.onParamEdit)        

        self.applyButton.connect("clicked", self.onApply)
        self.applyAllButton.connect("clicked", self.onApplyAll)        
        self.restoreButton.connect("clicked", self.onRestore)
        self.restoreAllButton.connect("clicked", self.onRestoreAll)                
        self.editinfoButton.connect("clicked", self.onEditInfo)
        self.quitButton.connect("clicked", self.onQuit)
        self.window.connect("delete_event", self.Quit)
        self.window.show_all()
        gtk.main()
        

    def onDirSelect(self, treeview):
        dirIter = self.dirselection.get_selected()[1]
        self.clear_paramInfo()

        try:
            path = dirValue = self.dirstore.get_value(dirIter, 0)
        except TypeError:
            # this code for preventing TypeError exception when user trying to search in directory treee
            self.paramstore.clear()
            return
    
        parentIter = self.dirstore.iter_parent(dirIter)
        while parentIter != None:
            path = self.dirstore.get_value(parentIter, 0) + "/" + path
            parentIter = self.dirstore.iter_parent(parentIter)

        path = self.dirname + "/" + path
        self.paramstore.clear()
        self.valuestore.clear()
        self.selected_param=None
        self.selected_dir = path
        self.procReader.fillParamStore(self.selected_dir, self.paramstore)

        self.selected_dirtreestore_path = self.dirstore.get_path(dirIter)

        self.applyButton.set_sensitive(False)
        self.restoreButton.set_sensitive(False)
        self.editinfoButton.set_sensitive(False)
        
        Iter = self.paramstore.get_iter_first()
        while Iter!=None:
            filename = self.editedParams.retrieve_filename(
                self.selected_dirtreestore_path, self.paramstore.get_path(Iter))
            if filename!=None:
                self.paramstore.set_value(Iter, 0, '<span foreground="blue"><b>' +
                                          filename
                                          + '</b></span>')
            Iter = self.paramstore.iter_next(Iter)       
            
    def onParamSelect(self, treeview):
        self.subparamselection.unselect_all()
        listIter = self.paramselection.get_selected()[1]
        dirIter = self.dirselection.get_selected()[1]
        dirPath = self.dirstore.get_path(dirIter)
        listPath = self.paramstore.get_path(listIter)
        param_assume_readonly=False

        paramValue = self.editedParams.retrieve_filename(dirPath, listPath)
        if paramValue==None:
            paramValue = self.paramstore.get_value(listIter, 0)
        if paramValue!=self.selected_param:
            self.valuestore.clear()
            
            self.update_paramInfo(self.selected_dir +
                                      "/" + paramValue)
            param_locked=self.descParser.isLocked(self.selected_dir +
                                                      "/" + paramValue)
            param_readonly = self.procReader.isReadOnly(self.selected_dir +
                                                        "/" + paramValue)
            param_writeonly = self.procReader.isWriteOnly(self.selected_dir + 
                                                          "/" + paramValue)
            try:
                param_content=self.procReader.readContent( self.selected_dir +
                                                           "/" + paramValue)
            except IOError, (errno, strerror):
                self.valuestore.clear() 
                param_content=''

            subparams = self.enumerate_subparams(param_content)
            if (param_locked or param_readonly) and len(subparams)==1:
                self.viewframe.hide_all()
                if self.viewinfoframe.get_no_show_all():
                    self.viewinfoframe.set_no_show_all(False)
                self.viewinfoframe.show_all()
                self.valueinfoview.set_text(param_content)
                self.selected_param = paramValue
                self.applyButton.set_sensitive(True)
                self.restoreButton.set_sensitive(True)
                self.editinfoButton.set_sensitive(True)
                return
                
            self.viewinfoframe.hide_all()
            self.viewframe.show_all()
            param_content = None
            retrieved=self.editedParams.retrieve(dirPath, listPath)
            new_value = []
            self.subattr = self.descParser.getSubParamsAttr(self.selected_dir +
                                                       "/" +paramValue)

            for l in range(len(subparams)):
                try:
                    if retrieved[l]!=None:
                        new_value.append(retrieved[l])
                    else:
                        new_value.append('')
                except IndexError:
                    new_value.append('')
                except TypeError:
                    new_value.append('')                    
            if len(subparams)>1:
                if len(self.valuetreeview.get_columns())==2:
                    self.valuetreeview.insert_column(self.valuecolumn_name,0)
                    self.valuetreeview.append_column(self.valuecolumn_restore)
                if len(self.valuetreeview.get_columns())==1:
                    self.valuetreeview.insert_column(self.valuecolumn_current,0)
                    self.valuetreeview.insert_column(self.valuecolumn_name,0)
                    self.valuetreeview.append_column(self.valuecolumn_restore)
                    
                if self.subattr!=None:
                    j = 0
                    subparam_name=""
                    current_val=""
                    changed_val = ""
                    for i in range(len(subparams)):
                        current_val = subparams[i]
                        changed_val = new_value[i]
                        subparam_name='(noname'+str(i+1)+')'                        
                        if j<len(self.subattr):
                            if int(self.subattr[j]['index'])==i:
                                try:
                                    subparam_name=self.subattr[j]['name']
                                except IndexError:
                                    subparam_name=""
                                if subparam_name=="":
                                    subparam_name='(noname'+str(i+1)+')'

                                if self.subattr[j]['type']=='number_items':
                                    description_old = self.descParser.getItemDescription(self.selected_dir + "/" + paramValue,i,
                                                                         subparams[i])
                                    description_new = self.descParser.getItemDescription(self.selected_dir + "/" + paramValue,i,
                                                                         new_value[i])
                                    if description_old!=None:
                                        current_val = current_val + " : " + description_old
                                    if description_new!=None:
                                        changed_val = changed_val + " : " + description_new
           
                                j = j +1
                        self.valuestore.append([subparam_name,current_val,
                                                changed_val, True])
                else:
                    for i in range(len(subparams)):
                        self.valuestore.append(['(noname'+str(i+1)+')',
                                                subparams[i],new_value[i],
                                                True])
            else:
                if len(subparams)==0:
                    subparams=['']
                if len(self.valuetreeview.get_columns())==4:
                    self.valuetreeview.remove_column(self.valuecolumn_name)                    
                    self.valuetreeview.remove_column(self.valuecolumn_restore)
                if len(self.valuetreeview.get_columns())==1:
                    self.valuetreeview.insert_column(self.valuecolumn_current, 0)

                if param_writeonly:
                    self.valuetreeview.remove_column(self.valuecolumn_current)
                
                self.subattr = self.descParser.getSubParamsAttr(self.selected_dir + "/" +paramValue)
                if self.subattr!=None:
                    current_val = subparams[0]
                    changed_val = new_value[0]

                    if self.subattr[0]['type']=='number_items':
                        description_old = self.descParser.getItemDescription(self.selected_dir + "/" + paramValue,0,
                                                             subparams[0])
                        description_new = self.descParser.getItemDescription(self.selected_dir + "/" + paramValue,0,
                                                             new_value[0])
                        if description_old!=None:
                            current_val = current_val + " : " + description_old
                        if description_new!=None:
                            changed_val = changed_val + " : " + description_new
                    self.valuestore.append([None,current_val, changed_val,
                                            True])                                    
                else:
                    self.valuestore.append([None,subparams[0], new_value[0],
                                            True])                                                        
            self.selected_param = paramValue
            self.applyButton.set_sensitive(True)
            self.restoreButton.set_sensitive(True)
            self.editinfoButton.set_sensitive(True)


    def onParamEdit(self, treeview, path, column):
        _=gettext.gettext
        if self.procReader.isReadOnly(self.selected_dir + "/" + self.selected_param):
            msg_readonly = gtk.MessageDialog(self.window,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                          gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                          _("Sorry, you haven't privileges to write in file:\n") +
                                          self.selected_dir + "/" + self.selected_param)
            msg_readonly.show()
            msg_readonly.connect("response", self.error_readonly)          
            return
        dirIter = self.dirselection.get_selected()[1]
        listIter = self.paramselection.get_selected()[1]
        dirPath = self.dirstore.get_path(dirIter)
        listPath = self.paramstore.get_path(listIter)
        subIter = self.subparamselection.get_selected()[1]
        
        subparam_index = self.valuestore.get_path(subIter)[0]
        attr=None
        if self.subattr!=None:
            for s in self.subattr:
                if int(s['index'])==subparam_index:
                    attr = s
                    break
            try:
                if attr['type']=='string':
                    self.paramEditor = StringParamEditor(self.editedParams, gettext)
                elif attr['type']=='number_range':
                    self.paramEditor = IntRangeParamEditor(self.editedParams, gettext)
                elif attr['type']=='number_items':
                    self.paramEditor = IntItemsParamEditor(self.editedParams, gettext)                        
            except TypeError:
                self.paramEditor = StringParamEditor(self.editedParams, gettext)
        else:
            self.paramEditor = StringParamEditor(self.editedParams, gettext)        
        self.paramEditor.edit_parameter(self.selected_dir + "/" + self.selected_param,
                              str(self.valuestore.get_value(subIter,1)),
                                    dirPath, listPath, self.paramview,
                                    subparam_index, self.descParser) 
        self.selected_param=None        
        
    def onParamInfo(self, treeview, path, column):
        self.iwindow = InfoWindow(self.dpfilename)
        self.iwindow.show_info(self.selected_dir + "/" + self.selected_param)        

    def error_response(self, dlg, response_id):
        dlg.destroy()
        self.paramselection.unselect_all()
        self.selected_param=None
    def error_readonly(self, dlg, response_id):
        dlg.destroy()        

    def onApply(self, button):
        (model, listIter) = self.paramselection.get_selected()
        listPath = self.paramstore.get_path(listIter)
        filename = self.editedParams.retrieve_filename(
            self.selected_dirtreestore_path, listPath)
        if self.procWriter.write(self.selected_dir,
                              self.selected_dirtreestore_path, listPath):
            self.editedParams.remove(self.selected_dirtreestore_path, listPath, -1)
            model.set_value(listIter, 0, filename)
        self.selected_param=None
        self.paramview.emit("cursor-changed")


    def onApplyAll(self, button):
        _=gettext.gettext
        applywindow = ApplyRestoreWindow(_("Apply all parameters"),
                                         _("Selected parameters will be applied to kernel"),
                                         self.editedParams, self.dirstore,
                                         self.paramstore, self.dirview,
                                         self.dirname, self.selected_dir, True, gettext)
            

    def onRestoreAll(self, button):
        _=gettext.gettext
        restorewindow = ApplyRestoreWindow(_("Restore all parameters"),
                                         _("Selected parameters will be restored from current kernel values"),
                                         self.editedParams, self.dirstore,
                                         self.paramstore, self.dirview,
                                         self.dirname, self.selected_dir, False, gettext)
        
    def onRestore(self, button):
        psel = self.paramselection.get_selected()
        (model, listIter) = psel
        sub_psel = self.subparamselection.get_selected()
        (submodel, subIter) = sub_psel
        if subIter!=None:
            self.restore_param(model, listIter, submodel, subIter)
        else:
            sub = self.valuestore.get_iter_first()
            while sub!=None:                
                self.restore_param(model, listIter, submodel, sub)
                sub = submodel.iter_next(sub)
        self.selected_param=None
        self.paramview.emit("cursor-changed")                
        

    def restore_param(self, model, listIter, submodel, subIter):
        if self.valuestore.get_value(subIter,3):
            listPath = self.paramstore.get_path(listIter)
            subPath = self.valuestore.get_path(subIter)
            filename = self.editedParams.retrieve_filename(
                self.selected_dirtreestore_path, listPath)
            if  filename != None:
                self.editedParams.remove(self.selected_dirtreestore_path, listPath,
                                         subPath[0])
                model.set_value(listIter, 0, filename)       

    def update_paramInfo(self, param_path):
        param_info = self.descParser.getInfo(param_path)
        if param_info!=None:
            self.paraminfotext.set_text(param_info)
        else:
            self.paraminfotext.set_text("")

    def clear_paramInfo(self):
        self.paraminfotext.set_text("")

    def onEditInfo(self, button):
        one=False            
        (model, subIter) = self.subparamselection.get_selected()
        if subIter != None:
            subparam_index = self.valuestore.get_path(subIter)[0]
            subparam_name = model.get_value(subIter, 0)
            if len(self.valuestore)==1:
                one=True
            if subparam_name==None:
                subparam_name=""
        else:
            subparam_index=-1
            subparam_name=""
            one=True
        self.eiwindow.edit_info(self.selected_dir + "/" + self.selected_param,
                                subparam_name, subparam_index,one)
        self.selected_param=None        
        
    def onToggleRestore(self, cell, path, model ):
        model[path][3] = not model[path][3]
        return
    
    def onQuit(self, button):
        self.Quit(self.window, "delete_event")
        
    def Quit(self, widget, event):
        gtk.main_quit()
        gtk.Widget.destroy(self.window)

    def enumerate_subparams(self, param_string):
        param_string = param_string.strip('\n')
        subparams=param_string.split('\t')
        while True:
            try:
                subparams.remove('')
            except ValueError:
                break
        if subparams==[]:
            subparams=['']
        return subparams
if __name__=="__main__":
    app = MainApp()


