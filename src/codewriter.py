#!/usr/bin/env python
from enum import Enum
import os

cType = Enum("cType", "ARITHMETIC POP PUSH LABEL \
                       GOTO IF FUNCTION RETURN CALL")
operator = {'add': '+',
            'sub': '-',
            'and': '&',
            'or': '|',
            'neg': '-',
            'not': '!',
            'eq': 'JEQ',
            'lt': 'JLT',
            'gt': 'JGT'}
segLabel = {'local': '@LCL',
            'argument': '@ARG',
            'pointer': '@R3',
            'this': '@THIS',
            'that': '@THAT',
            'temp': '@R5'}


class CodeWriter:
    def __init__(self, fileName, prog):
        self.outFile = open(fileName + ".asm", 'w')
        self.progName = os.path.basename(fileName)
        self.prog = prog
        self.ifCount = 0
        return None

    def popDReg(self):
        lines = '\n'.join(['@SP', 'AM=M-1', 'D=M\n'])
        return lines

    def pushDReg(self):
        lines = '\n'.join(['@SP', 'A=M', 'M=D', '@SP', 'M=M+1\n'])
        return lines

    def loadDReg(self, seg, i, src):
        if (seg in ['constant']):
            lines = '\n'.join([f'@{i}', 'D=A\n'])
        if (seg in ['local', 'argument', 'this', 'that']):
            lines = '\n'.join([f'@{i}', 'D=A\n'])
            lines += f'{segLabel[seg]}\n'
            lines += '\n'.join(['A=M+D', f'D={src}\n'])
        if (seg in ['temp', 'pointer']):
            lines = '\n'.join([f'@{i}', 'D=A\n'])
            lines += f'{segLabel[seg]}\n'
            lines += '\n'.join(['A=A+D', f'D={src}\n'])
        if (seg in ['static']):
            lines = '\n'.join([f'@{self.progName}.{i}', f'D={src}\n'])
        return lines

    def writeArithmetics(self, command):
        comStr = command[1]
        comment = '// ' + comStr + '\n'
        self.outFile.write(comment)
        if (comStr in ['add', 'sub', 'and', 'or']):
            lines = self.popDReg()
            lines += 'A=A-1\n'
            lines += f'M=M{operator[comStr]}D\n'
        elif (comStr in ['neg', 'not']):
            lines = self.popDReg()
            lines += f'M={operator[comStr]}M\n'
            lines += '\n'.join(['@SP', 'M=M+1\n'])
        elif (comStr in ['eq', 'gt', 'lt']):
            lines = self.popDReg()
            lines += '\n'.join(['A=A-1', 'D=M-D', 'M=-1\n'])
            lines += f'@__ENDIF{self.ifCount}__\n'
            lines += f'D;{operator[comStr]}\n'
            lines += '\n'.join(['@SP', 'A=M-1', 'M=0\n'])
            lines += f'(__ENDIF{self.ifCount}__)\n'
            self.ifCount += 1
        self.outFile.write(lines)
        pass

    def writePushPop(self, command):
        comType = command[0]
        segment = command[1]
        index = command[2]

        if (comType.name == "POP"):
            comStr = 'pop'
            comment = '// ' + ' '.join((comStr, segment, index)) + '\n'
            self.outFile.write(comment)
            self.pop(segment, index)
        elif (comType.name == "PUSH"):
            comStr = 'push'
            comment = '// ' + ' '.join((comStr, segment, index)) + '\n'
            self.outFile.write(comment)
            self.push(segment, index)
        # debugging
        pass

    def push(self, seg, i):
        lines = self.loadDReg(seg, i, 'M')
        lines += self.pushDReg()
        self.outFile.write(lines)
        pass

    def pop(self, seg, i):
        lines = self.loadDReg(seg, i, 'A')
        lines += '\n'.join(['@R13', 'M=D\n'])
        lines += self.popDReg()
        lines += '\n'.join(['@R13', 'A=M', 'M=D\n'])
        self.outFile.write(lines)
        pass

    def writeCode(self):
        for com in self.prog:
            if (com[0].name == "ARITHMETIC"):
                self.writeArithmetics(com)
            if (com[0].name == "POP" or com[0].name == "PUSH"):
                self.writePushPop(com)
        lines = '(__ENDPROG__)\n'
        lines += '@__ENDPROG__\n'
        lines += '0;JMP\n'
        self.outFile.write(lines)
        pass
