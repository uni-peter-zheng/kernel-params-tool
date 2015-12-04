#!/usr/bin/env python
# -*- coding: utf-8 -*-
# here is the Reader class for reading kernel parameters from /proc/sys
import os

class Reader:  
    def getSubDirList(self, path):
        return os.walk(path).next()[1]

    def getFileNames(self, path):
        return os.walk(path).next()[2]

    def isReadOnly(self, path):
        try:
            f = open(path, "w")
        except IOError:
            return True
        f.close()
        return False

    def readContent(self, path):
        f = open(path, "r")
        data = f.read()
        f.close()
        return data

    # fill TreeStore with directory structure
    def fillDirStore(self, rootDir, store, parent=None):
        subdirs = self.getSubDirList(rootDir)
        subdirs.sort()
        for s in subdirs:
            child = store.append(parent, [s])
            child_dir = rootDir + "/" + s
            self.fillDirStore(child_dir, store, child)
        
    # fill ListStore with a file list (i.e. parameters list)
    def fillParamStore(self, sel_dir, store):
        files = self.getFileNames(sel_dir)
        files.sort()
        for f in files:
            store.append([f])
