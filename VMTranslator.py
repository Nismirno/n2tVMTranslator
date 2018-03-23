#!/usr/bin/env python
from VMParser import Parser
from VMCodewriter import CodeWriter
from pathlib import Path
import sys


def processDirectory(inputPath):
    fileName = str(inputPath.stem)
    myWriter = CodeWriter(fileName)
    lines = myWriter.initHeader()
    for f in inputPath.glob("*.vm"):
        lines += processFile(f)
    return lines


def processFile(inputPath):
    myParser = Parser(inputPath)
    fileName = str(inputPath.stem)
    parsedProg = [line for line in myParser.parse()]
    myWriter = CodeWriter(fileName)
    return myWriter.writeCode(parsedProg)


def main():
    if (len(sys.argv) < 2):
        print("Enter VM file name or directory")
        print("Example:")
        print("{0} path_to_file.vm".format(sys.argv[0]))
        print("{0} path_to_dir".format(sys.argv[0]))
        input("Press Enter to exit...")
    inputPath = Path(sys.argv[1])
    realPath = Path.resolve(inputPath)
    isDir = realPath.is_dir()
    if (isDir):
        outName = str(realPath / realPath.name)
        outFile = open("{0}.asm".format(outName), 'w')
        output = processDirectory(realPath)
        outFile.write('\n'.join(output))
    elif (realPath.suffix == ".vm"):
        outName = str(realPath.parent / realPath.stem)
        outFile = open("{0}.asm".format(outName), 'w')
        output = processFile(realPath)
        outFile.write('\n'.join(output))
    else:
        print("Input file must be of .vm extension")
    return None


if __name__ == "__main__":
    main()
