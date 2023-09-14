# -*- coding: utf-8 -*-

import numpy as np
import os
import time

SCRIPTDIR = "E:\\Jerome\\Documents\\LogiSim\\test_programs"
os.chdir(SCRIPTDIR);


A = 164
B = 16
depth2use=5;

def signExtend(value, vDepth, tDepth):
    assert vDepth>0, "/signExtend/ : vDepth must be >=1"
    res = value;
    sgn = value>>(vDepth-1)
    for j in range(vDepth,tDepth):
        res += sgn<<j
    return res;

def soft_mult(A, B, depth):
    res = 0
    for i in range(depth):
        b_i = (B>>i)&0x1
                
        tmp = A if b_i==1 else 0
        tmp <<= i
        
        res += tmp;
        
    return res;
    

def soft_mult_asasm(A, B, depth):
    res = 0
    i = depth
    while(i!=0):
        b_i = B&0x1
        B >>= 1
        
        tmp = A if b_i==1 else 0
        A <<= 1
        
        res += tmp;
        
        i -= 1
        
    return res;
   
time1 = time.perf_counter()    
C1 = soft_mult(A, B, depth2use)
time2 = time.perf_counter() 
C2 = soft_mult_asasm(A, B, depth2use)
time3 = time.perf_counter() 


print(f"(soft_mult) {A} x {B} = {C1} in {(time2-time1)*1e6:.3f}µs")
print(f"(asasmmult) {A} x {B} = {C2} in {(time3-time2)*1e6:.3f}µs")

