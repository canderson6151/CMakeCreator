# 
#  CMakeLists.txt
#
#  Generator      : CMakeCreator 
#  XML data file  : $XML_InputFile
#  Date           : $Date
#

cmake_minimum_required (VERSION $required_cmake)
project ($project)
message(STATUS "System Name $${CMAKE_SYSTEM_NAME}")

# Loads helper to print messages
 
include(CMakePrintHelpers)

# Suppresses the creation of the install script 

set(CMAKE_SKIP_INSTALL_RULES True) 

# Setup for debug and release targets 

ADD_CUSTOM_TARGET(debug
  COMMAND $${CMAKE_COMMAND} -DCMAKE_BUILD_TYPE=Debug $${CMAKE_SOURCE_DIR}
  COMMAND $${CMAKE_COMMAND} --build $${CMAKE_BINARY_DIR} --target all
  COMMENT "Creating the executable in the debug mode.")

ADD_CUSTOM_TARGET(release
  COMMAND $${CMAKE_COMMAND} -DCMAKE_BUILD_TYPE=Release $${CMAKE_SOURCE_DIR}
  COMMAND $${CMAKE_COMMAND} --build $${CMAKE_BINARY_DIR} --target all
  COMMENT "Creating the executable in the release mode.") 

