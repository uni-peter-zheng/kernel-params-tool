#!/usr/bin/env python
# -*- coding: utf-8 -*-
# this window displaying when user presses ApplyAll or RestoreAll
import pygtk
pygtk.require('2.0')
import gtk, gobject

from storage import *
from writer import *

class ApplyRestoreWindow:
    def __init__(self, title, framecaption, pathstorage, dirstore, paramstore,
                 dirmodelview, rootDir, selected_dir, mode, gettext):
        # mode = True - do apply
        # mode = False - do restore
        _=gettext.gettext
        self.mode = mode
        self.rootDir = rootDir
        self.dirpath_listpath = []
        self.pathstorage = pathstorage
        self.paramwriter = Writer(self.pathstorage)
        self.modelview = dirmodelview
        self.paramstore = paramstore
        self.selected_dir = selected_dir

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.viewframe = gtk.Frame(framecaption)
        # 3rd column is for storing parameter path
        self.liststore = gtk.ListStore(gobject.TYPE_STRING,
                                        gobject.TYPE_BOOLEAN)
        self.paramview = gtk.TreeView(self.liststore)
        self.paramScroll = gtk.ScrolledWindow()
        self.paramScroll.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
        self.paramScroll.add_with_viewport(self.paramview)
        self.paramScroll.set_border_width(5)        
        self.viewframe.add(self.paramScroll)

        self.paramcell = gtk.CellRendererText()
        self.paramcolumn = gtk.TreeViewColumn(_("Path"), self.paramcell)
        self.paramview.append_column(self.paramcolumn)
        self.paramcolumn.add_attribute(self.paramcell, 'text', 0)        

        self.togglecell = gtk.CellRendererToggle()
        self.togglecell.set_property('activatable', True)
        if self.mode:
            self.togglecolumn = gtk.TreeViewColumn(_("Apply"), self.togglecell)
        else:
            self.togglecolumn = gtk.TreeViewColumn(_("Restore"), self.togglecell)
        self.paramview.append_column(self.togglecolumn)
        self.togglecolumn.add_attribute(self.togglecell, "active", 1)


        self.mainBox = gtk.VBox(False,0)
        self.frameBox = gtk.HBox(False,0)
        self.buttonBox = gtk.HBox(True,0)

        if self.mode:
            self.okButton = gtk.Button(_("Apply selected"))
        else:
            self.okButton = gtk.Button(_("Restore selected"))
        self.cancelButton = gtk.Button(_("Cancel"))
        
        self.togglecell.connect('toggled', self.onToggle, self.liststore)
        self.okButton.connect('clicked', self.onOk)
        self.cancelButton.connect('clicked', self.onCancel)        
        
        self.window.connect("delete_event", self.Quit)
        
        self.mainBox.pack_start(self.frameBox,True,True,0)
        self.mainBox.pack_start(self.buttonBox,False,True,10)
        self.frameBox.pack_start(self.viewframe,True,True,0)
        self.buttonBox.pack_start(self.okButton,True,True,10)
        self.buttonBox.pack_start(self.cancelButton,True,True,10)                

        self.window.set_modal(True)
        self.window.set_title(title)
        self.window.set_border_width(15)
        self.window.set_size_request(600,375)        
        
        self.window.add(self.mainBox)

        empty = True
        dirs = pathstorage.get_dirs()
        dirs.sort()
        for d in dirs:
            params = pathstorage.get_params_from_dir(d)
            params.sort()
            for l in params:
                dirIter = dirstore.get_iter(d)
                filename = pathstorage.retrieve_filename(d, l)
                if filename!=None:
                    empty = False
                    path = dirstore.get_value(dirIter, 0)+ "." + filename
                    parentIter = dirstore.iter_parent(dirIter)
                    while parentIter != None:
                        path = dirstore.get_value(parentIter, 0) + "." + path
                        parentIter = dirstore.iter_parent(parentIter)
                    self.liststore.append([path, True])
                    self.dirpath_listpath.append((d,l))
        if empty!=True:
            self.window.show_all()        

    def onToggle(self, cell, path, model ):
        model[path][1] = not model[path][1]
        return        

    def onOk(self, button):
        Iter = self.liststore.get_iter_first()
        dlIter = iter(self.dirpath_listpath)
        if self.mode:
            writedList = []
            while Iter!=None:
                path =  self.liststore.get_value(Iter, 0)
                isApply = self.liststore.get_value(Iter, 1)
                (d, l) = dlIter.next()            
                if isApply:
                    if self.paramwriter.writePath(self.rootDir + "/" + path.replace(".", "/"),
                                               d, l):
                        writedList.append((d, l))
                Iter = self.liststore.iter_next(Iter)
            for i in writedList:
                self.pathstorage.remove(i[0], i[1], -1)
        else:
            while Iter!=None:
                path =  self.liststore.get_value(Iter, 0)
                isRestore = self.liststore.get_value(Iter, 1)
                (d, l) = dlIter.next()            
                if isRestore:
                    filename = self.pathstorage.retrieve_filename(d, l)
                    if  filename != None:
                        self.pathstorage.remove(d, l, -1)                    
                Iter = self.liststore.iter_next(Iter)

        self.window.hide_all()
        self.paramstore.clear()
        self.selected_dir = ""
        self.modelview.emit("cursor-changed")


    def onCancel(self, button):
        self.Quit(self.window, "delete_event")

    def Quit(self, widget, event):
        self.window.hide_all()
        return True
