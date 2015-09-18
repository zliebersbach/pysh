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

class Command(list):
    def __init__(self, *args):
        if len(args) < 1:
            raise IndexError("command must have a length of at least 1")
        if (len(args) == 1) and (" " in args[0]):
            super().__init__(args[0].split())
        elif len(args) == 1:
            super().__init__([args[0]])
        else:
            super().__init__(args)

    def __str__(self):
        return " ".join(self)

    @property
    def cmd(self):
        return self[0]
    @property
    def args(self):
        return self[1:]
    @property
    def argcount(self):
        return len(self[1:])
    
class Job(Thread):
    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd
        self.daemon = True
        self.name = "Job-" + "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.stdout = []
        
    def readlines(self):
        return self.stdout

    def run(self):
        tmpfile = TemporaryFile()
        shell = Shell(stdout=tmpfile)
        try:
            shell.runcmd(self.cmd)
            shell.end(0, exception=False)
        except Exception as e:
            shell.print(str(e) + "\n")
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

    def runcmd(self, cmd):
        if not isinstance(cmd, Command):
            raise TypeError("command must be of type Command")
        if len(cmd) == 0:
            return

        if cmd[-1] == "&":
            job = Job(Command(*cmd[:-1]))
            job.start()
            self.jobs.append(job)
            return
        
        ## inbuilt functions
        
        ## exit: ends pysh
        if cmd.cmd == "exit":
            self.end(0)

        ## cd: change current working directory
        elif cmd.cmd == "cd":
            if cmd.argcount != 1:
                raise ArgumentCountError(cmd.argcount, 1)
            self.cd(cmd.args[0])
            
        ## export: set environment variables
        elif cmd.cmd == "export":
            if cmd.argcount != 1:
                raise ArgumentCountError(cmd.argcount, 1)
            if "=" in cmd.args[0]:
                var, val = cmd.args[0].split("=", 1)
                self.setenv(var, val)
            else:
                raise ArgumentError("expected '=' in argument", 0)
            
        ## setenv: set environment variables in the form of "export var val"
        elif cmd.cmd == "setenv":
            if cmd.argcount != 2:
                raise ArgumentCountError(cmd.argcount, 2)
            self.setenv(cmd.args[0], cmd.args[1])
            
        ## printenv: print environment variables
        elif cmd.cmd == "printenv":
            if cmd.argcount != 0:
                raise ArgumentCountError(cmd.argcount, 0)
            self.printenv()

        ## history: shows command history from this session
        elif cmd.cmd == "history":
            if cmd.argcount != 0:
                raise ArgumentCountError(cmd.argcount, 0)
            self.showhist()
                
        ## !: runs previous command by index, visible through history
        elif cmd.cmd.startswith("!"):
            if cmd.argcount != 0:
                raise ArgumentCountError(cmd.argcount, 0)
            histcmd = cmd.cmd[1:]
            if len(histcmd) > 0:
                try:
                    histindex = int(histcmd)
                    if histindex > 0:
                        histindex -= 1
                    elif histindex < 0:
                        histindex += readline.get_current_history_length() - 1
                    selectcmd = readline.get_history_item(histindex)
                    readline.add_history(selectcmd)
                    self.runcmd(Command(selectcmd))
                except ValueError:
                    if histcmd == "!":
                        selectcmd = readline.get_history_item(readline.get_current_history_length() - 1)
                        readline.add_history(selectcmd)
                        self.runcmd(Command(selectcmd))
                    elif histcmd == "-":
                        self.clearhist()
            else:
                raise ArgumentError("expected character after '!'")

        ## jobs: shows background tasks
        elif cmd.cmd == "jobs":
            if cmd.argcount != 0:
                raise ArgumentCountError(cmd.argcount, 0)
            self.showjobs()
        ## job: shows the output of a background task
        elif cmd.cmd == "job":
            if cmd.argcount != 1:
                raise ArgumentCountError(cmd.argcount, 1)
            if not cmd.args[0].startswith("j"):
                raise ArgumentError("expected job identifier but found \"{0}\"".format(cmd.args[0]))
            self.outputjob(int(cmd.args[0][1:]))

        ## kill: kills a background task or process
        elif cmd.cmd == "kill":
            if cmd.argcount != 1:
                raise ArgumentCountError(cmd.argcount, 1)
            if cmd.args[0].startswith("j"):
                self.killjob(int(cmd.args[0][1:]))
            else:
                self.killproc(int(cmd.args[0]))

        ## not an inbuilt fuction, send to system
        else:
            subprocess.call(cmd, stdout=self.stdout, stdin=self.stdin)

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
        try:
            self.stdout.write(obj.encode("utf-8"))
        except Exception:
            self.stdout.write(str(obj))
    ## read text from stdin
    def input(self, string):
        return Command(parser.parse(input(string)))
