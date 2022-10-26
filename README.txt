
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

