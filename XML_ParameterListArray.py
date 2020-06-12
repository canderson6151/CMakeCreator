#!/usr/bin/env python3
import sys
import os
from copy import deepcopy

import xml.etree.ElementTree as ET

TRUE_VALS  = ( '1', 'true',  'True', 'TRUE',  'y', 'yes', 'Y', 'Yes', 'YES','ON',"on","On")
FALSE_VALS = ( '0', 'false', 'False', 'FALSE','n', 'no',  'N', 'No',   'NO',"OFF","off","Off")

class XML_ParameterListArray:
    def __init__(self,fileName = None):
        self.tree     = None
        self.root     = None
        self.fileName = fileName
        
        if(self.fileName != None):
            self.tree = ET.parse(fileName)
            self.root = self.tree.getroot()
            
    def deepcopy(self,xml_ParameterListArray):
        self.tree = deepcopy(xml_ParameterListArray)
        self.root = self.tree.getroot()
        
    def createParameterListArray(self,listArrayName):
        self.tree = ET.ElementTree(ET.Element(listArrayName))
        self.root = self.tree.getroot()
    
    def addParameterList(self,paramListName):
        if(self.tree.find(paramListName) != None):
            raise Exception("Duplicate parameter lists not allowed",paramListName)
        self.root.append(ET.Element(paramListName))
    #
    # The type of the parameter is determined by the value specified. If
    # None is specified, then the type and value attributes are not set
    #   
    def addParameter(self,value,parameterName, parameterListName):
        parameterList = self.tree.find(parameterListName)
        if(parameterList == None):
            raise Exception("Insertion of parameter in non-existent parameter list : ",parameterListName)
        
        if(value == None): 
            parameterList.append(ET.Element(parameterName))
            return
        
        valStr,typeStr = self.getValueAndTypeAsString(value)
        parameterList.append(ET.Element(parameterName,dict(type=typeStr,value=valStr)))
    
    def getParameterValue(self,parameterName, parameterListName):
        parameterList = self.tree.find(parameterListName)
        if(parameterList == None):
            raise Exception("\n ParameterList not found \n ParameterList specified  : " + parameterListName)
        instance = parameterList.find(parameterName)
        if(instance == None):
            raise Exception("\n Parameter not found in ParameterList \n ParmeterList : " + parameterListName \
                             + "\n Parameter    : " + parameterName)

        return self.getValue(instance)
    
    def getParameterValueOrText(self,parameterName, parameterListName):
        parameterList = self.tree.find(parameterListName)
        if(parameterList == None):
            raise Exception("\n ParameterList not found \n ParameterList specified  : " + parameterListName)
        instance = parameterList.find(parameterName)
        if(instance == None):
            raise Exception("\n Parameter not found in ParameterList \n ParmeterList : " + parameterListName \
                             + "\n Parameter    : " + parameterName)

        return self.getValueOrText(instance)
    
    def getParameterText(self,parameterName, parameterListName):
        parameterList = self.tree.find(parameterListName)
        if(parameterList == None):
            raise Exception("\n ParameterList not found \n ParameterList specified  : " + parameterListName)
        instance = parameterList.find(parameterName)
        if(instance == None):
            raise Exception("\n Parameter not found in ParameterList \n ParmeterList : " + parameterListName \
                             + "\n Parameter    : " + parameterName)

        return instance.text.strip()
      
    def getParameterAll(self,parameterName, parameterListName):
        parameterList = self.tree.find(parameterListName)
        if(parameterList == None):
            raise Exception("\n ParameterList not found \n ParameterList specified  : " + parameterListName)
        parameters = parameterList.findall(parameterName)
        if(parameters == None):
            raise Exception("\n Parameter not found in ParameterList \n ParmeterList : " + parameterListName \
                             + "\n Parameter    : " + parameterName)

        return parameters

    def getParameterValueOrDefault(self,parameterName, parameterListName,defaultValue):
        parameterList = self.tree.find(parameterListName)
        if(parameterList == None):
            raise Exception("\n ParameterList not found \n ParameterList specified  : " + parameterListName)
        instance = parameterList.find(parameterName)
        parameterValue = defaultValue;
        if(instance != None):
            parameterValue = self.getValue(instance)  
        return parameterValue
    
    def getParameterNames(self,parameterListName):
        parameterList = self.tree.find(parameterListName)
        if(parameterList == None):
            raise Exception("\n ParameterList not found \n ParameterList specified  : " + parameterListName)
        
        parameterNames = []
        for parameter in parameterList:
            parameterNames.append(parameter.tag)
        return parameterNames
    
    def isParameterList(self,parameterListName):
        parameterList = self.tree.find(parameterListName)
        if(parameterList == None): return False       
        return True
    
    def isParameter(self,parameterName,parameterListName):
        parameterList = self.tree.find(parameterListName)
        if(parameterList == None):
            raise Exception("\n ParameterList not found \n ParameterList specified  : " + parameterListName)
        instance = parameterList.find(parameterName)
        if(instance == None): return False
        return True
    
    def getParameterList(self,parameterListName):
        parameterList = self.tree.find(parameterListName)
        if(parameterList == None):
            raise Exception("\n ParameterList not found \n ParameterList specified  : " + parameterListName)
        
        return parameterList
        
    def getParameterListAll(self, parameterListName):
        parameterList = self.tree.findall(parameterListName)
        if(parameterList == None):
            raise Exception("\n ParameterList not found \n ParameterList specified  : " + parameterListName)
        
        return parameterList
    
    def getParameterChildNames(self,parameterName,parameterListName):
        parameterList = self.tree.find(parameterListName)
        if(parameterList == None):
            raise Exception("\n ParameterList not found \n ParameterList specified  : " + parameterListName)
        instance = parameterList.find(parameterName)
        if(instance == None):
            raise Exception("\n Parameter not found in ParameterList \n ParmeterList : " + parameterListName \
                             + "\n Parameter    : " + parameterName)
        childNames = []
        for childParam  in instance:
            childNames.append(childParam.tag)
        return childNames
    
    def getParameterChildValues(self,parameterChildName,parameterName,parameterListName):
        parameterList = self.tree.find(parameterListName)
        if(parameterList == None):
            raise Exception("\n ParameterList not found \n ParameterList specified  : " + parameterListName)
        instance = parameterList.find(parameterName)
        if(instance == None):
            raise Exception("\n Parameter not found in ParameterList \n ParmeterList : " + parameterListName \
                             + "\n Parameter    : " + parameterName)
        
        childParams = instance.findall(parameterChildName)
        if(childParams == []):
            raise Exception("\n Child parameter not found  \n ParmeterList   : " + parameterListName \
                             + "\n Parameter      : "  + parameterName   \
                             + "\n ChildParameter : " + parameterChildName)  
        childValues = []
        for p  in childParams:
            childValues.append(self.getValue(p))
        return childValues
    #
    # Adds a child value to all instances of the specified parameter in the
    # specified parameterList.
    #
    # If the parameter specified does not exist, then it is created
    #
    def addParameterChild(self, value, childName, parameterName, parameterListName): 
        parameterList = self.root.find(parameterListName)
        if(parameterList.findall(parameterName) == []):
            self.addParameter(None,parameterName,parameterListName)
    
        for instance in parameterList.findall(parameterName):
            if(instance.get("value") != None):
                raise Exception("Adding child to a parameter with value not allowed",childName,parameterName,parameterListName)
            if(value == None):
                if(instance.find(childName) != None):
                    raise Exception("Duplicate child parameters not allowed",childName,parameterName,parameterListName)
                else:
                    instance.append(ET.Element(childName))
            else:
                if(instance.find(childName)!= None):
                    raise Exception("Duplicate child parameters not allowed",childName,parameterName,parameterListName)
                else:
                    valStr,typeStr = self.getValueAndTypeAsString(value)
                    instance.append(ET.Element(childName,dict(type=typeStr,value=valStr)))
    
    #addParameterInstanceChild(XML_dataType value, int instanceIndex, const char* parameterChildName,
    #const char* parameterName, const char* parameterListName)       
                
    def getValueAndTypeAsString(self,value):
        if(type(value) is float): 
            typeStr = "float"
            valStr  = '{0:16.15e}'.format(value)
        elif(type(value) is bool) : 
            typeStr = "bool"
            if(value): valStr = "true"
            else:      valStr = "false"
        elif(type(value) is int) : 
            typeStr = "int"
            valStr  = '{0:d}'.format(value)
        elif(type(value) is str) : 
            typeStr = "string"
            valStr  = value
        else:
            raise Exception("Unacceptable value for parameter ",value,type(value))
        
        return valStr,typeStr
    
    def run(self):
        self.tree = ET.parse('XMLoutput.xml')
        #root = ET.fromstring(country_data_as_string)
        self.root = self.tree.getroot()
        
        # Returns the name of the containing XML node
        
        print(self.root.tag)
        
        # Returns the names of the parameter lists (there are no attributes)
        
        for parameterList in self.root:
            # prints the parameter list name 
            
            print ("ParameterListName: ",parameterList.tag)
            
            # Print the parameter name and attributes
 
            for parameter in parameterList:
                if(len(list(parameter)) == 0):
                    valueType = self.getType(parameter)
                    parameter.set('type',valueType)
                    print("    Parameter : ",parameter.tag,parameter.attrib,self.getValue(parameter),valueType)
                    
                else:
                    print("    Parameter : ",parameter.tag)
                    for child in parameter:
                        valueType = self.getType(child)
                        child.set('type',valueType)
                        print("         ",child.tag,child.attrib,self.getValue(child),valueType)
        
        self.outputToFile("XMLoutput2.xml")
    #
    # This outputs the xml parameter list to a file, and changes types
    # of float to double and int to long, since the float in python
    # typically gets mapped to a C (C++) double and an int to 32 bit C (C++)
    # integers = long for most C (C++) compilers. 
    #
    def outputToFile(self,fileName):
        outputTree = deepcopy(self.tree)
        root       = outputTree.getroot()

        # revert output types to longs and doubles 
 
        for parameterList in root:
            for parameter in parameterList:
                if(len(list(parameter)) == 0):
                    valueType = self.getType(parameter)
                    if(valueType != None):
                        if(valueType == "float"): valueType = "double"
                        if(valueType == "int")  : valueType = "long"
                        parameter.set('type',valueType)
                else:
                    for child in parameter:
                        valueType = self.getType(child)
                        if(valueType == "float"): valueType = "double"
                        if(valueType == "int")  : valueType = "long"
                        child.set('type',valueType)
                        child.set('type',valueType)
        fileOut = open(fileName,"w")
        fileOut.write("<?xml version=\"1.0\" standalone=\"no\" ?>\n")
        fileOut.write((ET.tostring(root)).decode('utf-8'))
        fileOut.close()
               
    def getType(self,paramElement):
        valType = paramElement.get("type",None)
        if(valType != None) : 
            if(valType == "double"): return "float"
            if(valType == "long"):   return "long"
            return valType
        
        strVal = paramElement.get("value",None)
        if(strVal == None):
            raise ValueError("value attribute not specified in ",paramElement)
        
        try:
            float(strVal)
            if(strVal.find(".") >= 0) : return "float"
            else:                       return "int"
        except ValueError:
            if( (strVal in TRUE_VALS) or (strVal in FALSE_VALS)): 
                return "bool"
            return "string"    
    
    def hasValueSpecified(self,paramElement):
        strVal  = paramElement.get("value",None)
        if(strVal == None): return False
        return True
    
    def getTextSpecification(self,paramElement):
        valType = paramElement.get('type',None)
        strVal  = paramElement.text
        if(strVal == None):
            raise ValueError("value attribute not specified in ",paramElement)
        
        if(valType != None) : 
            try:
                if(valType == "string"): return strVal
                if(valType == "float") : return float(strVal)
                if(valType == "double"): return float(strVal)
                if(valType == "int")   : return int(strVal)
                if(valType == "long")  : return int(strVal)
                if(valType == "bool")  : 
                    if(strVal in TRUE_VALS) : return True
                    if(strVal in FALSE_VALS): return False
            except:
                raise ValueError("type inconsistent with value specified or type un-supported",\
                                 paramElement).with_traceback(sys.exc_info()[2])
        
        try:
            float(strVal)
            if(strVal.find(".") >= 0) : return float(strVal) 
            else:                       return int(strVal)
        except ValueError:
            if(strVal in TRUE_VALS):
                return True 
            if(strVal in FALSE_VALS) : 
                return False 
            return strVal 

    def getValueOrText(selfself,paramElement):
        val = paramElement.get('value',None)
        if(val == None):
            if(paramElement.text != None):
               if(len(paramElement.text.strip()) != 0) : return paramElement.text.strip()
               return None
        else:
            if(len(val.strip()) != 0) : return val.strip()
            return None
 
           
    def getValue(self,paramElement):
        valType = paramElement.get('type',None)
        strVal  = paramElement.get("value",None)
        if(strVal == None):
            raise ValueError("value attribute not specified in ",paramElement)
        
        if(valType != None) : 
            try:
                if(valType == "string"): return strVal
                if(valType == "float") : return float(strVal)
                if(valType == "double"): return float(strVal)
                if(valType == "int")   : return int(strVal)
                if(valType == "long")  : return int(strVal)
                if(valType == "bool")  : 
                    if(strVal in TRUE_VALS) : return True
                    if(strVal in FALSE_VALS): return False
            except:
                raise ValueError("type inconsistent with value specified or type un-supported",\
                                 paramElement).with_traceback(sys.exc_info()[2])
        
        try:
            float(strVal)
            if(strVal.find(".") >= 0) : return float(strVal) 
            else:                       return int(strVal)
        except ValueError:
            if(strVal in TRUE_VALS):
                return True 
            if(strVal in FALSE_VALS) : 
                return False 
            return strVal 
    
        
if __name__ == '__main__':
    xml_ParameterListArray = XML_ParameterListArray()
    xml_ParameterListArray.createParameterListArray("NewArray")
    xml_ParameterListArray.addParameterList("NewParameterList")
    xml_ParameterListArray.addParameterChild("10","Age","NewParameter","NewParameterList")
    ET.dump(xml_ParameterListArray.root)
    

        
