## CMakeCreator 

A Python program for creating CMakeLists.txt build files. The input to the program is an XML data file specifying the information required to set up a project containing multiple targets (a.k.a executables). 

The purpose of the CMakeCreator program is to accept "generic" information necessasry to build a target and translate that information into CMake specific constructs. Decisions about what generic input should be accepted and the form of the resulting CMakeLists.txt file were based upon abstracting from the CMakeLists.txt files that were manually constructed for projects associated with the development of software components for CQSE simulation codes. 

A sample input XML file with annotations can be obtained by specifying the input option "-s" to the program. The file CMakeCreatorSample.xml will then be copied to the directory in which the program is invoked. After one is familiar with the structure of the input file, one can obtain a sample input file without annotations by specifyig an input option "-b" ("b" for brief). 

### Notes

If installed on ones system, the third party external dependencies that are supported are 

Lapack, MKL Lapack, FFTW3, MKL FFTW3, OpenMP, SQlite3, and valgrind.

In order for cmake to find these dependencies and create appropriate makefile entries, additional environment variables may need to be set. Typically additions to the PATH variable are required that specify the locations of the header files and libraries. If the MKL libraries are used, then on Linux and Windows machines, the environment variable MKLROOT must be set to the root of the MKL installation directory. If the environment variables are not set properly the execution of the cmake program will report errors in the construction of the makefiles required to build the target. The use of external shared object libraries may also require the appropriate setting of the LD_LIBRARY_PATH environment variables. 


### Prerequisites

Python 3

### Versioning

Release : 1.0.1

### Authors

Chris Anderson

### License

GPLv3  For a copy of the GNU General Public License see <http://www.gnu.org/licenses/>.

 



