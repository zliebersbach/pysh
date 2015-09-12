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

import os, random, readline, signal, string, subprocess, sys
from os import chdir, environ
from os.path import exists, isdir
from tempfile import TemporaryFile
from threading import Thread

from pysh.builtins import *
from pysh.parser import parser

def shrinkuser(path):
    if "HOME" in environ:
        return path.replace(environ["HOME"], "~", 1)
    return path
def strtocmd(string):
    return string.split()
def cmdtostr(cmd):
    return " ".join(cmd)

class Job(Thread):
    def __init__(self, cmdline):
        super().__init__()
        self.cmdline = cmdline
        self.daemon = True
        self.name = "Job-" + "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.stdout = []

    def __str__(self):
        return "[{0} {1}] {2}".format(self.name, "running" if self.is_alive() else "ended", cmdtostr(self.cmdline))

    def readlines(self):
        return self.stdout

    def run(self):
        tmpfile = TemporaryFile()
        shell = Shell(stdout=tmpfile)
        try:
            shell.runcmd(self.cmdline[:])
            shell.end(0, exception=False)
        except Exception as e:
            shell.print(str(e).strip("\n") + "\n")
        tmpfile.seek(0)
        self.stdout = [x.decode("utf-8") for x in tmpfile.readlines()]
        tmpfile.close()

class Shell:
    def __init__(self, stdout=sys.stdout, stdin=sys.stdin):
        self.jobs = []
        self.stdout = stdout
        self.stdin = stdin

    def newline(self):
        self.print("\n")

    def end(self, status, exception=True):
        if status > 0:
            self.newline()
        for job in self.jobs:
            job.join()
        if exception:
            raise ShellEndedError(status)
        
    def cd(self, directory):
        if not exists(directory):
            raise FileNotFoundError("{0}: no such file or directory".format(directory))
        if isdir(directory):
            chdir(directory)
        else:
            raise NotADirectoryError("{0}: not a directory".format(directory))

    def printenv(self):
        for var, value in environ.items():
            self.print("{0} = {1}\n".format(var, value))
    def setenv(self, var, val):
        environ[var] = val

    def runcmd(self, cmdline):
        if not isinstance(cmdline, list):
            raise TypeError("command must be of type list")
        if len(cmdline) == 0:
            return

        if cmdline[-1] == "&":
            job = Job(cmdline[:-1])
            job.start()
            self.jobs.append(job)
            return

        cmd = cmdline.pop(0)
        args = cmdline[:]
        argcount = len(args)
        
        ## inbuilt functions
        
        ## exit: ends pysh
        if cmd == "exit":
            self.end(0)

        ## cd: change current working directory
        elif cmd == "cd":
            if argcount != 1:
                raise ArgumentCountError(argcount, 1)
            self.cd(args[0])
            
        ## export: set environment variables
        elif cmd == "export":
            if argcount != 1:
                raise ArgumentCountError(argcount, 1)
            if "=" in args[0]:
                var, val = args[0].split("=", 1)
                self.setenv(var, val)
            else:
                raise ArgumentError("expected '=' in argument", 0)
            
        ## setenv: set environment variables in the form of "export var val"
        elif cmd == "setenv":
            if argcount != 2:
                raise ArgumentCountError(argcount, 2)
            self.setenv(args[0], args[1])
            
        ## printenv: print environment variables
        elif cmd == "printenv":
            if argcount != 0:
                raise ArgumentCountError(argcount, 0)
            self.printenv()

        ## history: shows command history from this session
        elif cmd == "history":
            if argcount != 0:
                raise ArgumentCountError(argcount, 0)
            self.showhist()
                
        ## !: runs previous command by index, visible through history
        elif cmd.startswith("!"):
            if argcount != 0:
                raise ArgumentCountError(argcount, 0)
            histcmd = cmd[1:]
            if len(histcmd) > 0:
                try:
                    histindex = int(histcmd)
                    if histindex > 0:
                        histindex -= 1
                    elif histindex < 0:
                        histindex += readline.get_current_history_length() - 1
                    selectcmd = readline.get_history_item(histindex)
                    readline.add_history(selectcmd)
                    self.runcmd(strtocmd(selectcmd))
                except ValueError:
                    if histcmd == "!":
                        selectcmd = readline.get_history_item(readline.get_current_history_length() - 1)
                        readline.add_history(selectcmd)
                        self.runcmd(strtocmd(selectcmd))
                    elif histcmd == "-":
                        self.clearhist()
            else:
                raise ArgumentError("expected character after '!'")

        ## jobs: shows background tasks
        elif cmd == "jobs":
            if argcount != 0:
                raise ArgumentCountError(argcount, 0)
            self.showjobs()
        ## job: shows the output of a background task
        elif cmd == "job":
            if argcount != 1:
                raise ArgumentCountError(argcount, 1)
            if not args[0].startswith("j"):
                raise ArgumentError("expected job identifier but found \"{0}\"".format(args[0]))
            self.outputjob(int(args[0][1:]))

        ## kill: kills a background task or process
        elif cmd == "kill":
            if argcount != 1:
                raise ArgumentCountError(argcount, 1)
            if args[0].startswith("j"):
                self.killjob(int(args[0][1:]))
            else:
                self.killproc(int(args[0]))

        ## not an inbuilt fuction, send to system
        else:
            subprocess.call([cmd] + args, stdout=self.stdout, stdin=self.stdin)

    def clearhist(self):
        readline.clear_history()
    def showhist(self):
        for i in range(readline.get_current_history_length() - 1):
            self.print("({0}) {1}\n".format(i + 1, readline.get_history_item(i)))

    def killjob(self, ident):
        self.jobs.pop(ident - 1).join()
    def killproc(self, ident):
        os.kill(ident, signal.SIGKILL)
    def outputjob(self, ident):
        self.print("".join(self.jobs[ident - 1].readlines()))
    def showjobs(self):
        for ident, job in enumerate(self.jobs):
            self.print("({0}) {1}\n".format(ident + 1, str(job)))

    ## write text to stdout
    def print(self, obj):
        if isinstance(obj, bytes):
            objparse = obj.decode("utf-8")
        else:
            objparse = str(obj)
        self.stdout.write(objparse)
    ## read text from stdin
    def input(self, string):
        return parser.parse(input(string))
