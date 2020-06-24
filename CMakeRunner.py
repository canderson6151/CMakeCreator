import os
import sys
import copy
import shutil
import argparse
import subprocess
import platform
import time

#############################################################################
#                                CMakeRunner.py 
#
# Author: C. Anderson
# Origin date : June 12, 2020 
#############################################################################
#
# Copyright  2020 Chris Anderson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License see
# <http://www.gnu.org/licenses/>.
#
#############################################################################
#
# A python program that invokes the ordered execution of CMakeList.txt files in
# contained within subdirectories of the directory in which this program
# is run or a specified working directory. 
# It is assumed that the CMakeFiles are those that were created using
# the CMakeCreator.py program with targets "release" and "debug" defined.
#
# This program does not invoke any installation targets  
# 
# The information contained within an input XML data file
# specifies the directories (projects) for which CMake should be executed, as 
# well as the order and any paramters to the Cmake procedure.   
#
# Typical invocation 
#
# python3 -m CMakeRunner -x <inputFile.xml> -b -r -c -v 
#
# (b = invoke CMake to build makefiles)
# (r = compile release, specify -d for debug)
# (c = run ctest)
# (v = use -V flag (verbose) for ctest)
#
# Also one can use 
#
# python -m CMakeCreator -s
#
# to obtain a sample XML data file 
# 
# Assumptions : The cmake command is always executed from within a subdirectory named build
#               of the directory containing the CMakeLists.txt file. 
#

from XML_ParameterListArray import XML_ParameterListArray

try:
    from pathlib  import Path
except Exception as e:
    print("")
    print ("XXX               Error                 XXXX") 
    print ("XXX CMakeRunner requires Python >= 3.4 XXXX")
    print ("XXX                                     XXXX") 
    exit(1)

def execCommand(command, consoleOutputFlag = False):
#
# Console output 
#
  if(consoleOutputFlag == True):
    if(platform.system() == "Darwin"):
      p = subprocess.Popen(command,shell=True,stdout=None,stderr=None)
      p.wait()
    else:
      local_env = os.environ.copy()
      p = subprocess.Popen(command,shell=True,stdout=None,stderr=None,env=local_env)
      p.wait()
    returnCode = 0
    runOutput = None
    runError  = None
    if((p.returncode != None) and (p.returncode != 0)):
      returnCode = p.returncode
    return (returnCode,runOutput,runError)
#
# Output captured in runOutput and runError 
# 
  runError  = None
  runOutput = None

  if(platform.system() == "Darwin"):
    p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  else:
    local_env = os.environ.copy() 
    p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=local_env)
  
  (runOutput,runError)  = p.communicate()
  
  returnCode = 0
  if((p.returncode != None) and (p.returncode != 0)):
    returnCode = p.returncode
  return (returnCode,runOutput,runError)

       
class CMakeRunner(object):
  
  def __init__(self):
        self.CMakeRunnerDataFile  = None
        self.localDirectory       = os.getcwd()
        self.verboseFlag          = False  
        self.releaseFlag          = False
        self.debugFlag            = False
        self.compileMode          = None
        self.ctestFlag            = False
        self.buildFlag            = False
        self.flushFlag            = False
        self.projectIndex         = None
        self.testIndex            = None

    
  def parseOptions(self):
      parser = argparse.ArgumentParser()
      parser.add_argument('--xmldatafile',  "-x",dest='xmldatafile',  default=None, help="Specify XML file containing CMakeRunner data")
      parser.add_argument('--samplefile',   "-s",action='store_true', dest='samplefileFlag', help="Creates sample XML input file with verbose commenting")
      parser.add_argument('--verbose',      "-v",action='store_true', dest='verboseFlag', help="Verbose output to screen")
      parser.add_argument('--release',      "-r",action='store_true', dest='releaseFlag', help="make release")
      parser.add_argument('--debug',        "-d",action='store_true', dest='debugFlag', help="make debug")
      parser.add_argument('--ctest',        "-c",action='store_true', dest='ctestFlag', help="run ctest")
      parser.add_argument('--build',        "-b",action='store_true', dest='buildFlag', help="build makefile")
      parser.add_argument('--flush',        "-f",action='store_true', dest='flushFlag', help="make clean")
      parser.add_argument('--project',      "-p",dest='projectIndex', default=None, help="Index of specific project to run")
      parser.add_argument('--index',        "-i",dest='testIndex',    default=None, help="Index of specific test within a project to run")

      args = parser.parse_args()
      if(args.samplefileFlag):
        sampleFile = Path(self.get_script_path())/"data"/"CMakeRunnerSample.xml"
        try :
          f = open(sampleFile,'r')
          sampleFileContents = f.read()
          f.close()
          
          fout = open("CMakeRunnerSample.xml",'w')
          fout.write(sampleFileContents)
          fout.close()
          print("Sample XML file written to : CMakeRunnerSample.xml")
          exit(0)
        except OSError as err:
          print (' === Error ===')
          print ("Sample XML file cannot be created")
          print (err)
          exit(1)
          
      self.CMakeRunnerDataFile   = args.xmldatafile
      self.verboseFlag           = args.verboseFlag
      self.releaseFlag           = args.releaseFlag
      self.debugFlag             = args.debugFlag
      self.ctestFlag             = args.ctestFlag
      self.buildFlag             = args.buildFlag
      self.flushFlag             = args.flushFlag
      
      if(args.projectIndex != None) :
        self.projectIndex = int(args.projectIndex)
      if(args.testIndex != None):
        self.testIndex = int(args.testIndex)
      
      if(self.debugFlag)   : self.compileMode = "debug"
      if(self.releaseFlag) : self.compileMode = "release"
      
      if(self.ctestFlag and (not self.debugFlag) and (not self.releaseFlag )):
          print (' === Error ===')
          print ("Compilation type flag (-d or -r) must also ")
          print ("be specified when invoking ctest (-c)")
          exit(1)
          
  def run(self): 
    
    start_time = time.monotonic()

    print ("Running CMakeRunner")
    self.CMakeCreatorDataDir = self.get_script_path() + "/data"
    
    self.parseOptions()
    if(self.CMakeRunnerDataFile  == None):
      print("Desired file containing CMakeRunner data specified with -x option ")
      sys.exit(1)

    paramList = XML_ParameterListArray(self.CMakeRunnerDataFile)

    # obtain the base path by
    
    workingDir = None
    
    if(paramList.isParameter("workingDir", "Common")):
      workingDir = paramList.getParameterText("workingDir", "Common").strip()
      if(not os.path.isdir(Path(workingDir))):
          print (' === Error ===')
          print ("Directory specified with <workingDir> parameter")
          print ("does not exit.")
          print ("Directory specified : " + workingDir)
          exit(1)
    
    if(workingDir == None):
      workingDir = os.path.dirname(os.path.abspath(self.CMakeRunnerDataFile))
    
    
    cmakeCommand = None
    makeCommand  = None
    ctestCommand = None
    if(platform.system() == "Linux"):
      
        if(self.buildFlag):
          cmakeCommand =  paramList.getParameterText("linuxCMakeCommand", "Common")
        
        if(self.compileMode != None):
          makeCommand  =  paramList.getParameterText("linuxMakeCommand","Common")
          makeCommand += " " + self.compileMode
        
        if(self.ctestFlag):
          ctestCommand =  paramList.getParameterText("linuxCtestCommand", "Common")
          if(self.verboseFlag) : ctestCommand += " -V"
       
        
    elif(platform.system() == "Darwin"):
      
        if(self.buildFlag):
          cmakeCommand =  paramList.getParameterText("macCMakeCommand", "Common")
        
        if(self.compileMode != None):
          makeCommand  =  paramList.getParameterText("macMakeCommand","Common")
          makeCommand += " " + self.compileMode
        
        if(self.ctestFlag):
          ctestCommand =  paramList.getParameterText("macCtestCommand", "Common")
          if(self.verboseFlag) : ctestCommand += " -V"
        
    elif(platform.system() == "Windows"):
      
        if(self.buildFlag):
          cmakeCommand =  paramList.getParameterText("vsCMakeCommand", "Common")
        
        if(self.compileMode != None):
          makeCommand  =  paramList.getParameterText("vsMakeCommand","Common")
          makeCommand +=  self.compileMode

        if(self.ctestFlag):
          ctestCommand =  paramList.getParameterText("vsCtestCommand", "Common")
          ctestCommand +=  self.compileMode
    
    #
    # Replace AMPERSAND with &. Used in Visual Studio commands 
    #
    OptionsList = {}  # for options list 
    
    print("---------------------------------------------------------------------")
    
    OptionList = {}
    if(cmakeCommand != None) : 
      cmakeCommand = cmakeCommand.replace("AMPERSAND","&")
      globalOptions = paramList.getParameterAll("globalCMakeOption","Common")
      for p in globalOptions:
        OptionList[p.text.split("=")[0].strip()] = p.text.split("=")[1].strip()
      print("CMake Command Used : " + cmakeCommand)

    if(makeCommand != None) : 
      print("Make Command Used  : " +  makeCommand)
    if(ctestCommand != None) : 
      print("ctest Command Used : " + ctestCommand)
    print("---------------------------------------------------------------------")

    
    paramListArray = paramList.getParameterListAll("ProjectDir")
    pTasks = []
    
    for p in paramListArray:
        LocalOptionList = {}
        LocalOptionList = copy.deepcopy(OptionList)
        localOptions    =  p.findall("localCMakeOption")
        for q in localOptions:
          LocalOptionList[q.text.split("=")[0].strip()] = q.text.split("=")[1].strip()
          
        optionString = ""
        for q in LocalOptionList.keys():
          optionString += " " + q + "=" + LocalOptionList[q] 
         
        indexInput = None
        if(p.find("index") != None) : indexInput = paramList.getValueOrText(p.find("index"))
        
        if(indexInput == None) : indexVal = "1"
        else                   : indexVal = indexInput
        print((p.text.strip(), indexVal,optionString))
        pTasks.append((p.text.strip(), indexVal,optionString))
        
    projectTasks = sorted(pTasks, key=lambda project : project[1])
    projectCount = len(projectTasks)
    projectIndex = 0
    
    summaryString = ""
    
    if(os.path.isfile(Path(workingDir)/"CMakeRunner.log")): os.remove(Path(workingDir)/"CMakeRunner.log")
    
    consoleOutputFlag = True
    returnCode = 0
    for p in projectTasks:
        if((self.projectIndex != None) and (int(p[1]) != self.projectIndex)):
          continue
        projectIndex = projectIndex + 1
        projectDir = os.path.abspath(Path(workingDir)/p[0])
        print("\n\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("[" + str(projectIndex) + "/" + str(projectCount) + "] " + projectDir)
        projectString = "[" + str(projectIndex) + "/" + str(projectCount) + "] " + p[0]  + "\n"
        summaryString += projectString
        f = open(Path(workingDir)/"CMakeRunner.log", 'a')
        f.write(projectString)
        f.flush()
        f.close()
        projectString = ""
        
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        if(os.path.isdir(projectDir)):
          
            if(self.flushFlag):
              print("+++++++++++++ Removing build and test files +++++++++++++++++++++++++")
              os.chdir(Path(projectDir))
              shutil.rmtree("build",ignore_errors=True)
              shutil.rmtree("Testing",ignore_errors=True)
                  
            if(not os.path.isdir(Path(projectDir)/"build")):
                os.mkdir(Path(projectDir)/"build")
                
            if(os.path.isdir(Path(projectDir)/"build")):
                os.chdir(Path(projectDir)/"build")
                returnCode = 0
                
                if(self.buildFlag) :
                  print("\n++++++++++++++++++++++    Running CMake     +++++++++++++++++++++++++\n")
                  if(os.path.isfile("CMakeCache.txt")) : os.remove("CMakeCache.txt")
                  command = cmakeCommand + " ../ " + p[2]
                  print("Command : " + command +"\n") 
                  (returnCode,runOutput,runError) = execCommand(command, consoleOutputFlag)
                  if(returnCode == 0): 
                    projectString += "Cmake       : passed "+ "\n"
                  else:   
                    projectString += "Cmake       : failed "+ "\n"         

                if((returnCode == 0) and (self.compileMode != None)):
                    print("\n++++++++++++++++++++++    Compiling         +++++++++++++++++++++++++\n")
                    print("Command : " + makeCommand +"\n") 
                    (returnCode,runOutput,runError) = execCommand(makeCommand, consoleOutputFlag)
                    if(returnCode == 0): 
                      projectString += "Compilation : passed "+ "\n"
                    else               : 
                      projectString += "Compilation : failed "+ "\n"


                if((returnCode == 0) and (self.ctestFlag)):
                    print("\n+++++++++++++++++++++     Running Tests      ++++++++++++++++++++++++\n")
                    
                    if((self.testIndex != None) and (self.projectIndex != None)) :
                      ctestCommand += " -I " + str(self.testIndex) + "," + str(self.testIndex) 
                    print("Command : " + ctestCommand +"\n") 
                    (returnCode,runOutput,runError) = execCommand(ctestCommand, consoleOutputFlag)
                    if(returnCode == 0): 
                      projectString += "Ctest       : passed "+ "\n"
                    else               : 
                      projectString += "Ctest       : failed "+ "\n"
                    
                    os.chdir(Path(projectDir)/"build")
                    shutil.copyfile(Path(projectDir)/"build"/"Testing"/"Temporary"/"LastTest.log",Path(projectDir)/"Testing"/"LastTest.log")
                    print("Output log file : " + str(Path(projectDir)/"Testing"/"LastTest.log")) 
                    print("\n+++++++++++++++++++++     Tests Finished     ++++++++++++++++++++++++\n\n")   
                summaryString += "\n"
                projectString += "\n" 
                summaryString += projectString

                f = open(Path(workingDir)/"CMakeRunner.log", 'a')
                f.write(projectString)
                f.flush()
                f.close()
                
        os.chdir(self.localDirectory)
      
    print("\n")
    print("XXXXXXXXXXXXXXXXXXX         SUMMARY       XXXXXXXXXXXXXXXXXXXXXXXXXXX\n\n")
    print(summaryString)
    
    print("\n")
    elapsed_time = time.monotonic() - start_time
    print("Elapsed time (sec) : " + str(elapsed_time))
    print("Elapsed time (min) : " + str(elapsed_time/60.0))  
    print("Elapsed time (hrs) : " + str(elapsed_time/360.0))


#
#=========== Local utility routines  ============================
#   

# Returns the location of the python program that was invoked 

  def get_script_path(self):
    return os.path.dirname(os.path.realpath(sys.argv[0]))
   

#   
#
#   Stub for executing the class defined in this file 
#   
if __name__ == '__main__':
  cMakeRunner = CMakeRunner()
  cMakeRunner.run()
  
  
