#!/usr/bin/env python
# -*- coding: utf-8 -*-
# class for writing parameters to /proc/sys filesystem
from storage import *

class Writer:
    def __init__(self, storage):
        self.storage = storage


    def write(self, selected_dir, dirPath, listPath):
        filename = self.storage.retrieve_filename(dirPath, listPath)
        if filename==None:
            return False
        return self.writePath(selected_dir + "/" + filename,
                              dirPath, listPath)

    def writePath(self, fs_path, dirPath, listPath):        
        f = open(fs_path, "w")
        value = self.storage.retrieve(dirPath, listPath)
        if value==None:
            return False
        old_values = self.enumerate_subparams_from_file(fs_path)
        new_values = old_values
        for i in range(len(value)):
            if value[i] != None:
                new_values[i]=value[i]

        write_data=""
        for n in new_values:
            write_data = write_data + n + '\t'
        write_data.strip('\t')
        write_data = write_data + '\n'
            
        f.write(write_data)
        f.close()        
        return True        

    def enumerate_subparams_from_file(self, fs_path):
        f = open(fs_path, "r")
        param_string = f.read()
        f.close()
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
