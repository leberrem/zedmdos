#!/usr/bin/env python3

import subprocess
import traceback
import datetime
import os
import glob
import json
import re
import random

# images_root = "/boot/configs/images"
# dmd_play    = "dmd-play"
# font        = "/boot/configs/SpaceMono-Bold.ttf"

images_root  = "../../animation"
dmd_play     = "../../dmd-simulator/dmd-play.py"
font         = "SpaceMono-Bold.ttf"

clock_format = " %H:%M:%S "

files = glob.glob(images_root + '/*.gif')
while True:
    try:
        p = subprocess.Popen([dmd_play, "--once", "--file", random.choice(files)])
        p.wait()
        p = subprocess.Popen([dmd_play, "--clock", "--red", "238", "--green", "102", "--blue", "32", "--clock-format", clock_format, "--font", font])
        p.wait(4)
    except subprocess.TimeoutExpired as e:
        p.kill()
