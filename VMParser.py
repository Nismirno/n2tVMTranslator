#!/usr/bin/env python
arithmetic = ("add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not")


class Parser:
    def __init__(self, fileName):
        with fileName.open() as f:
            self.prog = list(map(lambda x: x.strip(), f.readlines()))
        self.isComment = False
        return None

    def advance(self, line):
        outLine = ''
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
            t = "POP"
        elif ('push' in line):
            t = "PUSH"
        elif ('label' in line):
            t = "LABEL"
        elif ('if' in line):
            t = "IF"
        elif ('goto' in line):
            t = "GOTO"
        elif ('function' in line):
            t = "FUNCTION"
        elif ('call' in line):
            t = "CALL"
        elif ('return' in line):
            t = "RETURN"
        elif (any(x in line for x in arithmetic)):
            t = "ARITHMETIC"
        else:
            t = None
        return t

    def arg1(self, line, command):
        if (command == "ARITHMETIC"):
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
            command = self.commandType(parsedLine)
            if (command != "RETURN"):
                arg1 = self.arg1(parsedLine, command)
            else:
                arg1 = None
            arg2Cond = (command == "POP" or command == "PUSH" or
                        command == "FUNCTION" or command == "CALL")
            if (arg2Cond):
                arg2 = self.arg2(parsedLine)
            else:
                arg2 = None
            yield (command, arg1, arg2)
