#!/usr/bin/python
from subprocess import Popen
import shlex
import sys
import time

cmd = sys.argv[1]
while True:
    print(f"Starting {cmd}\n")
    # cmd is the full command string (README usage:
    # main_runner.py "autbot.py -a ... -c ...");
    # shlex.split handles both that and a bare script name.
    p = Popen([sys.executable, *shlex.split(cmd)])
    p.wait()
    # Sleep unconditionally: a clean exit 0 (e.g. the weekend break in
    # autbot.py) must not spin-restart the bot every second all weekend.
    print(f"{cmd} exited with code {p.returncode}; restarting in 30s\n")
    time.sleep(30)
