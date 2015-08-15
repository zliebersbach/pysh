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

import os, pwd, re, subprocess, sys
from argparse import ArgumentParser as argparser
from os import chdir, getcwd
from os.path import abspath, isdir

## function to end pysh
def end(status):
    sys.exit(status)

## TODO: -c on command line for non interactive
## setup vars for interactive session
history = []

## cd function
def updatecwd(path):
    if isdir(path):
        chdir(path)
    else:
        print("{0}: no such file or directory".format(path))

## path formatters
def fmtpath(path):
    if "HOME" in os.environ:
        path = path.replace(os.environ["HOME"], "~")
    return path
def unfmtpath(path):
    if "HOME" in os.environ:
        path = path.replace("~", os.environ["HOME"])
    return abspath(path)
## environment variable substituter
def subenvvars(string):
    strvars = re.findall(r"\$\w+", string)
    for var in strvars:
        try:
            string = string.replace(var, os.environ[var.strip("$")])
        except KeyError:
            continue
    return string

## history management
def addtohist(cmd):
    if type(cmd) == list:
        history.append(" ".join(cmd))
    elif type(cmd) == str:
        history.append(cmd)
    else:
        raise TypeError("command must be array or string")
def clearhist():
    history = []

## run command
def runcmd(cmdline):
    ## substitute environment variables
    cmdline = subenvvars(cmdline)

    ## create cmd array and check if any input
    cmd = cmdline.split()
    if len(cmd) < 1: return
    if cmd[0] == "": return
    
    ## inbuilt functions
    
    ## exit: ends pysh
    if cmd[0] == "exit":
        end(0)

    ## cd: change current working directory
    elif cmd[0] == "cd":
        updatecwd(unfmtpath(cmd[1]))
    ## export: set environment variables
    elif cmd[0] == "export" or cmd[0] == "setenv":
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

## argument parsing
parser = argparser(description = "A shell made in Python, prioritizing speed and efficiency.")

## system information
user = pwd.getpwuid(os.getuid()).pw_name
hostname = os.uname().nodename

## main loop
while True:
    ## update current working directory
    cwd = getcwd()

    ## get user input or command
    try:
        cmdline = input("{0}({1}):{2}/ ".format(user, hostname, fmtpath(cwd)))
    ## clean exit on ctrl-d
    except EOFError and KeyboardInterrupt:
        sys.stdout.write("\n")
        end(0)

    ## run command and add to history
    runcmd(cmdline)
    addtohist(cmdline)
