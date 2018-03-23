#!/usr/bin/env python
import os

operator = {'add': "+",
            'sub': "-",
            'and': "&",
            'or':  "|",
            'neg': "-",
            'not': "!",
            'eq':  "JEQ",
            'lt':  "JLT",
            'gt':  "JGT"}
segLabel = {'local':    "@LCL",
            'argument': "@ARG",
            'pointer':  "@R3",
            'this':     "@THIS",
            'that':     "@THAT",
            'temp':     "@R5"}


class CodeWriter:
    def __init__(self, fileName):
        self.prog = fileName
        self.ifCount = 0
        self.retCount = 0
        self.func = ""
        return None

    def initHeader(self):
        lines = ["@256", "D=A", "@SP", "M=D"]
        lines += self.writeCall(("", "Sys.init", "0"))
        return lines

    def popDReg(self):
        return ["@SP", "AM=M-1", "D=M"]

    def pushDReg(self):
        return ["@SP", "A=M", "M=D", "@SP", "M=M+1"]

    def initLocals(self, n, lines=[]):
        if (not n):
            return lines
        return self.initLocals(n - 1, lines + ["M=0", "A=A+1"])

    def loadDReg(self, seg, i, src):
        lines = []
        if (seg in ["constant"]):
            lines += ["@{0}".format(i), "D=A"]
        if (seg in ["local", "argument", "this", "that"]):
            lines += ["@{0}".format(i), "D=A"]
            lines += ["{0}".format(segLabel[seg])]
            lines += ["A=M+D", "D={0}".format(src)]
        if (seg in ["temp", "pointer"]):
            lines += ["@{0}".format(i), "D=A"]
            lines += ["{0}".format(segLabel[seg])]
            lines += ["A=A+D", "D={0}".format(src)]
        if (seg in ["static"]):
            lines = ["@{0}.{1}".format(self.prog, i),
                     "D={0}".format(src)]
        return lines

    def writeArithmetics(self, command):
        comStr = command[1]
        lines = []
        if (comStr in ["add", "sub", "and", "or"]):
            lines += self.popDReg()
            lines += ["A=A-1"]
            lines += ["M=M{0}D".format(operator[comStr])]
        elif (comStr in ["neg", "not"]):
            lines += self.popDReg()
            lines += ["M={0}M".format(operator[comStr])]
            lines += ["@SP", "M=M+1"]
        elif (comStr in ["eq", "gt", "lt"]):
            lines += self.popDReg()
            lines += ["A=A-1", "D=M-D", "M=-1"]
            lines += ["@__ENDIF{0}__".format(self.ifCount)]
            lines += ["D;{0}".format(operator[comStr])]
            lines += ["@SP", "A=M-1", "M=0"]
            lines += ["(__ENDIF{0}__)".format(self.ifCount)]
            self.ifCount += 1
        return lines

    def writePushPop(self, command):
        comType = command[0]
        segment = command[1]
        index = command[2]

        if (comType == "POP"):
            lines = self.pop(segment, index)
        elif (comType == "PUSH"):
            lines = self.push(segment, index)
        return lines

    def push(self, seg, i):
        lines = self.loadDReg(seg, i, "M")
        lines += self.pushDReg()
        return lines

    def pop(self, seg, i):
        lines = self.loadDReg(seg, i, "A")
        lines += ["@R13", "M=D"]
        lines += self.popDReg()
        lines += ["@R13", "A=M", "M=D"]
        return lines

    def writeLabel(self, command):
        lines = ["({0}${1})".format(self.func, command[1])]
        return lines

    def writeGoto(self, command):
        lines = ["@{0}${1}".format(self.func, command[1])]
        lines += ["0;JMP"]
        return lines

    def writeIfgoto(self, command):
        lines = self.popDReg()
        lines += ["@{0}${1}".format(self.func, command[1])]
        lines += ["D;JNE"]
        return lines

    def writeCall(self, command):
        lines = ["@SP", "D=M", "@R13", "M=D"]
        lines += ["@{0}$ret{1}".format(self.func, self.retCount), "D=A"]
        lines += self.pushDReg()
        lines += ["@LCL", "D=M"]
        lines += self.pushDReg()
        lines += ["@ARG", "D=M"]
        lines += self.pushDReg()
        lines += ["@THIS", "D=M"]
        lines += self.pushDReg()
        lines += ["@THAT", "D=M"]
        lines += self.pushDReg()
        lines += ["@R13", "D=M", "@{0}".format(command[2])]
        lines += ["D=D-A", "@ARG", "M=D"]
        lines += ["@SP", "D=M", "@LCL", "M=D"]
        lines += ["@{0}".format(command[1]), "0;JMP"]
        lines += ["({0}$ret{1})".format(self.func, self.retCount)]
        self.retCount += 1
        return lines

    def writeFunction(self, command):
        self.func = command[1]
        lines = ["({0})".format(command[1])]
        lines += ["@SP", "A=M"]
        lines += self.initLocals(int(command[2]))
        lines += ["D=A", "@SP", "M=D"]
        return lines

    def writeReturn(self, command):
        lines = ["@LCL", "D=M", "@5", "A=D-A", "D=M", "@R13", "M=D"]
        lines += self.popDReg()
        lines += ["@ARG", "A=M", "M=D", "D=A+1", "@SP", "M=D"]
        lines += ["@LCL", "AM=M-1", "D=M", "@THAT", "M=D"]
        lines += ["@LCL", "AM=M-1", "D=M", "@THIS", "M=D"]
        lines += ["@LCL", "AM=M-1", "D=M", "@ARG", "M=D"]
        lines += ["@LCL", "AM=M-1", "D=M", "@LCL", "M=D"]
        lines += ["@R13", "A=M", "0;JMP"]
        return lines

    def writeCode(self, prog):
        # self.prog content (commandType, arg1, arg2)
        lines = []
        for com in prog:
            if (com[0] == "ARITHMETIC"):
                lines += ["// {0}".format(com[1])]
                lines += self.writeArithmetics(com)
            if (com[0] == "POP" or com[0] == "PUSH"):
                lines += ["// {0} {1} {2}".format(com[0], com[1], com[2])]
                lines += self.writePushPop(com)
            if (com[0] == "LABEL"):
                lines += ["// label {0}".format(com[1])]
                lines += self.writeLabel(com)
            if (com[0] == "GOTO"):
                lines += ["// goto {0}".format(com[1])]
                lines += self.writeGoto(com)
            if (com[0] == "IF"):
                lines += ["// if-goto {0}".format(com[1])]
                lines += self.writeIfgoto(com)
            if (com[0] == "CALL"):
                lines += ["// call {0} {1}".format(com[1], com[2])]
                lines += self.writeCall(com)
            if (com[0] == "FUNCTION"):
                lines += ["// function {0} {1}".format(com[1], com[2])]
                lines += self.writeFunction(com)
            if (com[0] == "RETURN"):
                lines += ["// return"]
                lines += self.writeReturn(com)
        return lines
