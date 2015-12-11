#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Class for parsing description.xml file

import xml.dom.minidom

class DescriptionParser:        
    def __init__(self):
        self.description_file=None
        self.dom = None
        
    def setXMLFileName(self, filename):
        self.description_file=filename
        try:
            df = open(filename, "rw")
        except IOError:
            df = open(filename, "w")
            df.write("<?xml version=\"1.0\" encoding=\"utf-8\"?><params/>")
        df.close()
        self.dom = xml.dom.minidom.parse(self.description_file)        

    def getXMLFileName(self):
        return self.description_file


    def saveToXML(self):
        self.dom.normalize()
        data=self.dom.toxml("utf-8")
        df = open(self.description_file, "w")
        df.write(data)
        df.close()        
        self.dom = xml.dom.minidom.parse(self.description_file)        

    
    def setInfo(self, param_path, data):
        p = self.findParamByPath(param_path)
        if p==None:
            p = self.createParam(param_path)
        try:
            infotext = p.getElementsByTagName("info")[0]
            infotext.removeChild(infotext.childNodes[0])
            p.removeChild(infotext)
        except IndexError:
            # if <info> tag doesn't exist, create it
            infotext = self.dom.createElement("info")
        if len(data)!=0:
            infotext.appendChild(self.dom.createTextNode(data))
            p.appendChild(infotext)


    def findParamByPath(self, param_path):
        for p in self.dom.getElementsByTagName("param"):
            if p.getAttribute("path") == param_path:
                return p
        return None
        
    def getInfo(self, param_path):
        p = self.findParamByPath(param_path)
        if p==None:
            return None
        try:
            infotext = p.getElementsByTagName("info")[0]
            
        except IndexError:
            # If <info> tag doesn't exist, return None
            return None

        rc = ""
        for i in infotext.childNodes:
            if i.nodeType == i.TEXT_NODE:
                rc = rc + i.data
        return rc

    def isLocked(self, param_path):
        # return values:
        # True - locked XML attribute set to 1
        # False - locked XML attribute set to 0 (default!)
        # None - can't find this parameter in description XML file
        p = self.findParamByPath(param_path)
        if p==None:
            return False

        locked = p.getAttribute("locked")
        if locked=="":
            return 0
        if int(locked)>0:
            return 1
        else:
            return 0

    def setLocked(self, param_path, locked=0):
        p = self.findParamByPath(param_path)
        if p==None:
            return None

        if locked==True:
            locked=1
        else:
            locked=0
        p.setAttribute("locked", str(locked))
        return p

    def getSubParams(self, param_path):
        p = self.findParamByPath(param_path)
        if p==None:
            return None
        try:
            elements = p.getElementsByTagName("subparams")[0]
        except IndexError:
            # If <subparams> tag doesn't exist, return none
            return None
        
        subparamslist=[]
        for e in elements.childNodes:
            if e.nodeType!=e.TEXT_NODE and e.tagName=="subparam":
                subparamslist.append(e)
        return subparamslist
    
    def getSubParamsAttr(self, param_path):
        subparamslist = self.getSubParams(param_path)
        if subparamslist==None or subparamslist==[]:
            return None
        subparamstorage=[]
        for s in subparamslist:
            subparamstorage.append({'index':s.getAttribute('index'),
                                    'name':s.getAttribute('name'),
                                    'type':s.getAttribute('type'),
                                    'min':s.getAttribute('min'),
                                    'max':s.getAttribute('max'),
                                    'maxlen':s.getAttribute('maxlen')})
        # sort subparameters by index
        for i in range(len(subparamstorage)-1):
            for j in range(i+1,len(subparamstorage)):
                if(int(subparamstorage[i]['index'])>int(subparamstorage[j]['index'])):
                    tmp=subparamstorage[i]
                    subparamstorage[i]=subparamstorage[j]
                    subparamstorage[j]=tmp
        return subparamstorage
        

    def getSubParamInfo(self, param_path, subparam_index):
        p = self.findParamByPath(param_path)
        if p==None:
            return None
        subparam = self.findSubparamByIndex(p, subparam_index)
        if subparam==None:
            return None
        try:
            infotext = subparam.getElementsByTagName("subinfo")[0]
            
            if infotext.childNodes[0].nodeType == infotext.childNodes[0].TEXT_NODE:
                return infotext.childNodes[0].data            
            
        except IndexError:
            # if <subinfo> tag doesn't exist or index is wrong then return None
            return None

    def setSubParamInfo(self, param_path, subparam_index, data):
        p = self.findParamByPath(param_path)
        if p==None:
            return None
        subparam = self.findSubparamByIndex(p, subparam_index)
        if subparam==None:
            return None
        try:
            infotext = subparam.getElementsByTagName("subinfo")[0]
            subparam.removeChild(infotext)
            
        except IndexError:
            pass

        infotext = self.dom.createElement("subinfo")            
        infotext.appendChild(self.dom.createTextNode(data))
        subparam.appendChild(infotext)

            
    def getSubParamNumberItems(self, param_path, subparam_index):
        p = self.findParamByPath(param_path)
        if p==None:
            return None
        subparam = self.findSubparamByIndex(p, subparam_index)
        if subparam==None:
            return None
        itemstorage=[]
        try:
            items=subparam.getElementsByTagName("items")[0]
        except IndexError:
            # if <items> tag doesn't exist or index is wrong then return None
            return None
        for i in items.childNodes:
            if i.nodeType!=i.TEXT_NODE and i.tagName=="item":
                itemstorage.append({'value':i.getAttribute('value'),
                                    'description':i.getAttribute('description')})
        return itemstorage

    def getItemDescription(self, param_path, subparam_index, item_value):
        itemstorage = self.getSubParamNumberItems(param_path, subparam_index)
        description = None
        if itemstorage!=None or itemstorage!=[]:
            for i in itemstorage:
                if i['value']==item_value:
                    description = i['description']
                    break
        return description

    def setSubParamAttr(self,param_path, subparam_index, name="", sub_type='string',
                         sub_len=0, sub_min=0, sub_max=0):
        p = self.findParamByPath(param_path)
        if p==None:
            p = self.createParam(param_path)
        subparamslist = self.getSubParams(param_path)
        if subparamslist==None:
            s = p.appendChild(self.dom.createElement("subparams"))
            subparamslist=[]
            
        if subparamslist==[]:
            ss =  self.dom.createElement("subparam")
            subparam = s.appendChild(ss)
            subparam.setAttribute("index", str(subparam_index))
            subparam.setAttribute("name", name)
            subparam.setAttribute("type", sub_type)
            subparam.setAttribute("maxlen", str(sub_len))
            subparam.setAttribute("min", str(sub_min))
            subparam.setAttribute("max", str(sub_max))
            return subparam

        subparam = self.findSubparamByIndex(p, subparam_index)
        subparams = p.getElementsByTagName("subparams")[0]
        if subparam!=None:
            subparams.removeChild(subparam)

        subparam = subparams.appendChild(self.dom.createElement("subparam"))
        
        subparam.setAttribute("index", str(subparam_index))
        subparam.setAttribute("name", name)
        subparam.setAttribute("type", sub_type)
        subparam.setAttribute("maxlen", str(sub_len))
        subparam.setAttribute("min", str(sub_min))
        subparam.setAttribute("max", str(sub_max))            
            
        return subparam

    def setSubParamNumberItems(self, param_path, subparam_index,
                               name, itemstorage):
        subparam = self.setSubParamAttr(param_path, subparam_index, name,
                                   sub_type='number_items')
        items = self.findItemsInSubparam(subparam)
        if items!=None:
            subparam.removeChild(items)

        items = subparam.appendChild(self.dom.createElement("items"))
        
        for i in itemstorage:
            cur_item = items.appendChild(self.dom.createElement("item"))
            cur_item.setAttribute("value", str(i['value']))
            cur_item.setAttribute("description", str(i['description']))            

    def findItemsInSubparam(self, subparam):
        if subparam==None:
            return None
        try:
            items = subparam.getElementsByTagName("items")[0]
        except IndexError:        
            return None
        return items

    
    def findSubparamByIndex(self, p, subparam_index):
        try:
            elements = p.getElementsByTagName("subparams")[0]
        except IndexError:
            # if <subparams> tag doesn't exist then return None            
            return None
        for e in elements.childNodes:
            if e.nodeType!=e.TEXT_NODE and e.tagName=="subparam":
                if e.getAttribute('index')==str(subparam_index):
                    return e
        return None
        
    def createParam(self,param_path):
        p = self.findParamByPath(param_path)
        if p==None:
            # if parameter not found in XML-file then create it
            root_element = self.dom.getElementsByTagName("params")[0]
            p = self.dom.createElement("param")
            p.setAttribute("path", param_path)
            return root_element.appendChild(p)
