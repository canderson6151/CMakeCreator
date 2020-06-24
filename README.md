## CMakeCreator and CMakeRunner

**CMakeCreator** is a Python program for creating CMakeLists.txt build files. The input to the program is an XML data file specifying the information required to set up a project containing multiple targets (a.k.a executables) and data for the execution of target test cases invoked with ctest. 

The purpose of the CMakeCreator program is to accept "generic" information necessary to build a target and translate that information into CMake specific constructs. Decisions about what generic input should be accepted and the form of the resulting CMakeLists.txt file were based upon abstracting from the CMakeLists.txt files manually created for projects organized in a manner similar to the standard Workspace/Projects or Solution/Projects structure employed by the Eclipse IDE or the Visual Studio IDE.    

A sample input XML file with annotations can be obtained by specifying the input option "-s" to the program. The file CMakeCreatorSample.xml will then be copied to the directory in which the program is invoked. After one is familiar with the structure of the input file, one can obtain a sample input file without annotations by specifying an input option "-b" ("b" for brief). 

**CMakeRunner** is a python program that invokes the ordered execution of CMakeList.txt files contained within subdirectories of the directory in which the program is run or a specified working directory. It is assumed that the CMakeFiles were created using the CMakeCreator.py program so that targets "release" and "debug" defined. No installation commands are executed. A sample input XML file with annotations can be obtained by specifying the input option "-s" to the program. 


### Notes

If installed on ones system, the third party external dependencies that are supported are 

Lapack, MKL Lapack, FFTW3, MKL FFTW3, OpenMP, SQlite3, and valgrind.

In order for cmake to find these dependencies and create appropriate makefile entries, additional environment variables may need to be set. Typically additions to the PATH variable are required that specify the locations of the header files and libraries. If the MKL libraries are used, then on Linux and Windows machines, the environment variable MKLROOT must be set to the root of the MKL installation directory. If the environment variables are not set properly the execution of the cmake program will report errors in the construction of the makefiles required to build the target. The use of external shared object libraries may also require the appropriate setting of the LD_LIBRARY_PATH environment variables. 

When specifying <Library>s the order is important, as the order is replicated in the link command invoked. If library libA requires linking to routines in libB, then libA needs to be specified before libB.  

### Prerequisites

Python 3

### Versioning

Release : 1.0.3

### Date

June 24, 2020 

### Authors

Chris Anderson

### License

GPLv3  For a copy of the GNU General Public License see <http://www.gnu.org/licenses/>.

 



