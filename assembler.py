functions = {"syscall": ["000000", "r", ""], "jal": ["000011", "j", "1"], "sw": ["101011", "i", "231"],
             "add": ["000000", "r", "312"], "addi": ["001000", "i", "213"], "move": ["000000", "r", "312"],
             "mul": ["011100", "i", "312"], "lw": ["100011", "i", "231"], "beq": ["000100", "i", "123"],
             "j": ["000010", "j", "1"], "slt": ["000000", "r", "312"], "li": ["001001", "i", "213"],
             "jr": ["000000", "r", "1"], "bne": ["000101", "i", "123"]}

# The above dictionary is to contain all the functions that are being used in the program, along with their type, their
# opcode and the order of the parameters of rs, rt and rd/imm


r_functions = {"syscall": "001100", "add": "100000", "jr": "001000", "slt": "101010", "move": "100001"}

# The above dictionary is used to store all the R-type instructions along with their respective "function" field values

registers = ["$0", "$at", "$v0", "$v1", "$a0", "$a1", "$a2", "$a3", "$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6",
             "$t7", "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7", "$t8", "$t9", "$k0", "$k1", "$gp", "$sp",
             "$fp", "$ra"]

# The above dictionary contains all the possible registers that can be used in the program, and their index represents
# their value, for example, $at = 1.


def twoscomplement(num):    # Function to return the 2's complement of a binary number
    t = (2**16-1) ^ num
    b = bin(t)[2:]
    n = int(b, 2)+1
    return bin(n)[2:]


def type_r(code_line):      # Function to handle/generate the machine level code for all R-type instructions

    par_array = [None, None, None, None]    # Array to take the line of code and store the operation, source and destination registers
    for i in range(len(code_line)):
        par_array[i] = code_line[i]

    instruct, arg1, arg2, arg3 = par_array     # Unwrapping the array to store the data in individual variables

    funct = r_functions[instruct]           # To obtain the value of the "function" field for the R-type instruction
    if funct == "100001":                  # if statement to handle "move" instruction since it is essentially "addu"
        arg2, arg3 = "$0", arg2
    info = functions[instruct]              # Store the list value of the corresponding operation from the "functions" dictionary
    op_code = "000000"

    if funct == "000000" or funct == "000010" or funct == "000011":  # To check if the operation is either sll, srl, sra
        shamt = str(arg3)                                           # To set the value of "shift amount"
        shamt = "0"*(5-len(shamt)) + shamt                          # Converting "shamt" into a 5-bit binary number
    else:
        shamt = "00000"                                             # Else setting shamt to 0
    temp = [arg1, arg2, arg3]
    args = ["$0", "$0", "$0"]                                       # Storing argument registers in array
    for ele in range(len(info[2])):
        args[int(info[2][ele])-1] = temp[ele]
    m_code = op_code                                                # Adding the opcode to the machine level code
    for i in range(len(args)):
        args[i] = registers.index(args[i])                          # Converting the register numbers to 5-bit binary
        b = bin(args[i])[2:]
        b = "0"*(5-len(b)) + b
        m_code = m_code + b                                         # Adding register binary numbers to the machine code
    m_code = m_code + shamt                                         # Adding shamt to machine code
    m_code = m_code + funct                                         # Adding function field value to machine code
    return m_code


def type_i(code_line):  # Functions which deals with I-type instructions and returns their machine level binary equival.

    par_array = [None, None, None, None]    # Array to store all parameters of the instruction.
    for i in range(len(code_line)):
        par_array[i] = code_line[i]

    instruct, arg1, arg2, arg3 = par_array  # Unwrapping of the parameters into an array

    info = functions[instruct]  # To store the opcode, the type of instruction and the order of parameters in an array
    op_code = info[0]           # To store the opcode of the operation
    if instruct == "li":        # if statement to handle "li" operation
        arg2, arg3 = "$0", arg2
    temp = [arg1, arg2, arg3]   # To store all the register arguments into variables
    args = ["$0", "$0", 0]  # To set initial default values to 0
    for ele in range(len(info[2])):
        args[int(info[2][ele])-1] = temp[ele]
    args[0] = bin(registers.index(args[0]))[2:]  # Two statements to retrieve the binary representation of the register
    args[0] = "0"*(5-len(args[0])) + args[0]     # and convert it into a 5-bit binary number
    args[1] = bin(registers.index(args[1]))[2:]
    args[1] = "0"*(5-len(args[1])) + args[1]     # Same thing with the second register
    if instruct == "mul":   # if statement to handle the "mul" operation, since it is essentially a "mulu" operation
        args[2] = bin(registers.index(args[2]))[2:]
        args[2] = "0"*(5-len(args[2])) + args[2] + "00000000010"
    else:
        args[2] = int(args[2])
        if args[2]<0:
            args[2] = twoscomplement(-args[2])
        else:
            args[2] = bin(args[2])[2:]
        args[2] = "0"*(16-len(args[2])) + args[2]
    m_code = op_code+args[0]+args[1]+args[2]
    return m_code


def type_j(code_line):  # Function which deals with J-type instructions and returns their machine level language

    par_array = [None,None]
    for i in range(len(code_line)):
        par_array[i] = code_line[i]

    instruct, arg1 = par_array

    info = functions[instruct]
    op_code = info[0]   # Storing opcode of the instruction.
    arg1 = arg1[4:-2]   # Trimming the first 4 and last 2 bits, since for a J-type instruction, they are always 0.
    m_code = op_code + arg1
    return m_code


def get_data(code):   # To get data on the ".asciiz" strings and their lengths, which are to be printed during execution
    if(code.find(".data") == -1):   # If there is no ".data" block in the code, return an empty dictionary
        return dict()
    code = code.split('.text')[0]
    code = code.split('.data')[1]
    code = code.split("\t")     # Getting each label under ".data" by splitting it on the basis of "\t".
    curr = 0    # Variable to keep track of how many characters have been printed up until now
    data = dict()   # Dictionary to store all the different labels as its key, and its value is the length of the string it is supposed to print
    for line in code:
        if line[-1] == "\n":
            line = line[:-1]
        if line != "":
            line = line.replace(" .asciiz ", "")
            line = line.split(":", 1)
            line.append(len(line[1])-2)
            data[line[0]] = curr
            curr += line[2]+1
    return data


def get_machine_code(code):
    data = get_data(code) #getting length of .data for usage in la
    code = code.split("\n")     # Splitting on the basis of \n to get all the lines of assemble code
    computed_code = []
    flag = 0                    # Flag variable to ensure we only get instructions from the ".text" block and not the
    if(".text" not in code):
        flag = 1
    print(code, "CODE")
    for i in code:              # ".data" block
        i = i.split("#")[0]     # Removing inline comments
        i = i.strip()           # Getting rid of any trailing spaces at the beginning or end of each line of code
        i = i.strip("\t")       # Getting rid of any trailing tab spaces at the beginning or end of each line of code
        if i == ".text":        # Once we find ".text" block, we start adding lines of code to the "computed_code" array
            flag = 1
            continue
        if i == '' or i[0] == "#" or flag == 0:     # To not read any line of code which is either a comment or empty
            continue
        i = i.replace(" ","")       # Replacing all spaces with empty characters in every line of code
        i = i.replace("$",",$",1)   # Replacing the first occurrence of "$" with ",$" (for splitting purpose later)
        i = i.replace("(",",")      # Replacing "(" with "," (for splitting purpose later)
        i = i.replace(")","")       # Replacing ")" with a null character to get rid of unnecessary closing bracket
        i = i.replace(":",":,")     # Replacing ":" (as in loop:) with ":," for splitting purposes later
        i = i.replace("$zero","$0") # For uniformity
        i = i.split(",")            # Splitting each line of code on the basis of "," to get the operation, list of
        computed_code.append(i)     # parameters and then append it to the array "computed_code", ready for assembling.

    m_code = []                     # Array to store the machine level binary code after assembling
    labels = dict()                 # Dictionary to contain the respective line addresses of the different labels
    i = 0                           # Variable to keep track of line numbers.
    for line_no in range(len(computed_code)):   # Iterating through each line of the code
        line = computed_code[line_no]           # Retrieving each line of code
        if ":" in line[0]:                      # Checking if the line of code is a label or not
            labels[line[0][:-1]] = i
            line.pop(0)
            computed_code[line_no] = line
        elif line[0] == "la":
            i += 1
        i += 1

    for line_no in range(len(computed_code)):
        line = computed_code[line_no]
        if "jal" == line[0][:3] or ("j" == line[0][0] and "r" != line[0][1]):  # To check if the statement is jal or j
            if "jal" == line[0][:3]:
                line = ["jal",line[0][3:]]
            else:
                line = ["j",line[0][1:]]
            computed_code[line_no] = line
    i = 0
    print(computed_code,"COMPUTED CODE")
    for line in computed_code:
        if line[0] == "la":  # if statement to check is statement is "la" because la is made up of 2 instructions, lui and ori
            lui = "00111100000000010001000000000001"  # binary representation of lui $1, 0x00001001 this is constant
            # for all la calls
            ori = "001101" #op_code
            reg = bin(registers.index(line[1]))[2:]
            reg = "0"*(5-len(reg))+reg
            num = data[line[2]]
            num = bin(num)[2:]
            num = num.rjust(16, "0")
            ori = ori+"00001"+reg+num
            m_code.append(lui)          # Append the binary equivalent of the "lui" instructions to the machine code
            m_code.append(ori)          # Append the binary equivalent of the "ori" instructions to the machine code
            i += 2    # to account for extra instruction
            continue

        if line[0] == "beq" or line[0] == "bne":    # To count the number of instructions between the "beq" and "bne" statements and the target instruction
            line[3] = labels[line[3]]-i-1
        init_adress = 4194304   # To store the address of the first line of the assembly code
        if line[0] == "jal" or line[0] == "j":
            address = labels[line[1]]*4 + init_adress
            line[1] = bin(address)[2:]
            line[1] = '0'*(32-len(line[1])) + line[1]
        i += 1

        info = functions[line[0]]
        type = info[1]
        print(type, "HWLLO")
        if type == "r":                 # Multiple if statements to check which type of instruction is to be executed.
            m_code.append(type_r(line))
        if type == "i":
            m_code.append(type_i(line))
        if type == "j":
            m_code.append(type_j(line))

        # print(m_code[-1], hex(int(m_code[-1], 2)))

    print("Machine code in Binary format: ")
    for i in m_code:    # Loop to print all the binary machine level code in binary format
        print(i)

    print("Machine code in Hexadecimal format: ")
    for i in m_code:       # Loop to print all the instructions in hexadecimal format
        h = hex(int(i, 2))
        h = "0"*(10-len(h)) + h[2:]
        print(h)

   
fname = input("Enter the name of the file containing the MIPS code: ")  # Taking the name of the file containing the MIPS code
with open(fname, 'r') as f:  # Open the file containing the MIPS code
    code = f.read()                 # Read the contents of the file

get_machine_code(code)      # Main function to send the MIPS code and get in return the machine level code.
