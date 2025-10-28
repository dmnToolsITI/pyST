#### pyST

pyST is a translator of a program written the the Structured Text (ST) language into a python program that tries to emulate its functional behavior.   The sole purpose of this translator is to create a tool for students to use when integrating logic expressed in ST (e.g. for a PLC controller) to create a form that is more amenable to integration with other software, and interactive debugging. In its present state pyST is very rudimentary, both in its approach to translation and in the subset of ST that is actually recognized.

This repository also contains what is needed to build and run a Docker container for an application that checks the syntax of ST programs.   The executable that performs the heavy lifting for this task was obtained from https://github.com/jubnzv/iec-checker and we are very grateful for the effort that went into this and the pre-built Linux application that performs the check.

This repository contains

- pyST.py
- iec_checker_Linux_x86_64 , the Linux executable that performs the ST syntax checking
- Dockerfile , used to build a container that runs the executable
- run_iec_check.sh , a shell script that calls Docker with the right flags for performing the analysis
- scada.st , a copy of an ST file found in the Shocklab distribution, for use in testing run_iec_check.sh and pyST.py



```
% docker build -t iecc .
% ./run_iec_check.sh scada.st
./run_iec_check.sh scada.st
0:0 PLCOPEN-CP9: Code is too complex (44 statements)
26:12 PLCOPEN-CP4: Address of direct variable %WI6 (size 2) should not overlap with direct variable %WI5
25:11 PLCOPEN-CP4: Address of direct variable %WI5 (size 2) should not overlap with direct variable %WI6
24:17 PLCOPEN-CP4: Address of direct variable %WI4 (size 2) should not overlap with direct variable %WI5
23:16 PLCOPEN-CP4: Address of direct variable %WI3 (size 2) should not overlap with direct variable %WI4
22:16 PLCOPEN-CP4: Address of direct variable %WI2 (size 2) should not overlap with direct variable %WI3
21:15 PLCOPEN-CP4: Address of direct variable %WI1 (size 2) should not overlap with direct variable %WI2
17:18 PLCOPEN-CP4: Address of direct variable %WI22 (size 2) should not overlap with direct variable %WI21
16:14 PLCOPEN-CP4: Address of direct variable %WI21 (size 2) should not overlap with direct variable %WI22
15:19 PLCOPEN-CP4: Address of direct variable %WI20 (size 2) should not overlap with direct variable %WI21
14:18 PLCOPEN-CP4: Address of direct variable %WQ20 (size 2) should not overlap with direct variable %WI21
8:18 PLCOPEN-CP4: Address of direct variable %WI12 (size 2) should not overlap with direct variable %WI11
7:14 PLCOPEN-CP4: Address of direct variable %WI11 (size 2) should not overlap with direct variable %WI12
6:19 PLCOPEN-CP4: Address of direct variable %WI10 (size 2) should not overlap with direct variable %WI11
5:18 PLCOPEN-CP4: Address of direct variable %WQ10 (size 2) should not overlap with direct variable %WI11

% python pyST.py -st scada.st -mpc 500
%
```

The warnings produced by running the ST syntax check apparently come from perceived misalignment of the memory addresses of variables declared in scada.st .   The code complexity warning is just that, a warning.
