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
