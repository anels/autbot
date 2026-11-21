#!/usr/bin/python
from subprocess import Popen
import sys
import time

cmd = sys.argv[1]
while True:
    print(f"Starting {cmd}\n")
    p = Popen([sys.executable, cmd])
    p.wait()
    if p.returncode != 0:
        print(f"{cmd} exited with code {p.returncode}; restarting in 30s\n")
        time.sleep(30)
