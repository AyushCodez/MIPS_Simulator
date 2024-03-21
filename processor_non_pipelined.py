
registers = {"$0" : 0, "$at" : 0, "$v0" : 0, "$v1" : 0, "$a0" : 0, "$a1": 0, "$a2" : 0, "$a3" : 0, "$t0" : 0, "$t1" : 0, "$t2" : 0, "$t3" : 0, "$t4" : 0, "$t5" : 0, "$t6" : 0,
             "$t7" : 0, "$s0" : 0, "$s1" : 0, "$s2" : 0, "$s3": 0, "$s4": 0, "$s5": 0, "$s6": 0, "$s7": 0, "$t8": 0, "$t9": 0, "$k0": 0, "$k1": 0, "$gp": 0x10008000, "$sp": 0x7fffeffc,
             "$fp": 0, "$ra": 0}

registersList = ["$0", "$at", "$v0", "$v1", "$a0", "$a1", "$a2", "$a3", "$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6",
             "$t7", "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7", "$t8", "$t9", "$k0", "$k1", "$gp", "$sp",
             "$fp", "$ra"]

def IF(instructions,pc):
    return instructions[pc] #full instruction

def ID(instruction):
    opcode = instruction[0:6]
    control_unit(opcode)
    values = registerFile(instruction)
    if(instruction[16] == "1"):
        imm = -twoscomplement(int(instruction[16:],2))
    else:
        imm = int(instruction[16:],2)
    return imm, int(instruction[26:],2), values[0], values[1] #imm,funct_field,rd1,rd2,write_reg

def EX(rd1,rd2,imm,funct_field,signals):
    ALUres = ALU(signals["ALUOp"],signals["ALUSrc"],imm,funct_field,rd1,rd2)
    return ALUres

def Mem(instuction,ALURes,rd2,pc,imm,signals):
    rd = DataMemory(address=ALURes,write_data=rd2,mem_read=signals["MemRead"],mem_write=signals["MemWrite"])
    pc_next = PC_Update(currentLocation=pc,isZero=int(ALURes == 0),
                        branch=imm,branch_signal=signals["Branch"],
                        jump = signals["JMP"],jumpLocation=int(instuction[6:],2)*4) #left shifting location by 2
    return [ALURes,rd][signals["MemtoReg"]],pc_next #write_data,pc_next
    
def WB(instruction,write_data,signals):
    registerFile(instruction=instruction,regWrite=signals["RegWrite"],
                 regDst=signals["RegDst"],writeData=write_data) #writing data if required
    

    
    
def generateInstructions(machineCode, startMemory = "0x400000"):
    instructions = dict()
    insts = machineCode.split("\n")
    for i in range(len(insts)):
        if(insts[i].strip() == ''):
            continue
        instructions[startMemory] = insts[i]
        temp = int(startMemory, 16)
        temp += 4
        startMemory = hex(temp)
    return instructions


def control_unit(op_code):
    signals = dict()
    if(op_code == 0): #R Type
        signals["RegDst"] = 1
        signals["ALUSrc"] = 0
        signals["MemtoReg"] = 0
        signals["RegWrite"] = 1
        signals["MemRead"] = 0
        signals["MemWrite"] = 0
        signals["Branch"] = 0
        signals["ALUOp"] = 2
        signals["JMP"] = 0
    if(op_code == 35): #LW
        signals["RegDst"] = 0
        signals["ALUSrc"] = 1
        signals["MemtoReg"] = 1
        signals["RegWrite"] = 1
        signals["MemRead"] = 1
        signals["MemWrite"] = 0
        signals["Branch"] = 0
        signals["ALUOp"] = 0
        signals["JMP"] = 0
    if(op_code == 43): #SW
        signals["RegDst"] = 1
        signals["ALUSrc"] = 1
        signals["MemtoReg"] = 0
        signals["RegWrite"] = 0
        signals["MemRead"] = 0
        signals["MemWrite"] = 1
        signals["Branch"] = 0
        signals["ALUOp"] = 0
        signals["JMP"] = 0
    if(op_code == 4): #BEQ
        signals["RegDst"] = 0
        signals["ALUSrc"] = 0
        signals["MemtoReg"] = 0
        signals["RegWrite"] = 0
        signals["MemRead"] = 0
        signals["MemWrite"] = 0
        signals["Branch"] = 1
        signals["ALUOp"] = 1
        signals["JMP"] = 0
    if(op_code == 2): #JMP
        signals["RegDst"] = 0
        signals["ALUSrc"] = 0
        signals["MemtoReg"] = 0
        signals["RegWrite"] = 0
        signals["MemRead"] = 0
        signals["MemWrite"] = 0
        signals["Branch"] = 0
        signals["ALUOp"] = 0
        signals["JMP"] = 1
    if(op_code == 8): #ADDI
        signals["RegDst"] = 0
        signals["ALUSrc"] = 1
        signals["MemtoReg"] = 0
        signals["RegWrite"] = 1
        signals["MemRead"] = 0
        signals["MemWrite"] = 0
        signals["Branch"] = 0
        signals["ALUOp"] = 0
        signals["JMP"] = 0

    return signals

def ALUControl(aluOP, functField):
    if(aluOP == 0):
        return 2
    elif(aluOP == 1):
        return 6
    elif(aluOP == 2):
        if(functField == 32):
            return 2
        elif(functField == 34):
            return 6
        elif(functField == 36):
            return 0
        elif(functField == 37):
            return 1
        elif(functField == 42):
            return 7


def registerFile(instruction, regWrite = 0, regDst = 0, writeData = 0):
    register1 = int(instruction[6:11], 2)
    register2 = int(instruction[11:16], 2)
    reg1, reg2 = registersList[register1], registersList[register2]
    if(regWrite == 1):
        if(regDst == 0):
            registers[reg2] = writeData
        else:
            registers[registersList[int(instruction[16:21], 2)]] = writeData
    return [registers[reg1], registers[reg2]]
    

def PC_Update(currentLocation, isZero = 0, branch = 0,branch_signal = 0, jump = 0, jumpLocation = 0):
    actualNext = 0
    branch += 1
    if(isZero == 1 and branch_signal == 1): 
        actualNext = hex(int(currentLocation, 16) + branch*4) 
    else:
        actualNext = hex(int(currentLocation, 16) + 4)
    if(jump == 1):
        actualNext = hex(jumpLocation) 
    return actualNext


def ALU(ALUOp,ALUSrc,imm,funct_field,rd1,rd2):
    ALU_cont = ALUControl(ALUOp,funct_field)
    inp1 = rd1
    inp2 = [rd2,imm][ALUSrc]
    #print(inp1,inp2,"HELLO")
    if(ALU_cont == 2): #add
        ALU_res = inp1+inp2
    if(ALU_cont == 6): #sub
        ALU_res = inp1-inp2
    if(ALU_cont == 0): #and
        ALU_res = inp1 & inp2
    if(ALU_cont == 1):#or
        ALU_res = inp1 | inp2
    if(ALU_cont == 7):#SLT
        ALU_res = int(inp1 < inp2)
    return ALU_res

def DataMemory(address,mem_write = 0,mem_read = 0, write_data = 0):
    if mem_write == 1:
        memory[address] = write_data
    if mem_read == 1:
        if(address not in memory):
            return 0
        return memory[address]
    

def twoscomplement(num):    # Function to return the 2's complement of a binary number
    t = (2**16-1) ^ num
    return t+1

def run(instructions):
    instructions = generateInstructions(instructions)
    PC = "0x400000"
    clock_cycles = 0
    while(PC in instructions.keys()):
        clock_cycles+=1
        instruction = IF(instructions,PC)
        #print(instruction)
        signals = control_unit(int(instruction[:6],2))
        #print(signals)
        imm,funct_field,rd1,rd2 = ID(instruction)
        ALURes = EX(rd1,rd2,imm,funct_field,signals)
        write_data,pc_next = Mem(instruction,ALURes,rd2,PC,imm,signals)
        WB(instruction,write_data,signals)


        #print(imm,funct_field,rd1,rd2,ALURes,pc_next)
        
        PC = pc_next
    
    print("Clock cycles taken:",clock_cycles)
    print("Registers:")
    for reg in registers:
        print(f"{reg}: {registers[reg]}")
    print("Memory:")
    print(memory)

def main():
    global memory,registers
    memory = {}
    n = 6
    print(f"Calculating {n+4}! and storing in $s2:")
    registers['$s4'] = n
    with open("mcode1.txt",'r') as f:
        instructions = f.read()
    run(instructions)
    memory = {268468224:3,268468228:1,268468232:5,268468236:4,268468240:2}
    registers = {"$0" : 0, "$at" : 0, "$v0" : 0, "$v1" : 0, "$a0" : 0, "$a1": 0, "$a2" : 0, "$a3" : 0, "$t0" : 0, "$t1" : 0, "$t2" : 0, "$t3" : 0, "$t4" : 0, "$t5" : 0, "$t6" : 0,
             "$t7" : 0, "$s0" : 0, "$s1" : 0, "$s2" : 0, "$s3": 0, "$s4": 0, "$s5": 0, "$s6": 0, "$s7": 0, "$t8": 0, "$t9": 0, "$k0": 0, "$k1": 0, "$gp": 0x10008000, "$sp": 0x7fffeffc,
             "$fp": 0, "$ra": 0}
    print("\nSorting numbers and storing in memory:")
    with open("mcode2.txt",'r') as f:
        instructions = f.read()
    run(instructions)


    fname = input("Enter the filename to read machine code from:")
    with open(fname,'r') as f:
        instructions = f.read()

    registers = {"$0" : 0, "$at" : 0, "$v0" : 0, "$v1" : 0, "$a0" : 0, "$a1": 0, "$a2" : 0, "$a3" : 0, "$t0" : 0, "$t1" : 0, "$t2" : 0, "$t3" : 0, "$t4" : 0, "$t5" : 0, "$t6" : 0,
             "$t7" : 0, "$s0" : 0, "$s1" : 0, "$s2" : 0, "$s3": 0, "$s4": 0, "$s5": 0, "$s6": 0, "$s7": 0, "$t8": 0, "$t9": 0, "$k0": 0, "$k1": 0, "$gp": 0x10008000, "$sp": 0x7fffeffc,
             "$fp": 0, "$ra": 0}
    memory = {}
    run(instructions)
    
main()