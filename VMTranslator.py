#!/usr/bin/env python
from src.parser import Parser
from src.codewriter import CodeWriter
import sys
import os


def main():
    if (len(sys.argv) < 2):
        print("Enter VM file name")
        print("Example:")
        print(f"{os.path.basename(sys.argv[0])} path_to_file.vm")
        input("Press Enter to exit...")
    fileName = os.path.splitext(sys.argv[1])[0]
    print(fileName)
    myParser = Parser(fileName)
    myParser.initializeParser()
    parsedProg = [line for line in myParser.parse()]
    myCodeWriter = CodeWriter(fileName, parsedProg)
    myCodeWriter.writeCode()
    return None


if __name__ == "__main__":
    main()
