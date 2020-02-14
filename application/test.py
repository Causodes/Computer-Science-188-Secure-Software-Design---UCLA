import os
from asynproc import Process
myProc = Process("helloworld.py")
while True:
    # check to see if process has ended
    poll = myProc.wait(os.WNOHANG)
    if poll != None:
        break
    # print any new output
    out = myProc.read()
    if out != "":
        print(out)