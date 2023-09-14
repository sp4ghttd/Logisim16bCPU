# -*- coding: utf-8 -*-

RESET       ="\033[0m"
BLACK       ="\033[30m" 
RED         ="\033[31m"     
GREEN       ="\033[32m"      
YELLOW      ="\033[33m"     
BLUE        ="\033[34m"     
MAGENTA     ="\033[35m"      
CYAN        ="\033[36m"  
BOLD        ="\033[1m"
ITALIC      ="\033[3m"
UNDERLINE   ="\033[4m" 

BLACKBG     ="\033[40m";
REDBG       ="\033[41m";
GREENBG     ="\033[42m";
YELLOWBG    ="\033[43m";

SLOWBLINK   ="\033[5m" 
RAPIDBLINK  ="\033[6m" 
  

import numpy as np
import os
import re

SCRIPTDIR = "your-local-repo-here"
assemblyFile = "./test_programs/soft_8b_int_mult[V2].s" 
HEXPRGMFILE = "./test_programs/flashMe.hex"
try:
    os.chdir(SCRIPTDIR);
except FileNotFoundError:
    print(f"{RED} Veuillez renseigner {ITALIC}SCRIPTDIR{RESET}{RED} avec le chemin dans lequel ce trouve ce script {RESET}")
    exit()


### DEFINES

Itype = (1<<15)

opCodes = {
 "R3": { "ADD":0,   "SUB":1,   "AND":2,  
  "OR":3,  "XOR":4 },
 "R2": { "NOP":0, "CMP":1, "MOV":2, 
 "<<":5,  ">>":6, ">>>":7 },
 "R0": { "BZ":0, "BNZ":1, "BLT":2, "BLE":3, 
 "JI": 4 },
 "MEM": {"lw":0, "sw":1 },
 "1R1I": {"JR":0, "ADDa": 1 },
 "2W": {"JAL":0, "ADDi":1, "SUBi":1, "ANDi":1, 
  "ORi":1, "XORi":1, "LOD":2, "CMPi": 3}
}

regNums = {
 "0":0, "gp":1, "sp":2, "bp":3,
 "ra":4, "s0":5, "t0":6, "t1":7,
 "s1":8, "t2":9, "t3":10, "v0":11,
 "v1":12, "a0":13, "a1":14, "a2":15
}

allMnemo = [];
for row_key, inner_dict in opCodes.items():
    allMnemo += list(inner_dict.keys())

def getMnemoStrType_v2(mnem_target, opCodes):
    for row_key, inner_dict in opCodes.items():
        if mnem_target in inner_dict.keys():
            return row_key, inner_dict[mnem_target]
    return "", 0
    
## functions

#format to formatType v2.0 raw
def format_rom_v2(fileName_str, r_rom, nBitsPerAddress):
    nHexsPerCommand =  int(np.ceil(nBitsPerAddress/4))
    fid = open(fileName_str, mode="wt")
    fid.write("v2.0 raw\n");
    for i in range(r_rom.shape[0]):
        fid.write("{0:0{1:d}x}".format(r_rom[i], nHexsPerCommand)+"\n");
    fid.close();
    
    return;
    
#check registers are accessibles & immediate doesnt overflow
def sanityChecks_v2(strType, valsDict):
    print(RED, end='')
    
    # if "dstNum" in valsDict.keys():

    print(RESET, end='')
    
    return;


##main



def parseDotDirectives(assemblyFile):

    labelTable = {};
    aliasTable = {};
    defineTable= {};
    dorgTable  = {};
    linestoMEMcommit = [];

    fid = open(assemblyFile, mode="rt")
    a = fid.readline()
    currentAddr = 0;
    idxline = 0;
    while(a!=""):
        cmdStr = a.rstrip('\n').split(';')[0]
        if len(cmdStr)>2:
            #line of interest
            if( (cmdStr[0] != " ") and (cmdStr[0] != '.') ): #check label
                print(f"{a} is label!");
                labelTable[cmdStr.split(":")[0]] = currentAddr
                
            elif ".org" in cmdStr: #check .org
                print(f"{a} is a .org directive!");
                pattern = r'0x[0-9a-fA-F]+' ;  
                match = re.search(pattern, a)
                if not match:
                    raise ValueError(f"ERROR on line {a}")
                currentAddr = eval(match.group(0))
                # linestoMEMcommit.append((idxline, currentAddr)); #reset caOffset at each stumbled upon.

            elif ".alias" in cmdStr: #check .alias
                pattern = r'\.alias\s(\w+)\s->\s\$(\w+)\b'
                matches = re.match(pattern, cmdStr)
                if not matches:
                    raise ValueError(f"ERROR on {cmdStr}")
                aliasTable[matches.group(1)] = matches.group(2)
                
            elif ".DEFINE" in cmdStr: #check .DEFINE
                pattern = r'\.DEFINE\s(_[a-zA-Z0-9]+)\s([#%\$\w]+)\b'
                matches = re.match(pattern, cmdStr)
                if not matches:
                    raise ValueError(f"ERROR on {cmdStr}")
                defineTable[matches.group(1)] = matches.group(2)
                
            else:
                #line is instruction
                linestoMEMcommit.append((idxline, currentAddr));
                #parse instruction for 2W. If so, inc Addr.
                pattern = r'\s*([><a-zA-Z0-9]+)\s*' ;  
                match = re.search(pattern, cmdStr)
                if not match:
                    raise ValueError(f"ERROR on {cmdStr}")
                strMnem = match.group(1)
                opFamily, opCode = getMnemoStrType_v2(strMnem, opCodes)
                if opFamily=="2W":
                    print(f"found 2W instr on : {cmdStr}");
                    currentAddr += 1
                        
                currentAddr += 1 #only for actual memory entry (i.e., no label, define, or alias).

        #next file line
        a = fid.readline();
        idxline += 1;
    
    fid.close();
    return labelTable, aliasTable, defineTable, linestoMEMcommit

def processRegName(regOrAliasStr, aliasTable):
    """
    optionally replace alias by its reg name. then lstrip '$'.
    """
    try:
        regName = aliasTable[regOrAliasStr.lstrip('%')] if '%' in regOrAliasStr else regOrAliasStr.lstrip('$')
    except:
        raise ValueError(f"{RED}+undefined alias {allStrs[j]}+{RESET}");
    return regName;
    
def immediateBoundaries(ImmValue, isSigned, bdepth):
    if isSigned:
        if not -2**(bdepth-1)<=ImmValue<=+2**(bdepth-1)-1:
            print(f"{RED}Warning: Imm={ImmValue} exceeds {bdepth}b capacity!{RESET}");
        ImmValue %= 2**bdepth
    else:
        if not 0<=ImmValue<=+2**bdepth-1:
            print(f"{RED}Warning: Imm={ImmValue} exceeds {bdepth}b capacity!{RESET}");
    return ImmValue;

def translateR2R3(regsStr, opCode, currentAddr, nexpectedRegs):
    assert 2<=nexpectedRegs<=3, "/translateR2R3/ : nexpectedRegs input error."
    if 2==nexpectedRegs and opCode==0:
        return [currentAddr, 0]    #NOP
    pattern = r'\s*([%$\w]+)[,]?\s*'
    allStrs = re.findall(pattern, regsStr);
    if len(allStrs)!=nexpectedRegs:
        raise ValueError(f"ERROR on {regsStr}")
        
    instrCode = opCode<<12;
    poslists = [8,4,0] if nexpectedRegs==3 else [0,4]
    for j in range(len(poslists)):
        regName = processRegName(allStrs[j], aliasTable)
        instrCode |= regNums[regName]<<poslists[j]
    return [currentAddr, instrCode];

def translateR0orJAL(regsStr, opCode, currentAddr, isJAL=False):
    """
    if isALUi2, fill word 2 only.
    """
    pattern = r'\s*(#?\w+)\b'
    match = re.search(pattern, regsStr)
    if not match:
        raise ValueError(f"ERROR on {regsStr}")
    ImmStr = match.group(1)
    if ImmStr[0]=='_' : #overrule define
        ImmStr = defineTable[ImmStr]
    if ImmStr[0]=='#' : #direct immediate value
        ImmValue = eval(ImmStr.split('#')[1]) ;
    else:               #labeled immediate value
        ImmValue = labelTable[ImmStr] - currentAddr;
    
    if not isJAL:
        ImmValue -= 1; #to account for latch of PC' inside CPU value whereas reference of hereby calculation was PC...
        ImmValue = immediateBoundaries(ImmValue, True, 11);
        instrCode = 1<<15 | opCode<<11 | ImmValue
    else:
        ImmValue = immediateBoundaries(ImmValue, True, 16);
        instrCode = ImmValue
    return [currentAddr, instrCode];
    
def translateMEMorALUi2(regsStr, opCode, currentAddr, isALUi2=False):
    """
    if isALUi2, fill words 1 and 2
    """
    pattern = r'\s*([%\$\w]+),\s*([+-]?\d+)\(?([%\$a-zA-Z0-9]+)\)?' #1Reg1ImmReg
    matches = re.search(pattern, regsStr);
    if not matches:
        raise ValueError(f"ERROR on {regsStr}")
    instrCode = 0b110<<13 | opCode<<12 if not isALUi2 else 0b111<<13 | 1<<8
    poslists = [0,8,4]
    for j in [0,2]:
        regName = processRegName(matches.group(1+j), aliasTable)
        instrCode |= regNums[regName]<<poslists[j]
    j=1
    ImmValue = eval(matches.group(1+j))
    if not isALUi2:
        ImmValue = immediateBoundaries(ImmValue, True, 4);
        instrCode |= ImmValue<<poslists[j]
        addrAndCMD = [currentAddr, instrCode];
    else:
        ImmValue = immediateBoundaries(ImmValue, True, 16);
        addrAndCMD =  [currentAddr,   instrCode];
        addrAndCMD += [currentAddr+1, ImmValue];
    return addrAndCMD
    
def translate1R1I(regsStr, opCode, currentAddr, isI2andCode=0):
    pattern = r'\s*([%\$\w]+),\s*#([+-]?[\w]+)\b';
    matches = re.search(pattern, regsStr);
    if not matches:
        raise ValueError(f"ERROR on {regsStr}")
    regName = processRegName(matches.group(1), aliasTable)
    ImmStr = matches.group(2);
    if ImmStr[0]=='_' : #overrule define
        ImmStr = defineTable[ImmStr]
    ImmValue = eval(ImmStr) ;
    
    if not isI2andCode:
        ImmValue = immediateBoundaries(ImmValue, True, 7);
        instrCode = 0b1011<<12 | opCode<<11 | ImmValue<<4 | regNums[regName]<<0
        addrAndCMD = [currentAddr, instrCode];
    else:
        ImmValue = immediateBoundaries(ImmValue, True, 16);
        if isI2andCode==1: #LOD
            instrCode = 0b111<<13 | 0<<10 | 2<<8 | regNums["0"]<<4 | regNums[regName]<<0
        else: #CMPi
            instrCode = 0b111<<13 | 1<<10 | 3<<8 | regNums[regName]<<4
        addrAndCMD =  [currentAddr,   instrCode];
        addrAndCMD += [currentAddr+1, ImmValue];
    return addrAndCMD
    
def translate2W(regsStr, opCode, currentAddr):
    if opCode==0: #JAL : only Immediate.
        addrAndCMD = [currentAddr, 0b111 << 13 | 0b000 << 10 | opCode << 8 
        | regNums["0"] << 4 | regNums["ra"] << 0]
        addrAndCMD += translateR0orJAL(regsStr, opCode, currentAddr+1, True);
    elif opCode==1: #ALUi : 1reg1immreg
        addrAndCMD = translateMEMorALUi2(regsStr, opCode, currentAddr, True);
    elif opCode==2: #LOD : 1reg1imm
        addrAndCMD = translate1R1I(regsStr, opCode, currentAddr, 1);
    elif opCode==3: #CMPi : 1reg1imm
        addrAndCMD = translate1R1I(regsStr, opCode, currentAddr, 2);
        
    return addrAndCMD;



print("### parsing . directives ... ###");
labelTable, aliasTable, defineTable, linestoMEMcommit = parseDotDirectives(assemblyFile)
    
romName_str = "sram_256x16_raw2.hex"
sram_128w_bin = np.ones(256, dtype=np.uint16) * 0x00; #filled with NOPs



print("### reading RAM-tbw lines ... ###");
fid = open(assemblyFile, mode="rt")
alst = fid.readlines()
cAoffset = 0;
for lidx, currentAddr in linestoMEMcommit:
    a = alst[lidx]    
    cmdStr = a.rstrip('\n').split(';')[0]
    
    if ".org" in cmdStr: #reset cAoffset if programmer explicited position.
        cAoffset = 0
        addrAndCMD = []; #no commit to sram.
    
    if ".word" in cmdStr :
        print(f"{cmdStr} is a .word directive!");
        pattern = r'.word\s*[#]?([\w]+)'
        matches = re.match(pattern, cmdStr)
        if not matches:
            raise ValueError(f"ERROR on {cmdStr}")
        ImmValue = eval(matches.group(1))
        addrAndCMD = [currentAddr+cAoffset, ImmValue]
        
    else:
        #-- parse instruction
        pattern = r'\s*([><a-zA-Z0-9]+)\s*' ;  
        match = re.search(pattern, cmdStr)
        if not match:
            raise ValueError(f"ERROR on {cmdStr}")
        strMnem = match.group(1)
        opFamily, opCode = getMnemoStrType_v2(strMnem, opCodes)
        
        print(f"{cmdStr} is an {opFamily}-type instr.");
        regsStr = cmdStr.split(strMnem)[-1]
        
        if opFamily=="R3":
            addrAndCMD = translateR2R3(regsStr, opCode, currentAddr+cAoffset, 3)
            
        elif opFamily=="R2":
            # if strMnem=="MOV":
            #     dstInSrc2=True;
            # else:
            #     dstInSrc2=False;
            addrAndCMD = translateR2R3(regsStr, opCode, currentAddr+cAoffset, 2)
            
        elif opFamily=="R0":
            addrAndCMD = translateR0orJAL(regsStr, opCode, currentAddr+cAoffset, False)
            
        elif opFamily=="MEM":
            addrAndCMD = translateMEMorALUi2(regsStr, opCode, currentAddr+cAoffset)
        
        elif opFamily=="1R1I":
            addrAndCMD = translate1R1I(regsStr, opCode, currentAddr+cAoffset)
            
        elif opFamily=="2W":
            addrAndCMD = translate2W(regsStr, opCode, currentAddr+cAoffset)
            # cAoffset += 1;
            
    if len(addrAndCMD)>=2:
        print(f"\t==>{addrAndCMD[1]:016b}"); 
    
    #write deduced RAM entries into our RAM array.
    for i in range(len(addrAndCMD)//2):
        if i==1:
            print(f"detected {ITALIC}{MAGENTA}♥i2♥{RESET} instr, will pack 2 words into sram")
        sram_128w_bin[addrAndCMD[i*2]] = addrAndCMD[i*2+1]


format_rom_v2(HEXPRGMFILE, sram_128w_bin, 16);
print("\n:::flashMe.hex correctly created!");
            
#close file
fid.close()
