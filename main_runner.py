#!/usr/bin/python
from subprocess import Popen
import sys

cmd = sys.argv[1]
while True:
    print("Starting {}\n".format(cmd))
    p = Popen("python " + cmd, shell=True)
    p.wait()
