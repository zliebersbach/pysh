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
## builtins.py
##
## Global objects and variables, including custom exceptions.

from os.path import expanduser

PYSH_HISTFILE = expanduser("~/.pysh-history")

class ArgumentError(Exception):
    def __init__(self, message, argnum):
        super().__init__("ArgumentError: " + message)
        self.argnum = argnum

class ArgumentCountError(Exception):
    def __init__(self, argcount, expargcount):
        self.argcount = argcount
        self.expargcount = expargcount
        super().__init__("ArgumentCountError: expected {0} arguments but found {1}".format(self.expargcount, self.argcount))

class ShellEndedError(Exception):
    def __init__(self, status):
        self.status = status
        super().__init__("ShellEndedError: shell instance ended with status {0}".format(self.status))
