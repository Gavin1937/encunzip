#!/usr/bin/env python3

MSG = """

INFO
       Author      - Gavin1937
       Github      - https://github.com/Gavin1937/encunzip
       encunzip.py - simple script to list & extract zip/rar file with encodings.

SYNOPSIS
       python3 encunzip.py OPERATION ENCODING file.zip OUTPUTDIR OPERATION ARG

       you can set encunzip.py to an executable file and use:
       ./encunzip.py OPERATION ENCODING file.zip OUTPUTDIR

DESCRIPTION
       Unzip zip file with non utf-8 encodings.
       This tool is aiming to simplify command "unzip -O encoding" with a small ENCODING TABLE contians commonly used encodings.

REQUIREMENTS
       * rarfile >= 4.0

       install with `pip install -r requirements.txt`

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

OPTIONAL ARGUMENTS

           -noencerr        Ignore encoding & decoding error during operation

EXAMPLES:

           Listing contents in "file.zip" with jp(cp932) encoding.
               python3 encunzip.py l jp file.zip

           Extract contents in "file.zip" to directory "output" with utf-8 encoding without file structure.
               python3 encunzip.py e utf-8 file.zip output

           Extract contents in "file.zip" to directory "output" with chinese_1(gb18030) encoding keeping file structure.
               python3 encunzip.py x chinese file.zip output

           Extract contents in "file.zip" with password "1234" with chinese_1
               python3 encunzip.py e jp file.zip output p 1234 ch1

           Extract contents in "file.zip" with password "1234" with chinese_1 ignoring any encoding & decoding error
               python3 encunzip.py e jp file.zip output p 1234 ch1 -noencerr

"""

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

FILEHEADERS = {
    b'PK\x03\x04' : 'zip', # zip
    b'PK\x05\x06' : 'zip', # zip_empty
    b'PK\x07\x08' : 'zip', # zip_spanned
    b'\x52\x61\x72\x21\x1A\x07\x00' : 'rar', # rar_1_4
    b'\x52\x61\x72\x21\x1A\x07\x01\x00' : 'rar', # rar_5
}


def loadarchive(infile):
    
    def read_file_chunk(fd, chunk_size=1024):
        'lazy reading a file'
        while True:
            data = fd.read(chunk_size)
            if not data:
                break
            yield data
    
    libname = None
    with open(infile, 'rb') as file:
        exit_loop = False
        for chunk in read_file_chunk(file):
            for header,name in FILEHEADERS.items():
                if header in chunk:
                    libname = name
                    exit_loop = True
                    break
            if exit_loop:
                break
    if libname is None:
        raise Exception('Failed to load archive, file header check failed.')
    
    # load necessary library
    try:
        if libname == 'zip':
            from zipfile import ZipFile
            return ZipFile
        elif libname == 'rar':
            from rarfile import RarFile
            return RarFile
    except Exception as err:
        print(f'Failed to load library. {err}')

# list zip file content
# unzip -l
def enclszip(infile, encoding, ignore_encode_err=False):
    
    # setup/check input & output
    infile = Path(infile)
    if not infile.exists():
        raise Exception(f"Cannot find input file: {infile}")
    
    # unzip file
    archive = loadarchive(infile)
    with archive(infile) as zip:
        for info in zip.infolist():
            try:
                item = info.filename.encode('cp437').decode(encoding)
            except (UnicodeDecodeError, UnicodeEncodeError):
                if not ignore_encode_err:
                    raise
                item = info.filename
            print(item)

# unzip without file structure
# unzip -e
def encunzipe(infile, encoding, outfile, pwd=None, ignore_encode_err=False):
    
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
    archive = loadarchive(infile)
    with archive(infile) as zip:
        for info in zip.infolist():
            filename = info.filename
            try:
                outitem = outfile/filename[filename.rfind('/')+1:].encode('cp437').decode(encoding)
            except (UnicodeDecodeError, UnicodeEncodeError):
                if not ignore_encode_err:
                    raise
                outitem = outfile/filename[filename.rfind('/')+1:]
            current_size += info.file_size
            print(genPerc(current_size, size), outitem)
            if not info.is_dir(): # is file
                source = zip.open(filename, pwd=pwd)
                target = open(outitem, "wb")
                with source, target:
                    copyfileobj(source, target)

# unzip keeping file structure
# unzip -x
def encunzipx(infile, encoding, outfile, pwd=None, ignore_encode_err=False):
    
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
    archive = loadarchive(infile)
    with archive(infile) as zip:
        for info in zip.infolist():
            filename = info.filename
            try:
                outitem = outfile/filename.encode('cp437').decode(encoding)
            except (UnicodeDecodeError, UnicodeEncodeError):
                if not ignore_encode_err:
                    raise
                outitem = outfile/filename
            outitem.parent.mkdir(parents=True, exist_ok=True)
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
    archive = loadarchive(infile)
    with archive(infile) as zip:
        size = sum([info.file_size for info in zip.infolist() if not info.is_dir()])
    return size

def help():
    print(MSG, end='')


if __name__ == '__main__':
    
    try:
        
        if len(argv) < 4:
            help()
            exit()
        
        
        argv_len = len(argv)
        cursor = 1
        operation = argv[cursor]
        cursor += 1
        
        # list zip file
        if operation == 'l':
            encoding = getEnc(argv[cursor])
            cursor += 1
            infile = argv[cursor]
            cursor += 1
            ignore_encode_err = False
            if cursor < argv_len and argv[cursor] == '-noencerr':
                ignore_encode_err = True
            enclszip(infile, encoding, ignore_encode_err)
        
        elif operation == 'e':
            encoding = getEnc(argv[cursor])
            cursor += 1
            infile = argv[cursor]
            cursor += 1
            outpath = Path(argv[cursor])
            cursor += 1
            password = None
            if cursor < argv_len and argv[cursor] == 'p':
                pwdencode = getEnc(argv[cursor+2])
                password = argv[cursor+1].encode(pwdencode)
            if not outpath.exists(): outpath.mkdir()
            ignore_encode_err = False
            if cursor < argv_len and argv[cursor] == '-noencerr':
                ignore_encode_err = True
            encunzipe(infile, encoding, outpath, password, ignore_encode_err)
        
        # unzip to a folder with original file structure
        elif operation == 'x':
            encoding = getEnc(argv[cursor])
            cursor += 1
            infile = argv[cursor]
            cursor += 1
            outpath = Path(argv[cursor])
            cursor += 1
            password = None
            if cursor < argv_len and argv[cursor] == 'p':
                pwdencode = getEnc(argv[cursor+2])
                password = argv[cursor+1].encode(pwdencode)
            if not outpath.exists(): outpath.mkdir()
            ignore_encode_err = False
            if cursor < argv_len and argv[cursor] == '-noencerr':
                ignore_encode_err = True
            encunzipx(infile, encoding, outpath, password, ignore_encode_err)
        
        else:
            help()
        
    except KeyboardInterrupt:
        print()
        exit(-1)
    except IndexError:
        pass

