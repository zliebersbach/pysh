#!/usr/bin/python3
## Copyright 2015 Kevin Boxhoorn
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##   http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## parser.py
##
## Parsing of PySH commands.

import ply.yacc as yacc
from pysh.lexer import tokens

def p_main(p):
    """main : command
            | empty
    """
    p[0] = p[1]

def p_empty(p):
    """empty : """
    p[0] = ""

def p_command(p):
    """command : command command
               | command JOB
               | command JOBIDENT
               | command NUMBER
               | command OPTIONS
               | command VARASSIGN
               | COMMAND
               | HISTCMD
               | FILENAME
               | PATHNAME
               | VAR
    """
    p[0] = " ".join(p[1:])

def p_error(p):
    print("error: encountered syntax error while parsing command")

parser = yacc.yacc()
