
; program code
; compute A[8] x B[8], uint8_t type.
.DEFINE _depth 8	;-- tweak it with depth of B (put smallest value of the two inside B)
					;-- for faster computation.
.DEFINE _LCDaddr 0xf0


; reserve 2 registers for the 2 8bits words to be multiplied.
.alias A -> $a0
.alias B -> $a1
.alias TMP -> $t0
.alias RES -> $v0
.alias I -> $t1
.alias B_I -> $t2

; display is at address 0x7c
; $a3 will hold display address.
.alias DISP -> $a2
; res is to be displayed.

.alias MASK -> $s0

; ## DATA segment : Global Variables ##
.org 0x80
.word 253 ; must be <256
.word 197 ; must be <256. Put the lowest here.

startup:
 .org 0x00
 NOP ;mandatory for initial startup
 
init:
 AND %A, %B_I, %B
 LOD $gp, #0x80
 lw %A, 0($gp)
 lw %B, 1($gp)
 ; LOD %A, #8
 ; LOD %B, #9

 MOV %RES, $0 ;-- res = 0
 
 LOD %I, #_depth 	;-- variable i=depth=4
 LOD %MASK, #1		;-- fixed mask
 LOD %DISP, #_LCDaddr ;-- fixed display address

 
loop:
 
 ;display i value at each start of iter.
 JAL display_i_sbr ;display_i label (PC relative)
 
 AND %B_I, %B, %MASK  	;-- b_i = B & 0x1
 
 ; CMP #MASK, #B_I 		;-- 1-b_i == 0 ?
 BZ else			;BNZ else, had CMP been kept.
 MOV %TMP, %A			;-- if case, so tmp = A
 JI #2				;-- skip past the else block. 
else:
 MOV %TMP, $0		;-- else case (i.e. b_i=0), so tmp=0

 >>  %B, %B			;-- B = B>>1 
 <<  %A, %A			;-- A << 1 for possible store in tmp at next iter.
 
 ADD %RES, %RES, %TMP 	;-- res += tmp
 
 ADDa %I, #-1 ;-- i -= 1 (or reuse fixed '1 value of /MASK/ reg).
 ; CMP $w, $x; depth-i==0 ? [OPTIONAL AS ADDa UPDATES FLAGS ON ITS OWN]
 BNZ loop


display_res:
 sw %RES, 0(%DISP) 	; print res value at loop end
 
stall:
 JI stall
 
.org 0x70
display_i_sbr:
 sw %I, 0(%DISP) 	; print i value at each iter start*
 JR $ra, #1			; as it is a subroutine
 
.org 0x60
.word 0x5555
.word 0xAAAA