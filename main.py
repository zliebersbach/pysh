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
## main.py
##
## PySH entry point.

import os, pwd
from argparse import ArgumentParser as argumentparser
from os import getcwd

import pysh.core as core
from pysh.parser import parser

argparser = argumentparser(description="a shell made in Python, prioritizing speed and efficiency.")
argparser.add_argument("-c", help="command to run in the shell")
args = argparser.parse_args()

# if command argument exists run it
if args.c:
    core.runcmd(parser.parse(args.c))
    core.end(0)
# else start interactive shell
else:
    ## system information
    user = pwd.getpwuid(os.getuid()).pw_name
    hostname = os.uname().nodename

    ## main loop
    while True:
        cwd = getcwd()
        try:
            cmdline = parser.parse(input("{0}({1}):{2}/ ".format(user, hostname, cwd)))
        except EOFError:
            core.end(0)
        except KeyboardInterrupt:
            core.newline()
            continue
        ## run command
        core.runcmd(cmdline)
