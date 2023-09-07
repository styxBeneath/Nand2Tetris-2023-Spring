// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

//pseudocode:
// max_number_of_screen_register = 8192 (stored in R0 register)
// while(true) {
//     D = KBD
//     if(D==0) {
//         number_of_register = 0;
//         while(number_of_register - max_number_of_screen_register != 0) {
//             set the register #number_of_register to '0000000000000000'
//             number_of_register++;
//         }
//     } else {
//         number_of_register = 0;
//         while(number_of_register - max_number_of_screen_register != 0) {
//             set the register #number_of_register to '1111111111111111'
//             number_of_register++;
//         }
//     }
// }

//R0 - max num of screen regs + 1
//R1 - index of iteration
@8192 //max num of screen regs + 1
D=A;
@R0
M=D;

(LOOP)
@KBD
D=M;

@PAINTWHITE
D;JEQ
@PAINTBLACK
0;JMP

(PAINTWHITE)
    @R1
    M=0;
    (WHITELOOP)
        @R1
        D=M;
        @R0
        D=D-M;

        @ENDPAINT
        D;JEQ

        @R1
        D=M;
        @SCREEN
        A=A+D;
        M=0;

        @R1
        M=M+1;
        @WHITELOOP
        0;JMP

(PAINTBLACK)
    @R1
    M=0;
    (BLACKLOOP)
        @R1
        D=M;
        @R0
        D=D-M;

        @ENDPAINT
        D;JEQ

        @R1
        D=M;
        @SCREEN
        A=A+D;
        M=-1;

        @R1
        M=M+1;
        @BLACKLOOP
        0;JMP

(ENDPAINT)
@LOOP
0;JMP