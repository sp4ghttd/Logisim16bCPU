# -*- coding: utf-8 -*-

import numpy as np
import os

SCRIPTDIR = "E:\Jerome\Documents\LogiSim"
os.chdir(SCRIPTDIR);

### DEFINES

nHandles = 14+1+2+1

i = nHandles-1;
andValue = 2**nHandles-1

#Decode
PCCapture       = (1<<i) ; i-=1 ;
PCCount         = (1<<i) ; i-=1 ;
src1InSrc2      = (1<<i) ; i-=1 ; #b15
dstInSrc2       = (1<<i) ; i-=1 ;
i-=1 ; #Sign-Extend Source : 2b, 4 values.
R0_SESrc        = (0<<i) ; 
R1w_SESrc       = (1<<i) ; 
R2w_SESrc       = (2<<i) ;
I2_SESrc        = (3<<i) ; i-=1 ;

#EXecute
R1Capture       = (1<<i) ; i-=1 ;
PC_R1orPC       = (1<<i) ; i-=1 ; #b10
SE_R2orSE       = (1<<i) ; i-=1 ;
i-=2 ; #aluControls : 3b, 8 values.
add_ALUctrls    = (0<<i) ;
sub_ALUctrls    = (1<<i) ;
and_ALUctrls    = (2<<i) ;
or_ALUctrls     = (3<<i) ;
xor_ALUctrls    = (4<<i) ;
sll_ALUctrls    = (5<<i) ;
srl_ALUctrls    = (6<<i) ;
sra_ALUctrls    = (7<<i) ; i-=1 ;
updateFlags     = (1<<i) ; i-=1 ; #b5

#MEMory
RAMWrite = (1<<i) ; i-=1 ;

#WriteBack
i-=1 ; #writeSrc : 2b, 4 values.
PC_WriteSrc     = (0<<i) ;
RAM_WriteSrc    = (1<<i) ;
ALU_WriteSrc    = (2<<i) ;
R1_WriteSrc     = (3<<i) ; i-=1 ;
REGWrite        = (1<<i) ; i-=1 ;
PCLoad          = (1<<i) ; i-=1 ;


print("OK count" if i==-1 else "bad count")

del i;

### functions 


def fill_rom_v2(romName_str, nBitsCode, nBitsPerAddress, mnemAndInstr_dict):
    opNumbers = list(delem[0] for delem in mnemAndInstr_dict.values())
    opNames = list(mnemAndInstr_dict.keys())
    maxOpValuep1 = 1<<nBitsCode #maxOpValue+1
    assert  max(opNumbers)<maxOpValuep1, "/fill_rom_V2/ : error : not enough addressing bits w.r.t. opNumbers";

    r_rom_v2 = np.zeros( maxOpValuep1, np.uint32);
    for i in range(maxOpValuep1):
        if i in opNumbers:
            instrMnemo = opNames[opNumbers.index(i)]
            print(f"adding instr {instrMnemo} to rom file {romName_str}")
            toBeAddedVector = mnemAndInstr_dict[instrMnemo][1]
            r_rom_v2[i] = toBeAddedVector;
            
    return r_rom_v2;
        
#format to formatType v2.0 raw
def format_rom_v2(fileName_str, r_rom, nBitsPerAddress):
    nHexsPerCommand =  int(np.ceil(nBitsPerAddress/4))
    fid = open(fileName_str, mode="wt")
    fid.write("v2.0 raw\n");
    for i in range(r_rom.shape[0]):
        fid.write("{0:0{1:d}x}".format(r_rom[i], nHexsPerCommand)+"\n");
    fid.close();
    
    return;

### ALL-ROMS

## R2-ROM
mnemonicsAndsingleCycledInstrs_R2 = { 
 "NOP":[0b000, 0],
 "CMP":[0b001, updateFlags],
 "MOV":[0b010, dstInSrc2|R1Capture|R1_WriteSrc|REGWrite],
 "<<" :[0b101, dstInSrc2|sll_ALUctrls|ALU_WriteSrc|REGWrite],
 ">>" :[0b110, dstInSrc2|srl_ALUctrls|ALU_WriteSrc|REGWrite],
 ">>>":[0b111, dstInSrc2|sra_ALUctrls|ALU_WriteSrc|REGWrite],
}

## MEM-ROM
mnemonicsAndsingleCycledInstrs_MEM = {
 "lw" : [0, dstInSrc2|R1w_SESrc|SE_R2orSE|add_ALUctrls|RAM_WriteSrc|REGWrite],
 "sw" : [1, dstInSrc2|R1w_SESrc|SE_R2orSE|add_ALUctrls|RAMWrite],
}

## 1REG1IMM-ROM
mnemonicsAndsingleCycledInstrs_1REG1IMM = {
 "JR"   : [0, src1InSrc2|R2w_SESrc|SE_R2orSE|add_ALUctrls|PCLoad],
 "ADDa": [1, src1InSrc2|dstInSrc2|R2w_SESrc|SE_R2orSE|add_ALUctrls|updateFlags|ALU_WriteSrc|REGWrite], #ADDi1
}

## 2W-ROM

commonHandles = PCCount|I2_SESrc|SE_R2orSE
mnemonicsAndsingleCycledInstrs_2W = {
 "JAL"  : [0, commonHandles|PCCapture|dstInSrc2|PC_R1orPC|PC_WriteSrc|REGWrite|PCLoad],
 "ALUi": [1, commonHandles|dstInSrc2|updateFlags|ALU_WriteSrc|REGWrite], #ALUi2
 "LOD": [2, commonHandles|dstInSrc2|ALU_WriteSrc|REGWrite], #LODi2
 "CMPi": [3, commonHandles|updateFlags], #CMPi2
}

### Generate ROMs

formatType = "raw-v2.0";
nBitsPerAddress = nHandles
nHexsPerAddress = int(np.ceil(nBitsPerAddress/4))

#a/ R2-rom. RQ: aluControls /could/ be straightfully read from opCode.
nBitsCode = 3

romName_str = "r2-rom_{}x{}_raw2".format(1<<nBitsCode, nHexsPerAddress)
rom_r = fill_rom_v2(romName_str, nBitsCode, nBitsPerAddress, mnemonicsAndsingleCycledInstrs_R2);
format_rom_v2("./v2roms_space/"+romName_str+".hex", rom_r, nBitsPerAddress);

#b/ MEM-rom
nBitsCode = 1

romName_str = "mem-rom_{}x{}_raw2".format(1<<nBitsCode, nHexsPerAddress)
rom_r = fill_rom_v2(romName_str, nBitsCode, nBitsPerAddress, mnemonicsAndsingleCycledInstrs_MEM);
format_rom_v2("./v2roms_space/"+romName_str+".hex", rom_r, nBitsPerAddress);

#c/ 1REG1IMM-rom
nBitsCode = 1

romName_str = "1reg1imm-rom_{}x{}_raw2".format(1<<nBitsCode, nHexsPerAddress)
rom_r = fill_rom_v2(romName_str, nBitsCode, nBitsPerAddress, mnemonicsAndsingleCycledInstrs_1REG1IMM);
format_rom_v2("./v2roms_space/"+romName_str+".hex", rom_r, nBitsPerAddress);

#b/ 2W-rom. RM: aluControls /will/ be straightfully read from opCode.
nBitsCode = 2

romName_str = "2w-rom_{}x{}_raw2".format(1<<nBitsCode, nHexsPerAddress)
rom_r = fill_rom_v2(romName_str, nBitsCode, nBitsPerAddress, mnemonicsAndsingleCycledInstrs_2W);
format_rom_v2("./v2roms_space/"+romName_str+".hex", rom_r, nBitsPerAddress);
