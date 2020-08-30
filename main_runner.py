#!/usr/bin/python
from subprocess import Popen
import sys

cmd = sys.argv[1]
while True:
    print(f"Starting {cmd}\n")
    p = Popen("python " + cmd, shell=True)
    p.wait()
