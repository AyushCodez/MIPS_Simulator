memory = {}
registers = {"$0" : 0, "$at" : 0, "$v0" : 0, "$v1" : 0, "$a0" : 0, "$a1": 0, "$a2" : 0, "$a3" : 0, "$t0" : 0, "$t1" : 0, "$t2" : 0, "$t3" : 0, "$t4" : 0, "$t5" : 0, "$t6" : 0,
             "$t7" : 0, "$s0" : 0, "$s1" : 0, "$s2" : 0, "$s3": 0, "$s4": 0, "$s5": 0, "$s6": 0, "$s7": 0, "$t8": 0, "$t9": 0, "$k0": 0, "$k1": 0, "$gp": 0x10008000, "$sp": 0x7fffeffc,
             "$fp": 0, "$ra": 0}

registersList = ["$0", "$at", "$v0", "$v1", "$a0", "$a1", "$a2", "$a3", "$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6",
             "$t7", "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7", "$t8", "$t9", "$k0", "$k1", "$gp", "$sp",
             "$fp", "$ra"]

phaseRegisters = {"IDIF" : 0, "IDEX" : 0, "EXMEM" : 0, "MEMWB" : 0}

def IF(instructions,pc):
    if pc in instructions:
        return instructions[pc] #full instruction
    else:
        return ''

def ID(instruction,signals):
    opcode = instruction[0:6]
    control_unit(opcode)
    rs,rt,write_reg = instruction[6:11],instruction[11:16],[instruction[11:16],instruction[16:21]][signals['RegDst']] 
    values = registerFile(rs,rt,write_reg)
    if(instruction[16] == "1"):
        imm = -twoscomplement(int(instruction[16:],2))
    else:
        imm = int(instruction[16:],2)
    return imm, int(instruction[26:],2), values[0], values[1],instruction[6:11],instruction[11:16],[instruction[11:16],instruction[16:21]][signals['RegDst']] 
    #imm,funct_field,read_data-1,read_data-2,reg1,reg2,write_reg

def EX(rd1,rd2,imm,funct_field,instruction,pc,signals):
    ALUres = ALU(signals["ALUOp"],signals["ALUSrc"],imm,funct_field,rd1,rd2)
    pc_next = PC_Update(currentLocation=pc,isZero=int(ALUres == 0),
                        branch=imm,branch_signal=signals["Branch"],
                        jump = signals["JMP"],jumpLocation=int(instruction[6:],2)*4)
    return ALUres,pc_next

def Mem(ALURes,rd2,signals):
    rd = DataMemory(address=ALURes,write_data=rd2,mem_read=signals["MemRead"],mem_write=signals["MemWrite"])
    return [ALURes,rd][signals["MemtoReg"]]#write_data
    
def WB(rs,rt,reg_write,write_data,signals):
    registerFile(rs,rt,reg_write,regWrite=signals["RegWrite"],
                 regDst=signals["RegDst"],writeData=write_data) #writing data if required
    

    
    
def generateInstructions(machineCode, startMemory = "0x400000"):
    instructions = dict()
    insts = machineCode.split("\n")
    for i in range(len(insts)-1):
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


def registerFile(rs,rt,write_reg, regWrite = 0, regDst = 0, writeData = 0):
    register1 = int(rs, 2)
    register2 = int(rt, 2)
    reg1, reg2 = registersList[register1], registersList[register2]
    if(regWrite == 1):
        if(regDst == 0):
            registers[reg2] = writeData
        else:
            registers[registersList[int(write_reg, 2)]] = writeData
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
        if(address in memory):
            return memory[address]
        return 0
    

def twoscomplement(num):    # Function to return the 2's complement of a binary number
    t = (2**16-1) ^ num
    return t+1

def shift_phases(phases,new_inst):
    phases['IF'],phases['IF-ID'],phases['ID-EX'],phases['EX-Mem'],phases['Mem-WB'] = {'instruction' :new_inst},phases['IF'],phases['IF-ID'],phases['ID-EX'],phases['EX-Mem']
    return phases

def run(instructions):
    instructions = generateInstructions(instructions)
    PC = "0x400000"
    phases = {
        'IF': {'instruction' : ''},
        'IF-ID': {'instruction':''},
        'ID-EX': {'instruction' : ''},
        'EX-Mem': {'instruction' : ''},
        'Mem-WB': {'instruction' : ''},
    }
    clock_cycles = 0
    instruction = ''
    count = 0
    instruction = IF(instructions,PC)
    phases = shift_phases(phases,instruction)
    phases['IF']['PC'] = PC
    stall = 0
    while(PC in instructions or count <5):
        if(PC not in instructions):
            count +=1
        else:
            count = 0
        flag = 0
        clock_cycles+=1
        if(phases['Mem-WB']['instruction'] != ''):
            WB(phases['Mem-WB']['rs'],phases['Mem-WB']['rt'],phases['Mem-WB']['write_reg'],phases['Mem-WB']['write_data'],phases['Mem-WB']['signals'])
        if(phases['EX-Mem']['instruction'] != ''):
            phases['EX-Mem']['write_data'] = Mem(phases['EX-Mem']['ALURes'],phases['EX-Mem']['rd2'],phases['EX-Mem']['signals'])
            

        if(phases['ID-EX']['instruction'] != '' and stall == 0):    
            phases['ID-EX']['ALURes'],pc_next = EX(phases['ID-EX']['rd1'],phases['ID-EX']['rd2'],phases['ID-EX']['imm'],
                                                phases['ID-EX']['funct_field'],phases['ID-EX']['instruction'],
                                                phases['ID-EX']['PC'],phases['ID-EX']['signals'])
            if((phases['ID-EX']['ALURes'] == 0 and phases['ID-EX']['signals']['Branch'] == 1) or phases['ID-EX']['signals']['JMP'] == 1):
                flag = 1
                phases['IF-ID'] = {'instruction' : ''} #Flushing
                phases['IF'] = {'instruction' : ''}
                pass
        
        
        
        if(phases['IF-ID']['instruction'] != '' and stall == 0):
            phases['IF-ID']['signals'] = control_unit(int(phases['IF-ID']['instruction'][:6],2))
            phases['IF-ID']['imm'], phases['IF-ID']['funct_field'],phases['IF-ID']['rd1'],phases['IF-ID']['rd2'],phases['IF-ID']['rs'],phases['IF-ID']['rt'],phases['IF-ID']['write_reg']= ID(phases['IF-ID']['instruction'],phases['IF-ID']['signals'])
        

        if(flag == 0 and stall == 0):
            PC = hex(int(PC, 16) + 4)
        elif stall == 0:
            PC = pc_next
        instruction = IF(instructions,PC)
        if(stall == 0):
            phases = shift_phases(phases,instruction)
        else:
            phases['Mem-WB'], phases['EX-Mem'] = phases['EX-Mem'],{'instruction':''}
        phases['IF']['PC'] = PC
        stall = 0
        #Forwarding
        if(phases['ID-EX']['instruction'] != ''):
            if(phases['Mem-WB']['instruction'] != '' and phases['Mem-WB']['signals']['RegWrite'] == 1):
                if(phases['Mem-WB']['write_reg'] == phases['ID-EX']['rs'] != '00000'):
                    phases['ID-EX']['rd1'] = [phases['Mem-WB']['ALURes'],phases['Mem-WB']['write_data']][phases['Mem-WB']['signals']['MemtoReg']]
                if(phases['Mem-WB']['write_reg'] == phases['ID-EX']['rt'] != '00000'):
                    phases['ID-EX']['rd2'] = [phases['Mem-WB']['ALURes'],phases['Mem-WB']['write_data']][phases['Mem-WB']['signals']['MemtoReg']]
            
            if(phases['EX-Mem']['instruction'] != '' and phases['EX-Mem']['signals']['RegWrite'] == 1):
                if(phases['EX-Mem']['signals']['MemtoReg'] == 0):
                    if(phases['EX-Mem']['write_reg'] == phases['ID-EX']['rs'] != '00000'):
                        phases['ID-EX']['rd1'] = phases['EX-Mem']['ALURes']
                    if(phases['EX-Mem']['write_reg'] == phases['ID-EX']['rt'] != '00000'):
                        phases['ID-EX']['rd2'] = phases['EX-Mem']['ALURes']
                elif(phases['EX-Mem']['write_reg'] == phases['ID-EX']['rs'] or phases['EX-Mem']['write_reg'] == phases['ID-EX']['rt']):
                    stall = 1
                    pass
    print("Clock cycles taken:",clock_cycles)
    print("Registers:")
    for reg in registers:
        print(f"{reg}: {registers[reg]}")
    print("Memory:")
    print(memory)

def main():
    global memory,registers
    memory = {}
    n = 9
    print(f"Calculating {n}! and storing in $s2:")
    registers['$s4'] = n
    with open("mcode2.txt",'r') as f:
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
