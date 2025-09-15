#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2011-2017, 2018 The Linux Foundation. All rights reserved.

# -*- coding: utf-8 -*-

import errno
import re
import os
import sys
import subprocess

allowed_warnings = {
    "umid.c:138",
    "umid.c:213",
    "umid.c:388",
}

ofile = None

warning_re = re.compile(r'''(.*/|)([^/]+\.[a-z]+:\d+):(\d+:)? warning:''')

def interpret_warning(line: str):
    """Decode the message from gcc.  The messages we care about have a filename, and a warning"""
    line = line.rstrip('\n')
    m = warning_re.match(line)
    if m and m.group(2) not in allowed_warnings:
        print("error, forbidden warning:", m.group(2))
        if ofile:
            try:
                os.remove(ofile)
            except OSError:
                pass
        sys.exit(1)

def run_gcc():
    global ofile
    args = sys.argv[1:]
    try:
        i = args.index('-o')
        ofile = args[i + 1]
    except (ValueError, IndexError):
        pass

    try:
        # text=True => stderr сразу строки, а не bytes
        proc = subprocess.Popen(args, stderr=subprocess.PIPE, text=True)
        for line in proc.stderr:
            print(line, end="")
            interpret_warning(line)

        result = proc.wait()
    except OSError as e:
        result = e.errno
        if result == errno.ENOENT:
            print(args[0] + ':', e.strerror)
            print('Is your PATH set correctly?')
        else:
            print(' '.join(args), str(e))

    return result

if __name__ == '__main__':
    status = run_gcc()
    sys.exit(status)
