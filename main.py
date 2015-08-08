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

history = []
running = True

## main loop
while running:
    cmdline = input()
    history.append(cmdline)
    cmd = cmdline.split()

    ## inbuilt functions
    
    ## exit: exits pysh
    if cmd[0] == "exit":
        running = False
        
    ## cd: change current working directory
    elif cmd[0] == "cd":
        cwd = cmd[1]
        
    ## history: shows command history from this session
    elif cmd[0] == "history":
        for index, line in enumerate(history):
            print(index, line)
            
    ## jobs: shows background tasks
    ## TODO: Implement
    elif cmd[0] == "jobs":
        pass
    ## kill: kills a background task or process
    ## TODO: Implement
    elif cmd[0] == "kill":
        pass

    ## not an inbuilt fuction
    else:
        pass
