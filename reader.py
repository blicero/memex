#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-07-31 18:08:24 krylon>
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
from datetime import datetime
from queue import Queue
from threading import Thread
from typing import Final, List, Optional

# import pytesseract  # type: ignore
# from PIL import Image  # type: ignore
import tesserocr  # type: ignore

from memex import common, database, image

CPU_COUNT: Final[Optional[int]] = os.cpu_count()


# pylint: disable-msg=R0903
class Reader:
    """Reader extracts text from image files,

    using the Tesseract OCR engine.
    """

    log: logging.Logger
    workers: List[Thread]
    file_queue: Queue[str]
    result_queue: Queue[image.Image]

    def __init__(self, queue: Queue[str], worker_cnt=CPU_COUNT) -> None:
        self.log = common.get_logger("reader")
        self.file_queue = queue
        self.workers = []
        self.result_queue = Queue()

        self.log.debug("Starting %d worker threads", worker_cnt)

        res_handler = Thread(target=self.__result_handler)
        res_handler.daemon = True
        res_handler.start()

        for i in range(worker_cnt):
            worker: Thread = Thread(target=self.__worker, args=(i, ))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

    def __worker(self, worker_id: int) -> None:
        """Process image files as they arrive at the queue."""
        self.log.debug("Worker %02d starting up", worker_id)
        while True:
            try:
                path: str = self.file_queue.get()
                # self.log.debug("Worker %02d: Got one file from queue: %s",
                #                worker_id,
                #                path)
                content: str = self.read_image(path)
                img = image.Image(0, path, content, "", datetime.now())
                self.result_queue.put(img)
            except Exception as e:  # pylint: disable-msg=W0718,C0103
                self.log.error("Failed to process image %s: %s",
                               path,
                               e)

    def __result_handler(self) -> None:
        """Store processed images into the database."""
        self.log.debug("Result handler starting up.")
        db: database.Database \
            = database.Database(common.path.db())  # pylint: disable-msg=C0103
        while True:
            with db:
                try:
                    img: image.Image = self.result_queue.get()
                    db.file_add(img.path, img.content, img.comment, img.timestamp)  # noqa: E501
                except Exception as ex:  # pylint: disable-msg=W0718
                    self.log.error("Error processing image %s: %s",
                                   img.path,
                                   ex)

    def read_image(self, path: str) -> str:
        """Extract text from an image file and return it as a string."""
        self.log.debug("Process image %s", path)
        try:
            # return pytesseract.image_to_string(Image.open(path))
            return tesserocr.file_to_text(path)  # pylint: disable-msg=I1101,E1101
        except Exception as ex:
            self.log.error("Error processing %s: %s", path, ex)
            raise

# Local Variables: #
# python-indent: 4 #
# End: #
