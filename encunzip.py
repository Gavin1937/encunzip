#!/usr/bin/env python3

MSG = """
INFO
       Author      - Gavin1937
       Github      - https://github.com/Gavin1937/encunzip
       encunzip.py - simple script to list & extract zip file with encodings.

SYNOPSIS
       python3 encunzip.py OPERATION ENCODING file.zip OUTPUTDIR OPERATION ARG

       you can set encunzip.py to an executable file and use:
       ./encunzip.py OPERATION ENCODING file.zip OUTPUTDIR

DESCRIPTION
       Unzip zip file with non utf-8 encodings.
       This tool is aiming to simplify command "unzip -O encoding" with a small ENCODING TABLE contians commonly used encodings.

ARGUMENTS
       OPERATION    Different operations for the script.

           l        List zip file content. (unzip -l)
                    "OUTPUTDIR" option will be ignore with this operation.

           e        Extract zip file content without file structure. (unzip -e)
                    Extracted filename's encoding will be the one specified by ENCODING.
                    "OUTPUTDIR" option is required for this operation.

           x        Extract zip file content with file structure. (unzip -x)
                    Extracted filename's encoding will be the one specified by ENCODING.
                    "OUTPUTDIR" option is required for this operation.

           p        Apply password to zipfile, this OPERATION must be add to the end of command.
                    You also need to supply a password after it.
                    After the password, you also need to supply the encoding of password.

       ENCODING     common encodings listing in ENCODING TABLE or other encodings like utf-8.

           Pick any name from ENCODING TABLE:
                name          encoding
              japanese, jp      cp932
              chinese_1, ch1    gb18030
              chinese_2, ch2    gbk

           Or use any other encodings. (utf-8, cp437, etc.)

       OUTPUTDIR    Output directory to extract into.
                    If supplied directory doesn't exist, this script will create one.

EXAMPLES:

           Listing contents in "file.zip" with jp(cp932) encoding.
               python3 encunzip.py l jp file.zip

           Extract contents in "file.zip" to directory "output" with utf-8 encoding without file structure.
               python3 encunzip.py e utf-8 file.zip output

           Extract contents in "file.zip" to directory "output" with chinese_1(gb18030) encoding keeping file structure.
               python3 encunzip.py x chinese file.zip output

           Extract contents in "file.zip" with password "1234" with chinese_1
               python3 encunzip.py e jp file.zip output p 1234 ch1

"""

from zipfile import ZipFile, ZipInfo
from sys import argv
from pathlib import Path
from shutil import copyfileobj


ENCODING_TABLE = {
    "japanese": "cp932",
    "jp": "cp932",
    "chinese_1": "gb18030",
    "ch1": "gb18030",
    "chinese_2": "gbk",
    "ch2": "gbk"
}

# list zip file content
# unzip -l
def enclszip(infile, encoding):

    # setup/check input & output
    infile = Path(infile)
    if not infile.exists():
        raise Exception(f"Cannot find input file: {infile}")

    # unzip file
    with ZipFile(infile) as zip:
        for info in zip.infolist():
            item = info.filename.encode('cp437').decode(encoding)
            print(item)

# unzip without file structure
# unzip -e
def encunzipe(infile, encoding, outfile, pwd=None):

    # setup/check input & output
    infile = Path(infile)
    if not infile.exists():
        raise Exception(f"Cannot find input file: {infile}")

    outfile = Path(outfile)
    if not outfile.exists():
        raise Exception(f"Cannot find output directory: {outfile}")

    size = zipSize(infile)
    current_size = 0

    # unzip file
    with ZipFile(infile) as zip:
        for info in zip.infolist():
            filename = info.filename
            outitem = outfile/filename[filename.rfind('/')+1:].encode('cp437').decode(encoding)
            current_size += info.file_size
            print(genPerc(current_size, size), outitem)
            if not info.is_dir(): # is file
                source = zip.open(filename, pwd=pwd)
                target = open(outitem, "wb")
                with source, target:
                    copyfileobj(source, target)

# unzip keeping file structure
# unzip -x
def encunzipx(infile, encoding, outfile, pwd=None):

    # setup/check input & output
    infile = Path(infile)
    if not infile.exists():
        raise Exception(f"Cannot find input file: {infile}")

    outfile = Path(outfile)
    if not outfile.exists():
        raise Exception(f"Cannot find output directory: {outfile}")

    size = zipSize(infile)
    current_size = 0

    # unzip file
    with ZipFile(infile) as zip:
        for info in zip.infolist():
            filename = info.filename
            outitem = outfile/filename.encode('cp437').decode(encoding)
            current_size += info.file_size
            print(genPerc(current_size, size), outitem)
            if not info.is_dir(): # is file
                source = zip.open(filename, pwd=pwd)
                target = open(outitem, "wb")
                with source, target:
                    copyfileobj(source, target)
            else:
                outitem.mkdir(parents=True, exist_ok=True)

def getEnc(enc) -> str:
    if enc in ENCODING_TABLE:
        return ENCODING_TABLE[enc]
    return enc

def genPerc(current_size, ttl_size) -> str:
    perc = ((current_size / ttl_size) * 100)
    int_part = int(perc)
    float_part = round((perc - int_part), 2)
    int_part = str(int_part).rjust(3, ' ')
    float_part = str(float_part)[2:].ljust(2, '0')
    perc = int_part + '.' + float_part + ' %'
    return perc

def zipSize(infile):
    size = 0
    with ZipFile(infile) as zip:
        size = sum([info.file_size for info in zip.infolist() if not info.is_dir()])
    return size

def help():
    print(MSG, end='')


if __name__ == '__main__':

    try:

        if len(argv) < 4 or len(argv) > 8 or len(argv) == 6:
            help()
            exit()

        operation = argv[1]
        encoding = getEnc(argv[2])
        infile = Path(argv[3])
        password = None
        pwdencode = None
        if len(argv) == 8:
             pwdencode = getEnc(argv[7])
             password = argv[6].encode(pwdencode)

        # list zip file
        if operation == 'l':
            enclszip(infile, encoding)

        elif operation == 'e':
            if len(argv) != 5 and len(argv) != 8: raise Exception("Please supply a output directory")
            outpath = Path(argv[4])
            if not outpath.exists(): outpath.mkdir()
            encunzipe(infile, encoding, outpath, password)

        # unzip to a folder with original file structure
        elif operation == 'x':
            if len(argv) != 5 and len(argv) != 8: raise Exception("Please supply a output directory")
            outpath = Path(argv[4])
            if not outpath.exists(): outpath.mkdir()
            encunzipx(infile, encoding, outpath, password)

        else:
            help()

    except KeyboardInterrupt:
        print()
        exit(-1)

