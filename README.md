# CASCADE

Computer Aided Side Channel Analysis Design Environment (CASCADE)
is a set of Python scripts and C binaries designed for automated and efficient 
SCA evaluations at design time. It is aimed at standard-cell based ASIC 
design flow and it revolves around several commercial EDA tools.

CASCADE consists of the Python 3.x.x compatible core and the following modules:
1. Handlers   - Wrappers for commercial EDA tools and some custom tools
2. Generators - Automatic generation of e.g. test vectors
3. Analyzers  - C binaries for efficient parsing and processing 

CASCADE is easily extensible to handle any other EDA tool, other than the ones
supported by this snapshot of our framework. Generators and analyzers work with
standardized formats such as VCD, SDF, etc. to ensure interoperability and 
easy addaptation. When needed they output custom binary formats aimed at SCA
evaluations. 

# DISCLAIMER 
We use all EDA tools under appriate licensing of KU Leuven, and 
therefore can not distribute these tools nor licences in any manner.

# WARNING 
All code is of experimental quality. It is provided as is, without any
guaranties, and is subject to change without notice.

# Starting
Command line arguments of src/cascade.py contain help pages for each instruction.
All the interaction with the tools should be done by invoking this file.

# First steps
1. Clone the repository on your machine.
2. Run the setup.sh script, it basically checks whether you have Python 3 and 
    alias cas="python .../CASCADE/src/cascade.py".
    ./setup.sh --global adds this to the .bashrc
3. Run cas -h to test whether everything is ok
4. Create *.json files for a library you want to use. 
Example is given at CASCADE/doc/example/nan45.json
5. Manage libraries using cas {add_lib | remove_lib | list_lib}, this data is 
    stored in CASCADE/data/libraries.json.
    Example of library configuration file is in CASCADE/data/nan45.json.
6. Default parameter sets are in CASCADE/data/default.json. 
    Feel free to add new ones as per your need, but know that changing the existing 
    ones will lead to misbehaviour of handlers that use them. 
    Of course, you may change the parameter values freely.
7. Navigate to the work directory and run cas init <designName>.
    This will create a src directory, a .cascade (hidden file) and a config file
    <designName>.json, which is the copy of CASCADE/data/default.json
9. Set parameters of your design and start implementing it. Common ones are:
    - ${design:clk},
    - ${design:rst}, ${design:rst_level},
    - ${design:nclk}, ${design:nshares},
    - ${design:sources},
    - ${lib_id},
    - ${test:id}, ${test:target},
    ...


