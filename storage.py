#!/usr/bin/env python
# -*- coding: utf-8 -*-
# here is the class for changed parameters' storage
class ParamStorage:
    def __init__(self):
        self.storage = {}


    def add(self, dirpath, listpath, text, subparam_index,filename):
        if self.storage.has_key(dirpath)==False:
            self.storage[dirpath] = {}
            self.storage[dirpath][listpath]=[[],'']
        try:
            value=self.storage[dirpath][listpath][0]
        except KeyError:
            self.storage[dirpath][listpath]=[[],'']
            value=self.storage[dirpath][listpath][0]            
        if len(value)<subparam_index+1:
            for i in range(len(value),subparam_index+1):
                value.append(None)
        value[subparam_index]=text
        self.storage[dirpath][listpath] = [value, filename]

    def retrieve(self, dirpath, listpath):
        if self.storage.has_key(dirpath):
            if self.storage[dirpath].has_key(listpath):
                return self.storage[dirpath][listpath][0]
        return None

    def retrieve_filename(self, dirpath, listpath):
        if self.storage.has_key(dirpath):
            if self.storage[dirpath].has_key(listpath):
                return self.storage[dirpath][listpath][1]
        return None

    def remove(self, dirpath, listpath, subparam_index):
        # subparam_index = -1 - remove all subparameters
        if self.storage.has_key(dirpath):
            if self.storage[dirpath].has_key(listpath):
                if subparam_index==-1:
                    for s in range(len(self.storage[dirpath][listpath][0])):
                        self.storage[dirpath][listpath][0][s]=None
                else:
                    self.storage[dirpath][listpath][0][subparam_index]= None
                for s in self.storage[dirpath][listpath][0]:
                    if s!=None:
                        return
                self.storage[dirpath][listpath][1]= None

    def get_dirs(self):
        return self.storage.keys()

    def get_params_from_dir(self, dirpath):
        return self.storage[dirpath].keys()

