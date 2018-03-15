#!/usr/bin/env python
from enum import Enum

cType = Enum("cType", "ARITHMETIC POP PUSH LABEL \
                       GOTO IF FUNCTION RETURN CALL")
arithmetic = ("add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not")


class Parser:
    def __init__(self, fileName):
        self.inFile = open(fileName + ".vm", 'r')
        return None

    def initializeParser(self):
        lines = self.inFile.readlines()
        self.prog = map(lambda x: x.strip(), lines)
        self.isComment = False
        return None

    def advance(self, line):
        if ('//' in line):
            i = line.find('/')
            outLine = line[:i].strip()
        elif ('/*' in line and '*/' in line):
            i = line.find('/')
            j = line[:i+1].find('/')
            outLine = (line[:i] + line[j+1:]).strip()
        elif ('/*' in line):
            self.isComment = True
            outLine = ''
        elif ('*/' in line):
            self.isComment = False
            outLine = ''
        elif (not line or self.isComment):
            outLine = ''
        else:
            outLine = line
        return outLine

    def commandType(self, line):
        if ('pop' in line):
            t = cType.POP
        elif ('push' in line):
            t = cType.PUSH
        elif ('label' in line):
            t = cType.LABEL
        elif ('goto' in line):
            t = cType.GOTO
        elif ('if-goto' in line):
            t = cType.IF
        elif ('function' in line):
            t = cType.FUNCTION
        elif ('call' in line):
            t = cType.CALL
        elif ('return' in line):
            t = cType.RETURN
        elif (any(x in line for x in arithmetic)):
            t = cType.ARITHMETIC
        else:
            t = None
        return t

    def arg1(self, line, command):
        if (command == cType.ARITHMETIC):
            arg1 = line
        else:
            arg1 = line.split()[1]
        return arg1

    def arg2(self, line):
        return line.split()[2]

    def parse(self):
        for line in self.prog:
            parsedLine = self.advance(line)
            if (not parsedLine):
                continue
            command = self.commandType(line)
#            print(command)  # debug
            if (command != cType.RETURN):
                arg1 = self.arg1(parsedLine, command)
            else:
                arg1 = None
            arg2Cond = (command == cType.POP or command == cType.PUSH or
                        command == cType.FUNCTION or command == cType.CALL)
            if (arg2Cond):
                arg2 = self.arg2(parsedLine)
            else:
                arg2 = None
            yield (command, arg1, arg2)
