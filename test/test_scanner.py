#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2023-09-30 22:17:51 krylon>
#
# /data/code/python/memex/test/test_scanner.py
# created on 30. 09. 2023
# (c) 2023 Benjamin Walkenhorst
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY BENJAMIN WALKENHORST ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""
memex.test.test_scanner

(c) 2023 Benjamin Walkenhorst
"""

import os
import os.path
import random
import unittest

from typing import Final


suffices: Final[list[str]] = [
    'jpg',
    'jpeg',
    'png',
    'gif',
    'txt',
    'mp4',
    'odt',
    'opus',
    'flac',
    'dll'
    'docx',
    'xlsx',
    'json',
    'el',
]

FFLAGS: Final[int] = os.O_RDWR | os.O_CREAT


def generate_directory_tree(root: str, depth: int = 3, num: int = 100) -> None:
    """Generate  directory tree to test our scanner"""
    if depth == 0:
        return

    try:
        os.mkdir(root)
        for i in range(num):
            folder = os.path.join(root, f"testfolder{i+1:02d}")
            os.mkdir(folder)
            generate_directory_tree(folder, depth - 1, num)
            for f in range(num*num):
                suffix: Final[str] = random.choice(suffices)
                filename: Final[str] = f"testfile{f+1:03d}.{suffix}"
                fullpath: Final[str] = os.path.join(folder, filename)
                with os.open(fullpath, FFLAGS):
                    pass
    except:  # noqa: E722
        os.system(f'rm -rf "{root}"')


class ScannerTest(unittest.TestCase):
    """Test the directory scanner. Duh"""

    pass

# Local Variables: #
# python-indent: 4 #
# End: #
