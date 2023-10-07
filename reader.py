#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2023-10-06 19:39:38 krylon>
#
# /data/code/python/memex/reader.py
# created on 04. 10. 2023
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
memex.reader

(c) 2023 Benjamin Walkenhorst

Attempts to extract text from image files.
"""

import logging
import os
from queue import Queue
from threading import Thread
from typing import List

import pytesseract  # type: ignore
from PIL import Image  # type: ignore

from memex import common


# pylint: disable-msg=R0903
class Reader:
    """Reader extracts text from image files,
    using the Tesseract OCR engine."""

    log: logging.Logger
    workers: List[Thread]
    file_queue: Queue

    def __init__(self, queue: Queue, worker_cnt=os.cpu_count()) -> None:
        self.log = common.get_logger("reader")
        self.file_queue = queue
        self.workers = []

        for i in range(worker_cnt):
            worker: Thread = Thread(target=self.__worker, args=(i, ))
            worker.daemon = True
            self.workers.append(worker)

    def __worker(self, worker_id: int) -> None:
        """Process image files as they arrive at the queue."""
        while True:
            path: str = self.file_queue.get()
            content: str = self.read_image(path)
            self.log.debug("""Worker%02d got text from %s:
            %s""", worker_id, path, content)

    def read_image(self, path: str) -> str:
        """Extract text from an image file and return it as a string."""
        self.log.debug("Process image %s", path)
        try:
            return pytesseract.image_to_string(Image.open(path))
        except Exception as ex:
            self.log.error("Error processing %s: %s", path, ex)
            raise

# Local Variables: #
# python-indent: 4 #
# End: #
