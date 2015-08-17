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
## core.py
##
## Core functions of the shell.

import subprocess, sys
from os import chdir, environ
from os.path import isdir

def newline():
    sys.stdout.write("\n")

# ends PySH
def end(status):
    newline()
    sys.exit(status)

def updatecwd(path):
    if isdir(path):
        chdir(path)
    else:
        print("{0}: no such file or directory".format(path))

history = []
def addtohist(cmd):
    if type(cmd) == list:
        history.append(" ".join(cmd))
    elif type(cmd) == str:
        history.append(cmd)
    else:
        raise TypeError("command must be array or string")
def clearhist():
    history = []

def runcmd(cmd):
    addtohist(cmd)
    
    # split command into tokens
    if type(cmd) == str:
        cmdline = cmd
        cmd = cmd.split()
    elif type(cmd) == list:
        cmdline = " ".join(cmd)
    else:
        raise TypeError("command must be array or string")
    
    ## inbuilt functions
    
    ## exit: ends pysh
    if cmd[0] == "exit":
        end(0)

    ## cd: change current working directory
    elif cmd[0] == "cd":
        updatecwd(cmd[1])
    ## export: set environment variables
    elif cmd[0] == "export" or cmd[0] == "setenv":
        if "=" in cmd[1]:
            var, value = cmd[1].split("=", 1)
            environ[var] = value
    ## printenv: print environment variables
    elif cmd[0] == "printenv":
        for var, value in environ.items():
            print("{0}={1}".format(var, value))

    ## history: shows command history from this session
    elif cmd[0] == "history":
        for index, line in enumerate(history):
            print("({0}) {1}".format(index + 1, line))
    ## !: runs previous command by index, e.g. !2
    elif cmd[0][0] == "!":
        histcmd = cmd[0][1:]
        if len(histcmd) > 0:
            try:
                histindex = int(histcmd)
                if histindex > 0:
                    histindex -= 1
                runcmd(history[histindex])
            except ValueError:
                if histcmd == "!":
                    runcmd(history[-1])
                elif histcmd == "-":
                    clearhist()

    ## TODO: implement
    ## jobs: shows background tasks
    elif cmd[0] == "jobs":
        pass
    ## kill: kills a background task or process
    elif cmd[0] == "kill":
        pass

    ## not an inbuilt fuction, send to system
    else:
        try:
            subprocess.call(cmd)
        except FileNotFoundError:
            print("{0}: command not found".format(cmd[0]))
            return
