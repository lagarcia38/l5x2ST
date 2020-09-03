
# L5X-to-ST Compiler for SCADMAN
This project builds upon the L5X parser for Allen Bradley L5X project files. This tool takes an L5X project file and generates a large Structured Text code that represents the control logic of the entire project. This consolidated representation was necessary for implementing the [Scadman](https://arxiv.org/pdf/1812.08310.pdf) tool. By normalizing an entire project into a single, structured text file, it enabled us to generate a giant software control-flow graph for cyber-physical analysis. You can feed the structured text into any number of available structured text compilers, e.g., [MATIEC](https://github.com/nucleron/matiec), for further analysis. Feel free to contact me for more details.

# USAGE

usage: l5x2ST.py [-h] [-o ST output file]
                 (-i L5X connectivity file | -d L5X Directory)

Produces consolidated ST File.

optional arguments:
  -h, --help            show this help message and exit
  -o ST output file
  -i L5X connectivity file
  -d L5X Directory

# Current Status:
* The code works for multiple PLCs, but does not support modules just yet. PLCs simply forward values to the modules, so I simply implemented a mechanism that comments out any references to modules. 

* The latest fix eliminated messages between PLCs and replaced them with direct writes to the associated PLC variables. I also noticed that structs and functions with the same names differ from PLC to PLC. As such, I had to implement a renaming for all the system variables. 

* The latest fix also fixed the wiring for all the FBDs. Before, I was simply initializing them with the given initial data. However, this is extremely flawed as the lack of wiring eliminates the connectivity of the main program to the FBDs, so no variables would have been updated

# Main TODOs/Issues
* Implement support for Module structs (right now we just comment them out)
* There are several minor TODOs enumerated at the top of the python script for sprucing up the code and organizing it a bit
* In the current state, the compilation of the five PLCs results in 2 very minor errors. This is due to a bug in the type checking mechanism. Allen Bradley allows integers to be directly assigned to reals, while MATIEC doesn't. I have a buggy implementation for this type-mismatch fixing, but for the time being it is easier to go to those 2 lines and change "7" to "7.0" :)

# Dependencies
* Python3
* [L5X](https://pypi.org/project/l5x/)