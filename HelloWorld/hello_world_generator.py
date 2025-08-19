#!/usr/bin/env python3
"""
Cross-Platform Hello World Code Generator
A GUI application that displays programming languages and generates Hello World code.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import sys

class HelloWorldGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Hello World Code Generator")
        self.root.geometry("900x700")
        
        # Create circuit board background
        self.create_circuit_background()
        
        # Configure digital fonts
        self.digital_font = ("Courier New", 10, "bold")  # Fallback font
        self.title_font = ("Courier New", 16, "bold")
        self.label_font = ("Courier New", 12, "bold")
        
        # Try to use more digital-looking fonts if available
        try:
            # These fonts give a more digital/dot-matrix appearance
            available_fonts = list(font.families())
            if "OCR A Extended" in available_fonts:
                self.digital_font = ("OCR A Extended", 10)
                self.title_font = ("OCR A Extended", 16, "bold")
                self.label_font = ("OCR A Extended", 12, "bold")
            elif "Consolas" in available_fonts:
                self.digital_font = ("Consolas", 10, "bold")
                self.title_font = ("Consolas", 16, "bold")
                self.label_font = ("Consolas", 12, "bold")
            elif "Monaco" in available_fonts:
                self.digital_font = ("Monaco", 10, "bold")
                self.title_font = ("Monaco", 16, "bold")
                self.label_font = ("Monaco", 12, "bold")
        except:
            pass  # Use fallback fonts
        
        # Programming languages with their code templates and compilation info
        # Structure: language -> {code: template, compile: command, type: compiled/interpreted}
        self.languages = {
            "Python": {
                "code": 'print("{text}")',
                "type": "interpreted"
            },
            "JavaScript": {
                "code": 'console.log("{text}");',
                "type": "interpreted"
            },
            "Java": {
                "code": '''public class HelloWorld {{
    public static void main(String[] args) {{
        System.out.println("{text}");
    }}
}}''',
                "compile": "javac HelloWorld.java && java HelloWorld",
                "type": "compiled"
            },
            "BASIC": {
                "Atari BASIC": {
                    "code": '''10 PRINT "{text}"
20 END''',
                    "type": "interpreted"
                },
                "Commodore BASIC": {
                    "code": '''10 PRINT "{text}"
20 END''',
                    "type": "interpreted"
                },
                "Apple BASIC": {
                    "code": '''10 PRINT "{text}"
20 END''',
                    "type": "interpreted"
                },
                "Microsoft BASIC": {
                    "code": '''10 PRINT "{text}"
20 END''',
                    "type": "interpreted"
                },
                "GW-BASIC": {
                    "code": '''10 PRINT "{text}"
20 END''',
                    "type": "interpreted"
                },
                "QBasic": {
                    "code": '''PRINT "{text}"''',
                    "type": "interpreted"
                },
                "QuickBASIC": {
                    "code": '''PRINT "{text}"''',
                    "compile": "qb hello.bas",
                    "type": "compiled"
                },
                "FreeBASIC": {
                    "code": '''PRINT "{text}"''',
                    "compile": "fbc hello.bas",
                    "type": "compiled"
                },
                "PureBASIC": {
                    "code": '''PrintN("{text}")''',
                    "compile": "pbcompiler hello.pb",
                    "type": "compiled"
                },
                "BBC BASIC": {
                    "code": '''PRINT "{text}"''',
                    "type": "interpreted"
                },
                "Sinclair BASIC": {
                    "code": '''10 PRINT "{text}"
20 STOP''',
                    "type": "interpreted"
                },
                "TI-BASIC": {
                    "code": '''Disp "{text}"''',
                    "type": "interpreted"
                },
                "HP BASIC": {
                    "code": '''PRINT "{text}"''',
                    "type": "interpreted"
                },
                "HP-71B BASIC": {
                    "code": '''10 DISP "{text}"
20 END''',
                    "type": "interpreted"
                },
                "HP-75 BASIC": {
                    "code": '''10 DISP "{text}"
20 END''',
                    "type": "interpreted"
                },
                "HP-85 BASIC": {
                    "code": '''10 PRINT "{text}"
20 END''',
                    "type": "interpreted"
                },
                "BASICA": {
                    "code": '''10 PRINT "{text}"
20 END''',
                    "type": "interpreted"
                },
                "True BASIC": {
                    "code": '''PRINT "{text}"
END''',
                    "type": "interpreted"
                },
                "PowerBASIC": {
                    "code": '''PRINT "{text}"''',
                    "compile": "pbcc hello.bas",
                    "type": "compiled"
                },
                "Liberty BASIC": {
                    "code": '''print "{text}"
end''',
                    "type": "interpreted"
                },
                "Just BASIC": {
                    "code": '''print "{text}"
end''',
                    "type": "interpreted"
                },
                "Yabasic": {
                    "code": '''print "{text}"''',
                    "type": "interpreted"
                },
                "Gambas": {
                    "code": '''Print "{text}"''',
                    "compile": "gbc3 -ag hello.gambas",
                    "type": "compiled"
                },
                "B4X (Basic4android)": {
                    "code": '''Log("{text}")''',
                    "compile": "Compile via B4A IDE",
                    "type": "compiled"
                },
                "REALbasic/Xojo": {
                    "code": '''MsgBox("{text}")''',
                    "compile": "Compile via Xojo IDE",
                    "type": "compiled"
                },
                "Visual Basic": {
                    "code": '''Module HelloWorld
    Sub Main()
        Console.WriteLine("{text}")
    End Sub
End Module''',
                    "compile": "vbc hello.vb && hello.exe",
                    "type": "compiled"
                },
            },
            "C": {
                "C (K&R)": {
                    "code": '''#include <stdio.h>

main()
{{
    printf("{text}\\n");
}}''',
                    "compile": "cc hello.c -o hello && ./hello",
                    "type": "compiled"
                },
                "C89/C90 (ANSI C)": {
                    "code": '''#include <stdio.h>

int main(void)
{{
    printf("{text}\\n");
    return 0;
}}''',
                    "compile": "gcc -std=c89 hello.c -o hello && ./hello",
                    "type": "compiled"
                },
                "C99": {
                    "code": '''#include <stdio.h>

int main(void)
{{
    printf("{text}\\n");
    return 0;
}}''',
                    "compile": "gcc -std=c99 hello.c -o hello && ./hello",
                    "type": "compiled"
                },
                "C11": {
                    "code": '''#include <stdio.h>

int main(void)
{{
    printf("{text}\\n");
    return 0;
}}''',
                    "compile": "gcc -std=c11 hello.c -o hello && ./hello",
                    "type": "compiled"
                },
                "C17/C18": {
                    "code": '''#include <stdio.h>

int main(void)
{{
    printf("{text}\\n");
    return 0;
}}''',
                    "compile": "gcc -std=c17 hello.c -o hello && ./hello",
                    "type": "compiled"
                },
                "C23": {
                    "code": '''#include <stdio.h>

int main(void)
{{
    printf("{text}\\n");
    return 0;
}}''',
                    "compile": "gcc -std=c2x hello.c -o hello && ./hello",
                    "type": "compiled"
                },
            },
            "Fortran": {
                "FORTRAN 66": {
                    "code": '''      PROGRAM HELLO
      PRINT *, '{text}'
      END''',
                    "compile": "f77 hello.f -o hello && ./hello",
                    "type": "compiled"
                },
                "FORTRAN 77": {
                    "code": '''      PROGRAM HELLO
      PRINT *, '{text}'
      END''',
                    "compile": "f77 hello.f -o hello && ./hello",
                    "type": "compiled"
                },
                "Fortran 90": {
                    "code": '''program hello
    print *, '{text}'
end program hello''',
                    "compile": "gfortran hello.f90 -o hello && ./hello",
                    "type": "compiled"
                },
                "Fortran 95": {
                    "code": '''program hello
    print *, '{text}'
end program hello''',
                    "compile": "gfortran -std=f95 hello.f95 -o hello && ./hello",
                    "type": "compiled"
                },
                "Fortran 2003": {
                    "code": '''program hello
    use iso_fortran_env, only: output_unit
    write(output_unit, '(a)') '{text}'
end program hello''',
                    "compile": "gfortran -std=f2003 hello.f03 -o hello && ./hello",
                    "type": "compiled"
                },
                "Fortran 2008": {
                    "code": '''program hello
    use iso_fortran_env, only: output_unit
    write(output_unit, '(a)') '{text}'
end program hello''',
                    "compile": "gfortran -std=f2008 hello.f08 -o hello && ./hello",
                    "type": "compiled"
                },
                "Fortran 2018": {
                    "code": '''program hello
    use iso_fortran_env, only: output_unit
    write(output_unit, '(a)') '{text}'
end program hello''',
                    "compile": "gfortran -std=f2018 hello.f18 -o hello && ./hello",
                    "type": "compiled"
                },
            },
            "C++": {
                "code": '''#include <iostream>

int main() {{
    std::cout << "{text}" << std::endl;
    return 0;
}}''',
                "compile": "g++ hello.cpp -o hello && ./hello",
                "type": "compiled"
            },
            "C#": {
                "code": '''using System;

class Program {{
    static void Main() {{
        Console.WriteLine("{text}");
    }}
}}''',
                "compile": "csc hello.cs && hello.exe",
                "type": "compiled"
            },
            "Go": {
                "code": '''package main

import "fmt"

func main() {{
    fmt.Println("{text}")
}}''',
                "compile": "go build hello.go && ./hello",
                "type": "compiled"
            },
            "Rust": {
                "code": '''fn main() {{
    println!("{text}");
}}''',
                "compile": "rustc hello.rs && ./hello",
                "type": "compiled"
            },
            "Ruby": 'puts "{text}"',
            "PHP": '<?php\necho "{text}\\n";\n?>',
            "Swift": 'print("{text}")',
            "Kotlin": '''fun main() {{
    println("{text}")
}}''',
            "Scala": '''object HelloWorld {{
    def main(args: Array[String]): Unit = {{
        println("{text}")
    }}
}}''',
            "R": 'cat("{text}\\n")',
            "MATLAB": 'fprintf("{text}\\n");',
            "Perl": 'print "{text}\\n";',
            "Lua": 'print("{text}")',
            "Haskell": '''main :: IO ()
main = putStrLn "{text}"''',
            "Erlang": '''main() ->
    io:format("{text}~n").''',
            "Elixir": 'IO.puts("{text}")',
            "Clojure": '(println "{text}")',
            "F#": 'printfn "{text}"',
            "Visual Basic": '''Module HelloWorld
    Sub Main()
        Console.WriteLine("{text}")
    End Sub
End Module''',
            "Pascal": '''program HelloWorld;
begin
    writeln('{text}');
end.''',
            "COBOL": '''IDENTIFICATION DIVISION.
PROGRAM-ID. HELLO-WORLD.
PROCEDURE DIVISION.
DISPLAY '{text}'.
STOP RUN.''',

            "Bash": 'echo "{text}"',
            "PowerShell": 'Write-Host "{text}"',
            "SQL": 'SELECT \'{text}\' AS message;',
            "HTML": '''<!DOCTYPE html>
<html>
<head>
    <title>Hello World</title>
</head>
<body>
    <h1>{text}</h1>
</body>
</html>''',
            "CSS": '''body::before {{
    content: "{text}";
    font-size: 24px;
    font-weight: bold;
}}''',
            "Dart": '''void main() {{
    print('{text}');
}}''',
            "TypeScript": 'console.log("{text}");',
            "Objective-C": '''#import <Foundation/Foundation.h>

int main() {{
    NSLog(@"{text}");
    return 0;
}}''',
            "Groovy": 'println "{text}"',
            "Julia": 'println("{text}")',
            "Nim": 'echo "{text}"',
            "Crystal": 'puts "{text}"',
            "Zig": '''const std = @import("std");

pub fn main() void {{
    std.debug.print("{text}\\n", .{{}});
}}''',
            "D": '''import std.stdio;

void main() {{
    writeln("{text}");
}}''',
            "OCaml": 'print_endline "{text}";;',
            "Scheme": '(display "{text}")\\n(newline)',
            "Racket": '#lang racket\\n(displayln "{text}")',
            "Common Lisp": '(format t "{text}~%")',
            "Prolog": '''hello_world :-
    write('{text}'), nl.

:- hello_world.''',
            "Smalltalk": "Transcript show: '{text}'; cr.",
            "Ada": '''with Ada.Text_IO;

procedure Hello_World is
begin
    Ada.Text_IO.Put_Line("{text}");
end Hello_World;''',
            "Tcl": 'puts "{text}"',
            "Verilog": '''module hello_world;
    initial begin
        $display("{text}");
        $finish;
    end
endmodule''',
            "VHDL": '''library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity hello_world is
end hello_world;

architecture Behavioral of hello_world is
begin
    process
    begin
        report "{text}";
        wait;
    end process;
end Behavioral;''',
            "ActionScript": '''package {{
    import flash.display.Sprite;
    import flash.text.TextField;
    
    public class HelloWorld extends Sprite {{
        public function HelloWorld() {{
            var txt:TextField = new TextField();
            txt.text = "{text}";
            addChild(txt);
        }}
    }}
}}''',
            "CoffeeScript": 'console.log "{text}"',
            "Elm": '''module Main exposing (..)

import Html exposing (text)

main =
    text "{text}"''',
            "PureScript": '''module Main where

import Prelude
import Effect.Console (log)

main = log "{text}"''',
            "ReasonML": 'Js.log("{text}");',
            "Solidity": '''pragma solidity ^0.8.0;

contract HelloWorld {{
    function sayHello() public pure returns (string memory) {{
        return "{text}";
    }}
}}''',
            "Vyper": '''@external
@view
def hello_world() -> String[100]:
    return "{text}"''',
            "Oberon": '''MODULE HelloWorld;
IMPORT Out;
BEGIN
    Out.String("{text}");
    Out.Ln
END HelloWorld.''',
            "Modula-2": '''MODULE HelloWorld;
FROM InOut IMPORT WriteString, WriteLn;
BEGIN
    WriteString("{text}");
    WriteLn
END HelloWorld.''',
            "C#": '''using System;

class Program {{
    static void Main() {{
        Console.WriteLine("{text}");
    }}
}}''',
            "Go": '''package main

import "fmt"

func main() {{
    fmt.Println("{text}")
}}''',
            "Rust": '''fn main() {{
    println!("{text}");
}}''',
            "Ruby": 'puts "{text}"',
            "PHP": '<?php\necho "{text}\\n";\n?>',
            "Swift": 'print("{text}")',
            "Kotlin": '''fun main() {{
    println("{text}")
}}''',
            "Scala": '''object HelloWorld {{
    def main(args: Array[String]): Unit = {{
        println("{text}")
    }}
}}''',
            "R": 'cat("{text}\\n")',
            "MATLAB": 'fprintf("{text}\\n");',
            "Perl": 'print "{text}\\n";',
            "Lua": 'print("{text}")',
            "Haskell": '''main :: IO ()
main = putStrLn "{text}"''',
            "Erlang": '''main() ->
    io:format("{text}~n").''',
            "Elixir": 'IO.puts("{text}")',
            "Clojure": '(println "{text}")',
            "F#": 'printfn "{text}"',
            "Visual Basic": '''Module HelloWorld
    Sub Main()
        Console.WriteLine("{text}")
    End Sub
End Module''',
            "Pascal": '''program HelloWorld;
begin
    writeln('{text}');
end.''',
            "Fortran": '''program hello
    print *, '{text}'
end program hello''',
            "COBOL": '''IDENTIFICATION DIVISION.
PROGRAM-ID. HELLO-WORLD.
PROCEDURE DIVISION.
DISPLAY '{text}'.
STOP RUN.''',

            "Bash": 'echo "{text}"',
            "PowerShell": 'Write-Host "{text}"',
            "SQL": 'SELECT \'{text}\' AS message;',
            "HTML": '''<!DOCTYPE html>
<html>
<head>
    <title>Hello World</title>
</head>
<body>
    <h1>{text}</h1>
</body>
</html>''',
            "CSS": '''body::before {{
    content: "{text}";
    font-size: 24px;
    font-weight: bold;
}}''',
            "Dart": '''void main() {{
    print('{text}');
}}''',
            "TypeScript": 'console.log("{text}");',
            "Objective-C": '''#import <Foundation/Foundation.h>

int main() {{
    NSLog(@"{text}");
    return 0;
}}''',
            "Groovy": 'println "{text}"',
            "Julia": 'println("{text}")',
            "Nim": 'echo "{text}"',
            "Crystal": 'puts "{text}"',
            "Zig": '''const std = @import("std");

pub fn main() void {{
    std.debug.print("{text}\\n", .{{}});
}}''',
            "D": '''import std.stdio;

void main() {{
    writeln("{text}");
}}''',
            "OCaml": 'print_endline "{text}";;',
            "Scheme": '(display "{text}")\\n(newline)',
            "Racket": '#lang racket\\n(displayln "{text}")',
            "Common Lisp": '(format t "{text}~%")',
            "Prolog": '''hello_world :-
    write('{text}'), nl.

:- hello_world.''',
            "Smalltalk": "Transcript show: '{text}'; cr.",
            "Ada": '''with Ada.Text_IO;

procedure Hello_World is
begin
    Ada.Text_IO.Put_Line("{text}");
end Hello_World;''',
            "Tcl": 'puts "{text}"',
            "Verilog": '''module hello_world;
    initial begin
        $display("{text}");
        $finish;
    end
endmodule''',
            "VHDL": '''library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity hello_world is
end hello_world;

architecture Behavioral of hello_world is
begin
    process
    begin
        report "{text}";
        wait;
    end process;
end Behavioral;''',
            "ActionScript": '''package {{
    import flash.display.Sprite;
    import flash.text.TextField;
    
    public class HelloWorld extends Sprite {{
        public function HelloWorld() {{
            var txt:TextField = new TextField();
            txt.text = "{text}";
            addChild(txt);
        }}
    }}
}}''',
            "CoffeeScript": 'console.log "{text}"',
            "Elm": '''module Main exposing (..)

import Html exposing (text)

main =
    text "{text}"''',
            "PureScript": '''module Main where

import Prelude
import Effect.Console (log)

main = log "{text}"''',
            "ReasonML": 'Js.log("{text}");',
            "Solidity": '''pragma solidity ^0.8.0;

contract HelloWorld {{
    function sayHello() public pure returns (string memory) {{
        return "{text}";
    }}
}}''',
            "Vyper": '''@external
@view
def hello_world() -> String[100]:
    return "{text}"''',
            "Oberon": '''MODULE HelloWorld;
IMPORT Out;
BEGIN
    Out.String("{text}");
    Out.Ln
END HelloWorld.''',
            "Modula-2": '''MODULE HelloWorld;
FROM InOut IMPORT WriteString, WriteLn;
BEGIN
    WriteString("{text}");
    WriteLn
END HelloWorld.''',
            "REXX": '''/* REXX */
say "{text}"''',
            "AREXX": '''/* AREXX - Amiga REXX */
say "{text}"''',
            "Eiffel": '''class
    HELLO_WORLD

create
    make

feature
    make
        do
            print("{text}%N")
        end

end''',
            "Forth": '''." {text}" CR''',
            "APL": '''⎕←'{text}' ''',
            "AppleScript": '''display dialog "{text}"''',
            "Bash": '''#!/bin/bash
echo "{text}"''',
            "csh": '''#!/bin/csh
echo "{text}"''',
            "Cray Fortran": '''C     Cray Fortran (CFT)
      PROGRAM HELLO
      WRITE(6,100) '{text}'
100   FORMAT(A)
      END''',
            "Convex Fortran": '''C     Convex Fortran
      PROGRAM HELLO
      WRITE(*,*) '{text}'
      END''',
            "DCL (VMS)": '''$ WRITE SYS$OUTPUT "{text}"''',
            "CAL (Cray Assembly)": '''        IDENT   HELLO
        ENTRY   START
START   S1      A1,=C'{text}'
        S2      A2,13
        CALL    WRITE
        J       EXIT
        END''',
            "JCL (Job Control Language)": '''//HELLO    JOB  CLASS=A,MSGCLASS=A
//STEP1    EXEC PGM=IEBGENER
//SYSPRINT DD   SYSOUT=*
//SYSUT1   DD   *
{text}
/*
//SYSUT2   DD   SYSOUT=*
//SYSIN    DD   DUMMY''',
            "IBM System/360 Assembly": '''HELLO    CSECT
         USING *,15
         WTO   '{text}',ROUTCDE=11
         BR    14
         END   HELLO''',
            "PL/I (IBM)": '''HELLO: PROCEDURE OPTIONS(MAIN);
   PUT SKIP LIST('{text}');
END HELLO;''',
            "FOCAL (PDP-8)": '''01.10 TYPE "{text}"
01.20 QUIT''',
            "RT-11 DCL": '''TYPE "{text}"''',
            "J": '''echo '{text}' ''',
            "K": '''`0:"{text}"''',
            "PostScript": '''({text}) show
showpage''',
            "Logo": '''print "{text}"''',
            "LaTeX": '''\\documentclass{{article}}
\\begin{{document}}
{text}
\\end{{document}}''',
            "TeX": '''{text}
\\bye''',
            "Assembly Variants": {
                "x86-64 (AT&T)": '''.section .data
    msg: .ascii "{text}\\n"
    msg_len = . - msg

.section .text
    .global _start

_start:
    mov $1, %rax
    mov $1, %rdi
    mov $msg, %rsi
    mov $msg_len, %rdx
    syscall
    
    mov $60, %rax
    mov $0, %rdi
    syscall''',
                "x86 (Intel)": '''section .data
    msg db '{text}', 0xA
    msg_len equ $ - msg

section .text
    global _start

_start:
    mov eax, 4
    mov ebx, 1
    mov ecx, msg
    mov edx, msg_len
    int 0x80
    
    mov eax, 1
    mov ebx, 0
    int 0x80''',
                "68000 (Motorola)": '''    section .data
msg:    dc.b    '{text}',10,0

    section .text
    global  _start

_start:
    move.l  #4,d0       ; sys_write
    move.l  #1,d1       ; stdout
    move.l  #msg,d2     ; message
    move.l  #13,d3      ; length
    trap    #0
    
    move.l  #1,d0       ; sys_exit
    move.l  #0,d1       ; exit status
    trap    #0''',
                "6502": '''        LDX #0
LOOP:   LDA MESSAGE,X
        BEQ DONE
        JSR $FFD2       ; CHROUT
        INX
        BNE LOOP
DONE:   RTS

MESSAGE:
        .BYTE "{text}",13,0''',
                "4004 (Intel)": '''; Intel 4004 Assembly
        FIM P0, >MSG    ; Load message address
        FIM P1, <MSG
LOOP:   SRC P0          ; Set ROM address
        RDM             ; Read from ROM
        JCN ZN, END     ; Jump if zero
        WMP             ; Write to output port
        INC R0          ; Increment address
        JUN LOOP        ; Jump to loop
END:    HLT             ; Halt

MSG:    DATA "{text}"
        DATA 0''',
                "PDP-8": '''        *200
START,  CLA CLL
        TAD MSG
        JMS PRINT
        HLT
MSG,    TEXT /{text}/
        PAGE''',
                "PDP-11": '''        .TITLE  HELLO
        .MCALL  .PRINT, .EXIT
START:  .PRINT  #MSG
        .EXIT
MSG:    .ASCII  /{text}/<15><12>
        .END    START''',
            },
        }
        
        # Compilation commands for compiled languages
        self.compilation_commands = {
            "Java": "javac HelloWorld.java && java HelloWorld",
            "C++": "g++ hello.cpp -o hello && ./hello",
            "C#": "csc hello.cs && hello.exe",
            "Go": "go build hello.go && ./hello",
            "Rust": "rustc hello.rs && ./hello",
            "Swift": "swiftc hello.swift -o hello && ./hello",
            "Kotlin": "kotlinc hello.kt -include-runtime -d hello.jar && java -jar hello.jar",
            "Scala": "scalac HelloWorld.scala && scala HelloWorld",
            "Pascal": "fpc hello.pas && ./hello",
            "Ada": "gnatmake hello_world.adb && ./hello_world",
            "Nim": "nim compile --run hello.nim",
            "Crystal": "crystal build hello.cr && ./hello",
            "Zig": "zig run hello.zig",
            "D": "dmd hello.d && ./hello",
            "Haskell": "ghc hello.hs && ./hello",
            "OCaml": "ocamlc -o hello hello.ml && ./hello",
            "Oberon": "Compile with Oberon compiler",
            "Modula-2": "Compile with Modula-2 compiler",
            "Eiffel": "ec hello.e && ./hello",
            "COBOL": "cobc -x hello.cob && ./hello",
            "Objective-C": "gcc -framework Foundation hello.m -o hello && ./hello",
            "Dart": "dart compile exe hello.dart && ./hello.exe",
            "Groovy": "groovyc HelloWorld.groovy && java HelloWorld",
            "Julia": "julia hello.jl",
            "Solidity": "solc hello.sol",
            "Vyper": "vyper hello.vy",
            "ActionScript": "Compile with Adobe Flash/AIR SDK",
            "Verilog": "iverilog -o hello hello.v && ./hello",
            "VHDL": "ghdl -a hello.vhd && ghdl -e hello && ghdl -r hello",
            "Forth": "gforth hello.fs",
            "PostScript": "gs hello.ps",
            "LaTeX": "pdflatex hello.tex",
            "TeX": "tex hello.tex && dvipdf hello.dvi",
            "AppleScript": "osascript hello.applescript",
            "Bash": "bash hello.sh",
            "csh": "csh hello.csh",
            "Cray Fortran": "cft hello.f && a.out",
            "Convex Fortran": "fc hello.f && a.out", 
            "DCL (VMS)": "Run on VAX/VMS system",
            "CAL (Cray Assembly)": "cal hello.cal && segldr hello && hello",
            "JCL (Job Control Language)": "Submit to IBM mainframe job queue",
            "IBM System/360 Assembly": "Assemble and link on IBM System/360",
            "PL/I (IBM)": "pli hello.pli && hello",
            "FOCAL (PDP-8)": "Run in FOCAL interpreter on PDP-8",
            "RT-11 DCL": "Run on RT-11 operating system",
            # C variants
            "  └─ C (K&R)": "cc hello.c -o hello && ./hello",
            "  └─ C89/C90 (ANSI C)": "gcc -std=c89 hello.c -o hello && ./hello",
            "  └─ C99": "gcc -std=c99 hello.c -o hello && ./hello",
            "  └─ C11": "gcc -std=c11 hello.c -o hello && ./hello",
            "  └─ C17/C18": "gcc -std=c17 hello.c -o hello && ./hello",
            "  └─ C23": "gcc -std=c2x hello.c -o hello && ./hello",
            # Fortran variants
            "  └─ FORTRAN 66": "f77 hello.f -o hello && ./hello",
            "  └─ FORTRAN 77": "f77 hello.f -o hello && ./hello",
            "  └─ Fortran 90": "gfortran hello.f90 -o hello && ./hello",
            "  └─ Fortran 95": "gfortran -std=f95 hello.f95 -o hello && ./hello",
            "  └─ Fortran 2003": "gfortran -std=f2003 hello.f03 -o hello && ./hello",
            "  └─ Fortran 2008": "gfortran -std=f2008 hello.f08 -o hello && ./hello",
            "  └─ Fortran 2018": "gfortran -std=f2018 hello.f18 -o hello && ./hello",
            # BASIC variants (compiled ones)
            "  └─ QuickBASIC": "qb hello.bas",
            "  └─ FreeBASIC": "fbc hello.bas",
            "  └─ PureBASIC": "pbcompiler hello.pb",
            "  └─ PowerBASIC": "pbcc hello.bas",
            "  └─ Gambas": "gbc3 -ag hello.gambas",
            "  └─ B4X (Basic4android)": "Compile via B4A IDE",
            "  └─ REALbasic/Xojo": "Compile via Xojo IDE",
            "  └─ Visual Basic": "vbc hello.vb && hello.exe",
            # Assembly variants
            "  └─ x86-64 (AT&T)": "as hello.s -o hello.o && ld hello.o -o hello && ./hello",
            "  └─ x86 (Intel)": "nasm -f elf32 hello.asm && ld -m elf_i386 hello.o -o hello && ./hello",
            "  └─ 68000 (Motorola)": "m68k-linux-gnu-as hello.s -o hello.o && m68k-linux-gnu-ld hello.o -o hello",
            "  └─ 6502": "ca65 hello.s && ld65 hello.o -o hello.prg",
            "  └─ 4004 (Intel)": "Assemble with Intel 4004 assembler",
            "  └─ PDP-8": "Assemble with PAL-8 assembler",
            "  └─ PDP-11": "macro hello.mac && link hello",
        }
        
        self.setup_ui()
        
    def create_circuit_background(self):
        """Create a subtle circuit board pattern background using tkinter Canvas"""
        # We'll create this dynamically in the UI setup since we need the window size
        pass
    
    def setup_ui(self):
        # Set the background color to match circuit board
        self.root.configure(bg='#2a2a2a')
        
        # Create main frame with circuit board background
        main_frame = tk.Frame(self.root, bg='#2a2a2a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a canvas for circuit board background
        self.bg_canvas = tk.Canvas(main_frame, highlightthickness=0, bg='#2a2a2a')
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Draw circuit board pattern
        def draw_circuit_pattern():
            self.bg_canvas.delete("circuit")
            canvas_width = self.bg_canvas.winfo_width()
            canvas_height = self.bg_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:  # Make sure canvas is initialized
                # Draw grid pattern
                trace_color = '#404040'
                pad_color = '#505050'
                component_color = '#606060'
                
                # Horizontal traces
                for y in range(0, canvas_height, 30):
                    self.bg_canvas.create_line(0, y, canvas_width, y, fill=trace_color, width=1, tags="circuit")
                    # Add connection pads
                    for x in range(15, canvas_width, 60):
                        self.bg_canvas.create_oval(x-3, y-3, x+3, y+3, fill=pad_color, outline=pad_color, tags="circuit")
                
                # Vertical traces
                for x in range(0, canvas_width, 30):
                    self.bg_canvas.create_line(x, 0, x, canvas_height, fill=trace_color, width=1, tags="circuit")
                    # Add connection pads
                    for y in range(15, canvas_height, 60):
                        self.bg_canvas.create_oval(x-3, y-3, x+3, y+3, fill=pad_color, outline=pad_color, tags="circuit")
                
                # Add some diagonal traces
                for i in range(0, canvas_width, 90):
                    for j in range(0, canvas_height, 90):
                        self.bg_canvas.create_line(i, j, i+45, j+45, fill=trace_color, width=1, tags="circuit")
                        self.bg_canvas.create_line(i+45, j, i, j+45, fill=trace_color, width=1, tags="circuit")
                
                # Add small components (rectangles)
                for x in range(45, canvas_width, 120):
                    for y in range(45, canvas_height, 120):
                        self.bg_canvas.create_rectangle(x-8, y-4, x+8, y+4, fill=component_color, outline=component_color, tags="circuit")
                
                # Send circuit pattern to back
                self.bg_canvas.tag_lower("circuit")
        
        # Bind canvas resize to redraw pattern
        self.bg_canvas.bind('<Configure>', lambda e: self.root.after(10, draw_circuit_pattern))
        
        # Create content frame with semi-transparent background
        content_frame = tk.Frame(main_frame, bg='#1a1a1a', relief=tk.RAISED, bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title with digital font and green color (like old CRT monitors)
        title_label = tk.Label(content_frame, 
                              text="Hello World Code Generator\n103+ Languages & Compilation Commands", 
                              font=self.title_font,
                              fg='#00ff00',  # Bright green like old terminals
                              bg='#1a1a1a',
                              justify=tk.CENTER)
        title_label.pack(pady=(10, 20))
        
        # Main content area
        main_content = tk.Frame(content_frame, bg='#1a1a1a')
        main_content.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Left panel - Language list
        left_frame = tk.Frame(main_content, bg='#1a1a1a')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        lang_label = tk.Label(left_frame, 
                             text="Programming Languages:", 
                             font=self.label_font,
                             fg='#00ff00',
                             bg='#1a1a1a')
        lang_label.pack(pady=(0, 5))
        
        # Language listbox with scrollbar
        listbox_frame = tk.Frame(left_frame, bg='#1a1a1a')
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.language_listbox = tk.Listbox(listbox_frame, 
                                          width=25, 
                                          font=self.digital_font,
                                          bg='#000000',  # Black background
                                          fg='#00ff00',  # Green text
                                          selectbackground='#004400',  # Dark green selection
                                          selectforeground='#00ff00')
        
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.language_listbox.yview)
        self.language_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.language_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate language list with hierarchical structure - CASE-INSENSITIVE ALPHABETICALLY SORTED
        self.flat_languages = {}  # Flattened for easy lookup
        
        # Sort the main language keys alphabetically (case-insensitive)
        sorted_languages = sorted(self.languages.keys(), key=str.lower)
        
        for key in sorted_languages:
            value = self.languages[key]
            if isinstance(value, dict) and "code" not in value:
                # This is a category with subcategories
                self.language_listbox.insert(tk.END, f"▼ {key}")
                # Sort subcategories alphabetically too (case-insensitive)
                for subkey in sorted(value.keys(), key=str.lower):
                    subvalue = value[subkey]
                    display_name = f"  └─ {subkey}"
                    self.language_listbox.insert(tk.END, display_name)
                    self.flat_languages[display_name] = subvalue
            else:
                # This is a direct language
                self.language_listbox.insert(tk.END, key)
                self.flat_languages[key] = value
        
        # Bind selection event
        self.language_listbox.bind('<<ListboxSelect>>', self.on_language_select)
        
        # Right panel - Code generation
        right_frame = tk.Frame(main_content, bg='#1a1a1a')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Custom text input
        custom_label = tk.Label(right_frame, 
                               text="Custom Text:", 
                               font=self.label_font,
                               fg='#00ff00',
                               bg='#1a1a1a')
        custom_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.custom_text = tk.StringVar(value="Hello World!")
        text_entry = tk.Entry(right_frame, 
                             textvariable=self.custom_text, 
                             font=("Arial", 10),  # Keep normal font for input
                             bg='#ffffff',
                             fg='#000000')
        text_entry.pack(fill=tk.X, pady=(0, 10))
        text_entry.bind('<KeyRelease>', self.on_text_change)
        
        # Generated code area
        code_label = tk.Label(right_frame, 
                             text="Generated Code:", 
                             font=self.label_font,
                             fg='#00ff00',
                             bg='#1a1a1a')
        code_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.code_text = scrolledtext.ScrolledText(right_frame, 
                                                  wrap=tk.WORD, 
                                                  font=("Courier New", 10),  # Keep normal font for code
                                                  height=15, 
                                                  width=50,
                                                  bg='#000000',  # Black background
                                                  fg='#00ff00',  # Green text
                                                  insertbackground='#00ff00')  # Green cursor
        self.code_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Compilation commands area (for compiled languages)
        self.compile_frame = tk.Frame(right_frame, bg='#1a1a1a')
        self.compile_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.compile_label = tk.Label(self.compile_frame, 
                                     text="Compilation Commands:", 
                                     font=self.label_font,
                                     fg='#00ff00',
                                     bg='#1a1a1a')
        self.compile_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.compile_text = tk.Text(self.compile_frame, 
                                   wrap=tk.WORD, 
                                   font=("Courier New", 10), 
                                   height=3, 
                                   width=50, 
                                   bg='#000000',  # Black background
                                   fg='#ffff00',  # Yellow text for commands
                                   insertbackground='#ffff00')
        self.compile_text.pack(fill=tk.X, pady=(0, 5))
        
        # Initially hide compilation section
        self.compile_frame.pack_forget()
        
        # Buttons frame
        button_frame = tk.Frame(right_frame, bg='#1a1a1a')
        button_frame.pack(fill=tk.X)
        
        # Style buttons to match the theme
        button_style = {
            'font': self.digital_font,
            'bg': '#004400',
            'fg': '#00ff00',
            'activebackground': '#006600',
            'activeforeground': '#00ff00',
            'relief': tk.RAISED,
            'bd': 2
        }
        
        copy_btn = tk.Button(button_frame, text="Copy Code", command=self.copy_code, **button_style)
        copy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        copy_compile_btn = tk.Button(button_frame, text="Copy Compile Command", command=self.copy_compile, **button_style)
        copy_compile_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(button_frame, text="Clear", command=self.clear_code, **button_style)
        clear_btn.pack(side=tk.LEFT)
        
        # Status bar
        status_frame = tk.Frame(content_frame, bg='#1a1a1a')
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Select a programming language to generate code")
        status_bar = tk.Label(status_frame, 
                             textvariable=self.status_var,
                             font=self.digital_font,
                             fg='#ffff00',  # Yellow for status
                             bg='#000000',
                             relief=tk.SUNKEN, 
                             anchor=tk.W,
                             bd=1)
        status_bar.pack(fill=tk.X, padx=5, pady=5)
        
    def on_language_select(self, event):
        """Handle language selection from the listbox"""
        selection = self.language_listbox.curselection()
        if selection:
            selected_item = self.language_listbox.get(selection[0])
            # Skip category headers (those starting with ▼)
            if selected_item.startswith("▼"):
                return
            # Generate code for the selected language/sublanguage
            if selected_item in self.flat_languages:
                self.generate_code_from_template(selected_item, self.flat_languages[selected_item])
            
    def on_text_change(self, event):
        """Handle custom text changes"""
        selection = self.language_listbox.curselection()
        if selection:
            selected_item = self.language_listbox.get(selection[0])
            if not selected_item.startswith("▼") and selected_item in self.flat_languages:
                self.generate_code_from_template(selected_item, self.flat_languages[selected_item])
            
    def generate_code_from_template(self, language_name, lang_info):
        """Generate code from a template and show compilation info if applicable"""
        custom_text = self.custom_text.get() or "Hello World!"
        # Escape special characters for string formatting
        escaped_text = custom_text.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
        
        try:
            # Handle both old string format and new dict format
            if isinstance(lang_info, str):
                template = lang_info
                compile_cmd = self.compilation_commands.get(language_name)
            else:
                template = lang_info.get("code", "")
                compile_cmd = lang_info.get("compile") or self.compilation_commands.get(language_name)
            
            # Generate the code
            code = template.format(text=escaped_text)
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(1.0, code)
            
            # Show/hide compilation section based on whether we have compilation commands
            if compile_cmd:
                self.compile_text.delete(1.0, tk.END)
                self.compile_text.insert(1.0, compile_cmd)
                self.compile_frame.pack(fill=tk.X, pady=(0, 10))
            else:
                self.compile_frame.pack_forget()
            
            # Clean up the display name for status
            clean_name = language_name.replace("  └─ ", "")
            status_msg = f"Generated {clean_name} code"
            if compile_cmd:
                status_msg += " (compiled language)"
            self.status_var.set(status_msg)
            
        except Exception as e:
            self.status_var.set(f"Error generating code: {str(e)}")
            self.compile_frame.pack_forget()
            
    def generate_code(self, language):
        """Legacy method - kept for compatibility"""
        if language in self.languages:
            template = self.languages[language]
            if isinstance(template, dict):
                # This shouldn't happen with new structure, but handle gracefully
                self.status_var.set("Please select a specific language variant")
                return
            self.generate_code_from_template(language, template)
                
    def copy_compile(self):
        """Copy compilation command to clipboard"""
        try:
            compile_cmd = self.compile_text.get(1.0, tk.END).strip()
            if compile_cmd:
                self.root.clipboard_clear()
                self.root.clipboard_append(compile_cmd)
                self.status_var.set("Compilation command copied to clipboard")
            else:
                self.status_var.set("No compilation command to copy")
        except Exception as e:
            self.status_var.set(f"Error copying compilation command: {str(e)}")
            
    def copy_code(self):
        """Copy generated code to clipboard"""
        try:
            code = self.code_text.get(1.0, tk.END).strip()
            if code:
                self.root.clipboard_clear()
                self.root.clipboard_append(code)
                self.status_var.set("Code copied to clipboard")
            else:
                self.status_var.set("No code to copy")
        except Exception as e:
            self.status_var.set(f"Error copying code: {str(e)}")
            
    def clear_code(self):
        """Clear the generated code area"""
        self.code_text.delete(1.0, tk.END)
        self.compile_text.delete(1.0, tk.END)
        self.compile_frame.pack_forget()
        self.status_var.set("Code cleared")

def main():
    """Main function to run the application"""
    try:
        root = tk.Tk()
        app = HelloWorldGenerator(root)
        
        # Center the window on screen
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Set minimum window size
        root.minsize(600, 400)
        
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
