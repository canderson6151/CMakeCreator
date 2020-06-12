## CMakeCreator 

A Python program for creating CMakeLists.txt build files. The input to the program is an XML data file specifying the information required to set up a project containing multiple targets (a.k.a executables). 

The purpose of the CMakeCreator program is to accept "generic" information necessasry to build a target and translate that information into CMake specific constructs. Decisions about what generic input should be accepted and the form of the resulting CMakeLists.txt file were based upon abstracting from the CMakeLists.txt files that were manually constructed for projects associated with the development of software components for CQSE simulation codes. 

A sample input XML file with annotations can be obtained by specifying the input option "-s" to the program. The file CMakeCreatorSample.xml will then be copied to the directory in which the program is invoked. After one is familiar with the structure of the input file, one can obtain a sample input file without annotations by specifyig an input option "-b" ("b" for brief). 



### Prerequisites

Python 3

### Versioning

Release : 1.0.1

### Authors

Chris Anderson

### License

GPLv3  For a copy of the GNU General Public License see <http://www.gnu.org/licenses/>.

 



