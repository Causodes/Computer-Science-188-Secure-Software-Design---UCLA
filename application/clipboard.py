from threading import Thread, Event, Timer
from subprocess import Popen, PIPE
import time
import pyperclip
import time
import os

def TimerReset(*args, **kwargs):
    """ Global function for Timer """
    return _TimerReset(*args, **kwargs)


class _TimerReset(Thread):
    """Call a function after a specified number of seconds:

    t = TimerReset(30.0, f, args=[], kwargs={})
    t.start()
    t.cancel() # stop the timer's action if it's still waiting
    """

    def __init__(self, interval, function, args=[], kwargs={}):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()
        self.resetted = True

    def cancel(self):
        """Stop the timer if it hasn't finished yet"""
        self.finished.set()

    def run(self):
        print("Time: %s - timer running..." % time.asctime())

        while self.resetted:
            print("Time: %s - timer waiting for timeout in %.2f..." % (time.asctime(), self.interval))
            self.resetted = False
            self.finished.wait(self.interval)

        if not self.finished.isSet():
            self.function(*self.args, **self.kwargs)
        self.finished.set()
        print("Time: %s - timer finished!" % time.asctime())

    def reset(self, interval=None):
        """ Reset the timer """

        if interval:
            print("Time: %s - timer resetting to %.2f..." % (time.asctime(), interval))
            self.interval = interval
        else:
            print("Time: %s - timer resetting..." % time.asctime())

        self.resetted = True
        self.finished.set()
        self.finished.clear()

def password_paster(password):
    pyperclip.copy(password)
    pyperclip.paste()
    
def clear_clipboard():
    pyperclip.copy("")
    pyperclip.paste()

myProc = Process("helloworld.py")
while True:
    tim = TimerReset(30, clear_clipboard)
    poll = myProc.wait(os.WNOHANG)
    if poll is not None:
        break
    out = myProc.read()
    if out != "":
        password_paster(out)
        tim.reset()

"""  
# With reset interval
print("Time: %s - start..." % time.asctime())
tim = TimerReset(5, hello)
tim.start()
print("Time: %s - sleeping for 4..." % time.asctime())
time.sleep (4)
tim.reset (9)
print("Time: %s - sleeping for 10..." % time.asctime())
time.sleep (10)
print("Time: %s - end..." % time.asctime())
"""