# MIPS Simulator
The purpose of this project is to take MIPS code and simulate it's output. This is done in 2 stages, first the mips code is converted to it's binary representation using `assembler.py` this is then simuated through both a pipeline dand non pipelined processor in `processor_non_pipelined.py` and `processor_pipelined.py` respectively.

## Assembler
The code here reads the MIPS intructions and splits it into the various types. Based on that it converts it to the binary code and prints the output in both binary and hexadecimal form.

## Processor
Both pipelined and non-pipelined are simulated through a typical 5 stage processor. Pipelined allows various processes to run at the same time in different phases leading to much faster output. Number of cycles is calculated for both and is printed to facilate comparisons.

## How to run
To assemble the code:
```
python3 assembler.py
``` 
then follow the command line prompts to enter a file for assembling. The binary and hex code is then printed out. This can be put into files for further processing.

Processors are run by 
```bash
python3 processor_non_pipelined.py
python3 processor_pipelined.py
```
These by default run a factorial code and a sorting code and a given binary code can be simulated after.