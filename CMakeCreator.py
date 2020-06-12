import os
import sys
import argparse
import subprocess
from datetime import datetime



from XML_ParameterListArray import XML_ParameterListArray
from string import Template

import sys
try:
    from pathlib  import Path
except Exception as e:
    print("")
    print ("XXX               Error                 XXXX") 
    print ("XXX CMakeCreator requires Python >= 3.4 XXXX")
    print ("XXX                                     XXXX") 
    exit(1)

#
# A python program that constructs a CMakeLists.txt file by 
# combining information contained within an input XML data file
# and code snippets contained in the /data subdirectory. 
#
# Typical invocation 
#
# python3 -m CMakeCreator -x <inputFile.xml> 
#
# To obtain a sample XML data file that's heavily annotated use the command 
#
# python -m CMakeCreator -s
#
# To obtain a sample XML data file that's minimally annotated, use the command
#
# python -m CMakeCreator -b 
#
# 
# Changes to the default values used to create CMakeLists.txt files can
# be implemented by modifying the contents of the CMake code snippets stored 
# in the /data subdirectory. 
#
# Chris Anderson : June, 3, 2020 
#
        
class CMakeCreator(object):
  
  def __init__(self):
        self.CMakeCreatorDataDir = None
        self.CMakeListDataFile   = None
        self.localDirectory      = os.getcwd()
        self.verboseFlag         = False
        self.timeStampFlag       = True
        
        self.linuxDebugOptions            = None
        self.visualStudioDebugOptions     = None
        self.macDebugOptions              = None
    
        self.linuxReleaseOptions           = None
        self.visualStudioReleaseOptions    = None
        self.macReleaseOptions             = None 
        self.forceOverwriteFlag            = False     

        
  def parseOptions(self):
      parser = argparse.ArgumentParser()
      parser.add_argument('--xmldatafile',"-x",dest='xmldatafile',default=None, help="Specify XML file containing CMakeLists.txt construction data")
      parser.add_argument('--samplefile',"-s",action='store_true', dest='samplefileFlag', help="Creates sample XML input file with verbose commenting")
      parser.add_argument('--basicSamplefile',"-b",action='store_true', dest='basicSamplefileFlag', help="Creates sample XML input file with minimal commenting.")
      parser.add_argument('--verbose',"-v",action='store_true', dest='verboseFlag', help="Output to screen and CMakeLists.txt file")
      parser.add_argument('--force',"-f",action='store_true', dest='forceFlag', help="Force automatic overwrite of existing CMakeLists.txt file")
      parser.add_argument('--notimestamp',"-n",action='store_true', dest='noStampFlag', help="Don't add timestamp to CMakeLists.txt file")
      
      args = parser.parse_args()
      if(args.samplefileFlag):
        sampleFile = Path(self.get_script_path())/"data"/"CMakeCreatorSample.xml"
        try :
          f = open(sampleFile,'r')
          sampleFileContents = f.read()
          f.close()
          
          fout = open("CMakeCreatorSample.xml",'w')
          fout.write(sampleFileContents)
          fout.close()
          print("Sample XML file written to : CMakeCreatorSample.xml")
          exit()
        except OSError as err:
          print (' === Error ===')
          print ("Sample XML file cannot be created")
          print (err)
          exit()
      if(args.basicSamplefileFlag):
        sampleFile = Path(self.get_script_path())/"data"/"CMakeCreatorSampleThin.xml"
        try :
          f = open(sampleFile,'r')
          sampleFileContents = f.read()
          f.close()
          
          fout = open("CMakeCreatorSample.xml",'w')
          fout.write(sampleFileContents)
          fout.close()
          print("Basic sample XML file written to : CMakeCreatorSample.xml")
          exit()
        except OSError as err:
          print (' === Error ===')
          print ("Sample XML file cannot be created")
          print (err)
          exit()
      self.CMakeListDataFile   = args.xmldatafile
      self.verboseFlag         = args.verboseFlag
      self.forceOverwriteFlag  = args.forceFlag
      if(args.noStampFlag) : 
        self.timeStampFlag = False
      
    
  def run(self): 
    
    print ("Running CMakeCreator")
    self.CMakeCreatorDataDir = self.get_script_path() + "/data"
    
    self.parseOptions()
    if(self.CMakeListDataFile  == None):
      print("Desired file containing CMakeLists data specified with -x option ")
      sys.exit(1)

          
    paramList = XML_ParameterListArray(self.CMakeListDataFile)
    
    fragmentFile = "CMakeBaseFrag.tpl"
    fragmentData = {}
    fragmentData["required_cmake"]      = paramList.getParameterValueOrText("required_cmake","Common")
    fragmentData["project"]             = paramList.getParameterValueOrText("project","Common")
    fragmentData["XML_InputFile"]       = self.CMakeListDataFile
    
    if(self.timeStampFlag):
      fragmentData["Date"]              =  '{0:%Y-%m-%d }'.format(datetime.now())
    else:
     fragmentData["Date"]               =  ""
    #################################################################
    #################################################################
    #                  Common settings
    #################################################################
    #################################################################
    
    #
    # Start off with text in CMakeBaseFrag to specify
    # required version, project name and build information
    #
    
    cmakeContents = self.createFragment(fragmentFile,fragmentData)
    
    
    #
    # Capture global include directories
    #
    
    cmakeContents += "#\n"
    cmakeContents += "# Global include directories \n"
    cmakeContents += "#\n"
    cmakeContents += "\n"
    cmakeContents += "list(APPEND IncludeDirs \"${CMAKE_SOURCE_DIR}\")\n" 
    

    commonList = paramList.getParameterList("Common")
      
    if(commonList != None):
        for p in commonList:
            if(p.tag == "IncludeDirs"):
                directories = p.findall("dir")
                for q in directories:
                    cmakeContents += "list(APPEND IncludeDirs \"${CMAKE_SOURCE_DIR}/" + paramList.getValueOrText(q) + "\")\n"                   
    
    #
    # Capture additional compiler options  
    #
    options = ""
    self.linuxDebugOptions         = ""
    self.visualStudioDebugOptions  = ""
    self.macDebugOptions           = ""
    if(commonList != None):
        for p in commonList:
            if(p.tag == "AdditionalDebugOptions"):
                optionValues = None
                optionValues = p.findall("linuxOption")
                for q in optionValues:
                    options = paramList.getValueOrText(q)
                    if(options != None) : optionSplit = options.split(",")
                    else                : optionSplit = {}
                    for r in optionSplit :
                      self.linuxDebugOptions += "\"" + r.strip().replace("\"","\\\"") + "\" "
                
                optionValues = None
                optionValues = p.findall("visualStudioOption")
                for q in optionValues:
                    options = paramList.getValueOrText(q)
                    if(options != None) : optionSplit = options.split(",")
                    else                : optionSplit = {}
                    for r in optionSplit :
                      self.visualStudioDebugOptions += "\"" + r.strip().replace("\"","\\\"") + "\" "
                      
                optionValues = None       
                optionValues = p.findall("macOption")
                for q in optionValues:
                    options = paramList.getValueOrText(q)
                    if(options != None) : optionSplit = options.split(",")
                    else                : optionSplit = {}
                    for r in optionSplit :
                      self.macDebugOptions += "\"" + r.strip().replace("\"","\\\"") + "\" "       
     
    self.linuxReleaseOptions         = ""
    self.visualStudioReleaseOptions  = ""
    self.macReleaseOptions           = ""
    
    if(commonList != None):
        for p in commonList:
            if(p.tag == "AdditionalReleaseOptions"):
                optionValues = None
                optionValues = p.findall("linuxOption")
                for q in optionValues:
                    options = paramList.getValueOrText(q)
                    if(options != None) : optionSplit = options.split(",")
                    else                : optionSplit = {}
                    for r in optionSplit :
                      self.linuxReleaseOptions += "\"" + r.strip().replace("\"","\\\"") + "\" "
                    
                optionValues = None
                optionValues = p.findall("visualStudioOption")
                for q in optionValues:
                    options = paramList.getValueOrText(q)
                    if(options != None) : optionSplit = options.split(",")
                    else                : optionSplit = {}
                    for r in optionSplit :
                      self.visualStudioReleaseOptions += "\"" + r.strip().replace("\"","\\\"") + "\" "
                      
                optionValues = None      
                optionValues = p.findall("macOption")
                for q in optionValues:
                    options = paramList.getValueOrText(q)
                    if(options != None) : optionSplit = options.split(",")
                    else                : optionSplit = {}
                    for r in optionSplit :
                      self.macReleaseOptions += "\"" + r.strip().replace("\"","\\\"") + "\" "
                           
    #                                 
    # Specify cmake modules directory paths
    #
    
    CMakeModulesDirSet = False
    if(commonList != None):
        for p in commonList:
            if(p.tag == "CMakeModulesDir"):
                cmakeContents += "\n"
                cmakeContents += "#\n"
                cmakeContents += "# Cmake modules directories \n"
                cmakeContents += "#\n"
                cmakeContents += "\n"
                directories = p.findall("dir")
                for q in directories:
                    cmakeContents += "list(APPEND CMAKE_MODULE_PATH \"${CMAKE_SOURCE_DIR}/" + paramList.getValueOrText(q) + "\")\n"
                    CMakeModulesDirSet = True
    
    #
    #################################################################
    # Specify libraries to be built as specified by option values 
    #################################################################
    #
    
    externalLibraryFlag = False
    libraryCount        = 0
    toggleVal           = "OFF"
    if(commonList != None):
        for p in commonList:
            if(p.tag == "Library"): 
                libraryCount += 1
                if(libraryCount == 1):
                    cmakeContents += "\n"
                    cmakeContents += "\n"
                    cmakeContents += "#####################################################\n"
                    cmakeContents += "# Invoke build of supporting libraries (projects)    \n"
                    cmakeContents += "#####################################################\n"
    
                externalLibraryFlag = True            
                cmakeContents += "\n"
                libDir  = p.find("libDir")
                libName = p.find("libName")
                cmakeContents += "add_subdirectory(\"${CMAKE_SOURCE_DIR}/" + paramList.getValueOrText(libDir) + "\" "
                cmakeContents += "\"${CMAKE_SOURCE_DIR}/" + paramList.getValueOrText(libDir) + "/build\")\n"
                cmakeContents +=  "list(APPEND ExternalLibs \"" + paramList.getValueOrText(libName) +  "\")\n"
      
    OptionNames = []
    if(paramList.isParameterList("Options")):
      OptionNames = paramList.getParameterNames("Options")
    
    if(OptionNames != []):
        cmakeContents += "\n"
        cmakeContents += "#####################################################\n"
        cmakeContents += "# Collecting data for components specified by options \n"
        cmakeContents += "#####################################################\n"
    
        cmakeContents += "\n#\n"
        cmakeContents += "# Specify cmake option value using -DOption_Name=ON (or = OFF)  \n" 
        cmakeContents += "# to override default\n"
        cmakeContents += "#\n"

    for p in OptionNames :
        val = str(paramList.getParameterValueOrText(p,"Options")).strip()
        if(val in self.TRUE_VALS) : toggleVal = "ON"
        if(val in self.FALSE_VALS): toggleVal = "OFF"
        cmakeContents += "\nOPTION(" + p + "  \"Option " + p + "\"  " + toggleVal + ")" 
    
    lapackFlag = False
    for p in OptionNames :
        if((p == "USE_LAPACK")):
            cmakeContents += "\n"
            cmakeContents += self.getFragment("LapackFrag.dat")
            lapackFlag = True
        if((p == "USE_OPENMP")):
            cmakeContents += "\n"
            cmakeContents += self.getFragment("OpenMPfrag.dat")
        if((p == "USE_FFTW")):
            cmakeContents += "\n"
            cmakeContents += self.getFragment("FFTWfrag.dat")
            if(not CMakeModulesDirSet) :
                print("Warning : cmake_modules directory path containing FindFFTW.cmake not set. ")
                print("          Add CMakeModulesDir parameter specifying cmake_modules path  ")
                print("          or remove option USE_FFTW. ")       
        if((p == "USE_SQLITE3")):
            cmakeContents += "\n"
            cmakeContents += self.getFragment("SQlite3frag.dat") 
        if((p == "USE_MEMCHECK")):
            cmakeContents += "\n"
            cmakeContents += self.getFragment("MemCheckFrag.dat")             



    # Enable testing if specified in any of the targets
    
    targetParamsTemp = paramList.getParameterList("BuildTargets")
    targetParams = []
    for p in targetParamsTemp:
      if(p.tag == "Target") : targetParams.append(p)
        
    ctestingFlag    = False
    for p in targetParams:
        ctestFlagParam = p.find("ctest")
        if(ctestFlagParam != None) : 
            ctestingFlag = False
            ctestingFlag = (str(paramList.getValueOrText(ctestFlagParam)) in self.TRUE_VALS)
            

    if(ctestingFlag) :
        cmakeContents += "\n"
        cmakeContents += "#\n"
        cmakeContents += "# Enable testing and create directories for testing \n"
        cmakeContents += "#\n"
        cmakeContents += "\n"  
        cmakeContents += "enable_testing()\n\n"
        
    #################################################################
    #################################################################
    #                   Specify targets 
    #################################################################
    #################################################################
    
    
    targetParamsTemp = paramList.getParameterList("BuildTargets")
    targetParams = []
    for p in targetParamsTemp:
      if(p.tag == "Target") : targetParams.append(p)
    
    # 
    #  Create a list of main sources and directories for testing
    # output
    #
    

    Main_Sources = ""
    
    ctestingFlag    = False
    for p in targetParams:
        mainSource     = None
        mainParam      = p.find("main")

        if(mainParam == None):
            raise Exception("\nError:  <main = ... > parameter specifying main source\n        not specified in <Target>  \n ")
            
        mainSource     = paramList.getValueOrText(mainParam)
        Main_Sources   += "\"" + mainSource + "\" "
        
        ctestFlagParam = p.find("ctest")
        if(ctestFlagParam != None) : 
            ctestFlag = False
            ctestFlag = (str(paramList.getValueOrText(ctestFlagParam)) in self.TRUE_VALS)
            if(ctestFlag) : 
                ctestingFlag = True 
                cmakeContents += "file(MAKE_DIRECTORY \"${CMAKE_SOURCE_DIR}/Testing/" + mainSource.split(".")[0] + "\")\n"
                
        
    cmakeContents += "\n"
    cmakeContents += "#####################################################\n"
    cmakeContents += "# Specify list of target sources containing \"main\"  \n"
    cmakeContents += "#####################################################\n"
           

    cmakeContents += "\n"
    cmakeContents += "set(Main_Sources " + Main_Sources + ")\n"


    #
    #################################################################
    # Loop over targets, specifying target specific information 
    #################################################################
    #
    
    cmakeContents +=  "\n#\n"
    cmakeContents +=  "#   Loop over build commands for each target  \n"
    cmakeContents +=  "#\n"
    
    
    cmakeContents += "\n"  
    cmakeContents +=  "foreach(mainFile ${Main_Sources} )\n"
    cmakeContents +=  "string( REPLACE \".cpp\" \"\" mainExecName ${mainFile} )\n\n"
    

    for p in targetParams:
        mainSource            = None
        additionalSources     = []
        additionalIncludeDirs = []
        ctestFlag             = False
        inputFiles            = []
        commandLineArguments  = None
        defaultXML            = False
            
        sourceFileList = ""  
        if(p.tag == "Target"):
            
            mainParam      = p.find("main")

            if(mainParam == None):
                raise Exception("\nError:  <main = ... > parameter specifying main source\n        not specified in <Target>  \n ")
            
            mainSource      = paramList.getValueOrText(mainParam)
            sourceFileList += "\"" + mainSource + "\" "
            
            additionalSourceParam = p.findall("additionalSource")
            for q in additionalSourceParam :
                additionalSources.append(paramList.getValueOrText(q))
            for q in additionalSources :
                sourceFileList +=   "\"" + q + "\" "  
            
            
            cmakeContents +=  "##################################################################\n"
            cmakeContents +=  "#   Target :  " + mainSource.split(".")[0]  + "\n"
            cmakeContents +=  "##################################################################\n"
    
            cmakeContents += "\n"
            cmakeContents += "    if(\"${mainExecName}.cpp\" STREQUAL \"" + mainSource + "\")\n"
            cmakeContents += "      add_executable( ${mainExecName} " + sourceFileList + ")\n"
            

            if(len(OptionNames) != 0) : 
                cmakeContents +=  "#\n"
                cmakeContents +=  "#     Supporting libraries and include directories \n"
                cmakeContents +=  "#\n"
    
            
            for q in OptionNames :
                
                if((q == "USE_LAPACK")):
                    cmakeContents += "      if(USE_LAPACK) \n"
                    cmakeContents += "          target_link_libraries(${mainExecName}  PUBLIC  ${LAPACK_LIBRARIES})\n"
                    cmakeContents += "      endif()\n\n"                    
                    
                if((q == "USE_OPENMP")):
                    cmakeContents += "      if(OpenMP_CXX_FOUND) \n"
                    cmakeContents += "         target_link_libraries(${mainExecName} PUBLIC OpenMP::OpenMP_CXX)\n"
                    cmakeContents += "      endif()\n\n"
                    
                if((q == "USE_FFTW")):
                    #if(not lapackFlag) : cmakeContents += "      target_link_libraries(${mainExecName}  PUBLIC  ${LAPACK_LIBRARIES})\n"
                    cmakeContents += "      if(USE_FFTW) \n"
                    cmakeContents += "          target_link_libraries(${mainExecName}  PUBLIC  ${FFTW_LIBRARIES})\n"
                    cmakeContents += "          target_include_directories(${mainExecName}  PUBLIC  ${FFTW_INCLUDES})\n"
                    cmakeContents += "      endif()\n\n"
                        
                if((q == "USE_SQLITE3")):
                    cmakeContents += "      if(USE_SQLITE3) \n"
                    cmakeContents += "          target_link_libraries(${mainExecName}  PUBLIC  ${SQLite3_LIBRARIES})\n"
                    cmakeContents += "          target_include_directories(${mainExecName} PUBLIC  ${SQLite3_INCLUDE_DIRS})\n"
                    cmakeContents += "      endif()\n\n"
                      
            if(externalLibraryFlag):
                cmakeContents += "\n"
                cmakeContents += "      target_link_libraries(${mainExecName} PUBLIC ${ExternalLibs})\n"
 
            cmakeContents += "\n"
            cmakeContents += "      target_include_directories(${mainExecName} PUBLIC ${IncludeDirs} ) \n"
            
                      
            additionalIncludeParam = p.findall("additionalIncludeDir")
            for q in additionalIncludeParam :
                additionalIncludeDirs.append(paramList.getValueOrText(q))
            for q in additionalIncludeDirs :
                cmakeContents += "      target_include_directories(${mainExecName} PUBLIC \"" + q +"\" )\n"
                
            ctestFlagParam = p.find("ctest")
            if(ctestFlagParam != None) : 
                ctestFlag = False
                ctestFlag = (str(paramList.getValueOrText(ctestFlagParam)) in self.TRUE_VALS)
                 
            
            if(ctestFlag):
                
                cmakeContents +=  "\n"
                cmakeContents +=  "#      --- Commands for ctest setup ---  \n"

                #cmakeContents +=  "\n"
                #cmakeContents +=  "#     Command to induce the creation of Testing/"+ mainSource.split(".")[0]  + " directory \n"
                
                
                #cmakeContents += "\n"
                #cmakeContents += "      add_custom_target(\"createTestOutputDir_${mainExecName}\" ALL \n"
                #cmakeContents += "      COMMAND ${CMAKE_COMMAND} -E make_directory \"${CMAKE_SOURCE_DIR}/Testing/${mainExecName}\")\n"
                
                inputFilesParam = p.findall("inputFile")
                for q in inputFilesParam :
                    inputFiles.append(paramList.getValueOrText(q))
                if(len(inputFiles) != 0) : 
                    cmakeContents += "\n"
                    cmakeContents +=  "#     Copy test input files to Testing/"+ mainSource.split(".")[0]  + " \n\n"
                    
                    
                for q in inputFiles :
                    cmakeContents += "      file(COPY \""+ q + "\"  DESTINATION \"${CMAKE_SOURCE_DIR}/Testing/${mainExecName}\")\n"
                
                defaultXMLParam = p.find("defaultXML")
                if(defaultXMLParam != None) :
                  defaultXML = False
                  defaultXML = (str(paramList.getValueOrText(defaultXMLParam)) in self.TRUE_VALS)
                  
                if(defaultXML):
                    cmakeContents += "\n"
                    cmakeContents +=  "#     defaultXML : If "+ mainSource.split(".")[0]  + ".xml exists then copy to testing   \n"
                    cmakeContents +=  "#     directory and construct command line input \"-f "+ mainSource.split(".")[0]  + ".xml\"  \n"
                    cmakeContents += self.getFragment("DefaultXMLtestDataFrag.dat")
                    cmakeContents += "\n"
                else:      
                    ctestArgumentsParam = p.find("ctestArguments")
                    if(ctestArgumentsParam != None) : 
                      cmakeContents += "\n"
                      cmakeContents +=  "#     Specify command line arguments  \n"
                    
                      ctestArguments = paramList.getValueOrText(ctestArgumentsParam)  
                      cmakeContents += "\n"
                      cmakeContents += "      set (ctestArguments " + ctestArguments + " )\n"
                      cmakeContents += "\n"
                      cmakeContents +=  "#     Add target to test set \n"
                      cmakeContents += "\n"
                      cmakeContents += "      add_test(NAME  ${mainExecName} WORKING_DIRECTORY \"${CMAKE_SOURCE_DIR}/Testing/${mainExecName}\"\n"
                      cmakeContents += "      COMMAND \"${CMAKE_SOURCE_DIR}/${CMAKE_BUILD_TYPE}/${mainExecName}\" ${ctestArguments} )\n"
                    else:
                      cmakeContents +=  "\n#     Add target to test set \n"
                      cmakeContents += "\n"
                      cmakeContents += "      add_test(NAME  ${mainExecName} WORKING_DIRECTORY \"${CMAKE_SOURCE_DIR}/Testing/${mainExecName}\"\n"
                      cmakeContents += "      COMMAND \"${CMAKE_SOURCE_DIR}/${CMAKE_BUILD_TYPE}/${mainExecName}\")\n"
                      

            cmakeContents += "\n    endif()\n\n"
            cmakeContents +=  "#----------------------------------------------------------------#\n"
            cmakeContents += "\n"
    
    #
    #################################################################
    # Specify compiler properties applied to every target 
    #################################################################
    #
    
    cmakeContents +=  self.getFragment("CompileFeaturesFrag.dat")
    
    cmakeContents += "#\n"
    cmakeContents += "#  Additional compiler options (operating system dependent)  \n"
    cmakeContents += "#  Visual studio options if \"Windows\", Mac options if \"Darwin\"  \n"
    cmakeContents += "#\n"
    
    
    cmakeContents += "    set(ADDITIONAL_DEBUG_OPTIONS \"\")\n"
    cmakeContents += "    if(\"${CMAKE_SYSTEM_NAME}\" STREQUAL \"Linux\")\n"
    if(len(self.linuxDebugOptions) != 0):
       cmakeContents += "      set(ADDITIONAL_DEBUG_OPTIONS " + self.linuxDebugOptions + ")\n"
    else:
        cmakeContents += "#     set(ADDITIONAL_DEBUG_OPTIONS " + "\"-Wall\"" + ")\n"
    cmakeContents += "    elseif(\"${CMAKE_SYSTEM_NAME}\" STREQUAL \"Windows\")\n"
    if(len(self.visualStudioDebugOptions) != 0):
        cmakeContents += "      set(ADDITIONAL_DEBUG_OPTIONS " + self.visualStudioDebugOptions + ")\n"
    else:
        cmakeContents += "#     set(ADDITIONAL_DEBUG_OPTIONS " + "\"/Wall\"" + ")\n"
    
    cmakeContents += "    elseif(\"${CMAKE_SYSTEM_NAME}\" STREQUAL \"Darwin\")\n"
    if(len(self.macDebugOptions) != 0):
        cmakeContents += "      set(ADDITIONAL_DEBUG_OPTIONS " + self.macDebugOptions + ")\n"
    else:
        cmakeContents += "#     set(ADDITIONAL_DEBUG_OPTIONS " + "\"-Wall\"" + ")\n"
    cmakeContents += "    endif()\n"
    cmakeContents += "\n"
    
    cmakeContents += "    set(ADDITIONAL_RELEASE_OPTIONS \"\")\n"
    cmakeContents += "    if(\"${CMAKE_SYSTEM_NAME}\" STREQUAL \"Linux\")\n"
    if(len(self.linuxReleaseOptions) != 0):
       cmakeContents += "      set(ADDITIONAL_RELEASE_OPTIONS " + self.linuxReleaseOptions + ")\n"
    else:
        cmakeContents += "#    set(ADDITIONAL_RELEASE_OPTIONS " + "\"-Wall\"" + ")\n"
    cmakeContents += "    elseif(\"${CMAKE_SYSTEM_NAME}\" STREQUAL \"Windows\")\n"
    if(len(self.visualStudioReleaseOptions) != 0):
        cmakeContents += "      set(ADDITIONAL_RELEASE_OPTIONS " + self.visualStudioReleaseOptions + ")\n"
    else:
        cmakeContents += "#     set(ADDITIONAL_RELEASE_OPTIONS " + "\"/Wall\"" + ")\n"
    
    cmakeContents += "    elseif(\"${CMAKE_SYSTEM_NAME}\" STREQUAL \"Darwin\")\n"
    if(len(self.macReleaseOptions) != 0):
        cmakeContents += "      set(ADDITIONAL_RELEASE_OPTIONS " + self.macReleaseOptions + ")\n"
    else:
        cmakeContents += "#     set(ADDITIONAL_RELEASE_OPTIONS " + "\"-Wall\"" + ")\n"
    cmakeContents += "    endif()\n"
    cmakeContents += "\n"
    
    
    cmakeContents += "    target_compile_options(${mainExecName} PUBLIC \"$<$<CONFIG:DEBUG>:${ADDITIONAL_DEBUG_OPTIONS}>\")\n"
    cmakeContents += "    target_compile_options(${mainExecName} PUBLIC \"$<$<CONFIG:RELEASE>:${ADDITIONAL_RELEASE_OPTIONS}>\")\n"
    
    cmakeContents += "\n"
    cmakeContents += "endforeach()   # Loop over targets \n"
          
    if(self.verboseFlag): 
      print(cmakeContents)
    if(os.path.isfile("CMakeLists.txt") and (not self.forceOverwriteFlag)):
        yesOrNo = input("Overwrite existing CMakeLists.txt ? y)es n)o [n]  :  ")
        if(yesOrNo != "y"):
          exit(0)       
      
    f = open("CMakeLists.txt", 'w')
    f.write(cmakeContents)
    f.close()
    print("File created : CMakeLists.txt")
    
  
  
#
#=========== Local utility routines  ============================
#   

# Returns the location of the python program that was invoked 

  def get_script_path(self):
    return os.path.dirname(os.path.realpath(sys.argv[0]))
   
  def createFileLinesArray(fileName):
    dataFile  = Path(fileName)
    try :
      f = open(dataFile,'r')
    except OSError as err:
      print (' === Error ===')
      print (" Data file cannot be read")
      print (err)
      exit()
      
    fileContents =  f.read()
    f.close()

    fileLines = fileContents.split("\n");
    return fileLines


  def getFragment(self,fileName):
    dataFile  = Path(self.CMakeCreatorDataDir + "/" + fileName)
    try :
      f = open(dataFile,'r')
    except OSError as err:
      print (' === Error ===')
      print (" Data file cannot be read")
      print (err)
      exit()
      
    fileContents =  f.read()
    f.close()

    return fileContents
  
  def createFragment(self,templateFragmentFile,fragmentData):
    dataFile  = Path(self.CMakeCreatorDataDir + "/" + templateFragmentFile)
    try :
      f = open(dataFile,'r')
    except IOError as exception:
        print('                 === Error ===')
        print(" Template file cannot be read") 
        print(exception)
        exit()
      
    fragmentContents =  f.read()
    f.close()
#
# Check to make sure all of the parameters that are to be
# substituted have template entries
#
    fragmentKeys = list(fragmentData.keys())
    for i in range(len(fragmentData)):
      findString = '$' + fragmentKeys[i]
      findString = findString.strip()
      if(fragmentContents.find(findString) == -1): 
            print('                 === Error ===')
            print(' Template variable \'' + findString +\
                '\' is not in the template fragment file')
            print(' ' + templateFragmentFile)
            exit()
#
# Substitute in the parameters
#
    r  = Template(fragmentContents)
    try:
      fragmentFile = r.substitute(fragmentData)
      return fragmentFile
    except KeyError as exception:
     print('                 === Error ===')
     print('A parameter in: ' + rtemplateFragmentFile)
     print('has not been specified.\n')
     print('The parameter that needs to be specified :')
     print('[',exception, ']')
     exit()
     
     
  TRUE_VALS  = ( '1', 'true',  'True', 'TRUE',  'y', 'yes', 'Y', 'Yes', 'YES','ON','on','On')
  FALSE_VALS = ( '0', 'false', 'False', 'FALSE','n', 'no',  'N', 'No',   'NO','OFF','off','Off')
#   
#
#   Stub for executing the class defined in this file 
#   
if __name__ == '__main__':
  cMakeCreator = CMakeCreator()
  cMakeCreator.run()
  
  
