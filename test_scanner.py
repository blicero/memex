#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2023-10-29 16:59:55 krylon>
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
memex.test_scanner

(c) 2023 Benjamin Walkenhorst
"""

import os
import os.path
import random
import unittest

from queue import Queue
from typing import Final, List

from memex import scanner

SUFFICES: Final[List[str]] = [
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

TMP_FOLDER: Final[str] = '/data/ram'

fqueue: Queue = Queue()
myScanner: scanner.Scanner


def generate_directory_tree(root: str, depth: int = 2, num: int = 5) -> int:
    """Generate  directory tree to test our scanner.
    Return the number of files created"""
    if depth < 1:
        return 0

    num_files: int = 0

    try:
        os.makedirs(root, 0o777, True)
        for i in range(num):
            folder = os.path.join(root, f"testfolder{i+1:02d}")
            os.mkdir(folder, 0o777)
            num_files += generate_directory_tree(folder, depth - 1, num)
            for file_idx in range(num*num):
                suffix: str = random.choice(SUFFICES)
                filename: str = f"testfile{file_idx+1:03d}.{suffix}"
                fullpath: str = os.path.join(folder, filename)
                with open(fullpath, "w"):  # pylint: disable-msg=W1514
                    num_files += 1
    except:  # noqa: E722,B001
        pass
    else:
        os.system(f'rm -rf "{root}"')

    return num_files


class ScannerTest(unittest.TestCase):
    """Test the directory scanner. Duh"""

    myScanner: scanner.Scanner
    fcnt: int
    root: str

    @classmethod
    def setUpClass(cls) -> None:
        folder: str = f'memex_test_scanner_{random.randint(0, 1<<32):08x}'
        cls.root = os.path.join(TMP_FOLDER, folder)
        cls.fcnt = generate_directory_tree(cls.root)

    @classmethod
    def tearDownClass(cls):
        os.system(f'rm -rf "{cls.root}"')

    def test_create(self) -> None:
        """Test creating a Scanner instance."""
        try:
            self.__class__.myScanner = scanner.Scanner(fqueue)
        except Exception as e:  # pylint: disable-msg=W0718,C0103
            self.fail(e)

    def test_walk(self) -> None:
        """Test walking a single directory tree."""
        try:
            self.__class__.myScanner.walk_dir(self.__class__.root)
        except Exception as e:  # pylint: disable-msg=W0718,C0103
            self.fail(e)
        else:
            self.assertLessEqual(fqueue.qsize(), self.__class__.fcnt)

# Local Variables: #
# python-indent: 4 #
# End: #
