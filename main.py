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

import getpass, locale, platform, sys
from argparse import ArgumentParser
from os import getcwd

from pysh.builtins import *
from pysh.core import Command, Shell, shrinkuser

locale.setlocale(locale.LC_ALL, "")

argparser = ArgumentParser(description="a shell made in Python, prioritizing speed and efficiency.")
argparser.add_argument("-c", help="command to run in the shell")
args = argparser.parse_args()

## if command argument exists run it
if args.c:
    shell = Shell()
    shell.runcmd(parser.parse(args.c).split())
    shell.end(0)
## else start interactive shell
else:
    shell = Shell()
    user = getpass.getuser()
    platid = platform.dist()[2].lower().replace(" ", "-")
    if user == "root":
        usersym = "#"
    else:
        usersym = "$"

    ## initialize readline module
    import readline
    open(PYSH_HISTFILE, "a").close()
    readline.read_history_file(PYSH_HISTFILE)
    readline.parse_and_bind("tab: complete")

    ## main loop
    while True:
        cwd = shrinkuser(getcwd())

        try:
            cmd = shell.input("{0}({1}){3}:{2}/ ".format(user, platid, cwd, usersym))
        except EOFError:
            shell.end(0, exception=False)
            shell.newline()
            break
        except KeyboardInterrupt:
            shell.newline()
            continue

        ## run command
        try:
            shell.runcmd(cmd)
        except ShellEndedError:
            break
        except Exception as e:
            shell.print(str(e) + "\n")

    readline.write_history_file(PYSH_HISTFILE)
