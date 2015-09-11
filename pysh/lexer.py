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
## lexer.py
##
## Tokenizing of PySH commands.

from os.path import expanduser, expandvars

import ply.lex as lex

tokens = (
    "COMMAND",
    "COMMENT",
    "FILENAME",
    "HISTCMD",
    "JOBIDENT",
    "NUMBER",
    "OPTIONS",
    "PATHNAME",
    "VAR",
    "VARASSIGN"
)

t_COMMAND = r"[A-Za-z0-9_-]+"
t_FILENAME = r"\w+\.\w+"
t_HISTCMD = r"\!(?:\!|-?\d+|-)"
t_JOBIDENT = r"j\d+"
t_NUMBER = r"\d+"
t_OPTIONS = r"-{1,2}\w+"
t_VARASSIGN = r"\w+=\w+"

def t_PATHNAME(t):
    r"(?:\~|\.{1,2})?(?:\/[A-Za-z0-9.\-_]*)+"
    t.value = expanduser(t.value)
    return t
def t_VAR(t):
    r"\$\w+"
    t.value = expandvars(t.value)
    return t

def t_error(t):
    print("error: cannot parse character \"{0}\"".format(t.value[0]))
    t.lexer.skip(1)

t_ignore = " \t\n"
t_ignore_COMMENT = r"\#.*"

lexer = lex.lex()
