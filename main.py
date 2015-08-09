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

import os, pwd, re, subprocess
from os import chdir, getcwd
from os.path import abspath, isdir

## cd function
def updatecwd(path):
    if isdir(path):
        chdir(path)

## path formatters
def fmtpath(path):
    if os.environ["HOME"]:
        path = path.replace(os.environ["HOME"], "~")
    return path
def unfmtpath(path):
    if os.environ["HOME"]:
        path = path.replace("~", os.environ["HOME"])
    return abspath(path)

## system information
user = pwd.getpwuid(os.getuid()).pw_name
hostname = os.uname().nodename

history = []
running = True

## main loop
while running:
    cwd = getcwd()
    
    cmdline = input("{0}({1}):{2}/ ".format(user, hostname, fmtpath(cwd)))
    history.append(cmdline)

    ## environment variable substitution
    cmdvars = re.findall("\$\w+", cmdline)
    for var in cmdvars:
        cmdline = cmdline.replace(var, os.environ[var.strip("$")])    
    
    cmd = cmdline.split()
    if len(cmd) < 1: cmd = [""]

    ## inbuilt functions
    
    ## exit: exits pysh
    if cmd[0] == "exit":
        running = False
        continue
        
    ## cd: change current working directory
    elif cmd[0] == "cd":
        updatecwd(unfmtpath(cmd[1]))
    ## export: set environment variables
    elif cmd[0] == "export":
        if "=" in cmd[1]:
            var, value = cmd[1].split("=", 1)
            os.environ[var] = value
    ## printenv: print environment variables
    elif cmd[0] == "printenv":
        for var, value in os.environ.items():
            print("{0}={1}".format(var, value))
    ## history: shows command history from this session
    elif cmd[0] == "history":
        for index, line in enumerate(history):
            print(index + 1, line)
            
    ## TODO: implement
    ## jobs: shows background tasks
    elif cmd[0] == "jobs":
        pass
    ## kill: kills a background task or process
    elif cmd[0] == "kill":
        pass

    ## not an inbuilt fuction, send to system
    else:
        subprocess.call(cmd)
