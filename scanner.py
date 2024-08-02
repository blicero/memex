#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-07-31 18:06:43 krylon>
#
# /data/code/python/memex/scanner.py
# created on 29. 09. 2023
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
memex.scanner

(c) 2023 Benjamin Walkenhorst

Scans directory trees for image files.
"""

import logging
import os
import os.path
import re
import stat
from datetime import datetime
from queue import Queue
from threading import Thread
from typing import Final, Optional

from memex import common, database

# pylint: disable-msg=C0103

_picPat: Final[re.Pattern[str]] = \
        re.compile("[.](?:jpe?g|png|webp|avif|gif)$", re.I)


def file_mtime(path: str) -> Optional[datetime]:
    """Return the file's mtime"""
    try:
        info = os.stat(path)
        mtime = info[stat.ST_MTIME]
        stamp = datetime.fromtimestamp(mtime)
        return stamp
    except FileNotFoundError:
        return None


class Scanner:
    """Scanner walks one or more directory trees, looking for image files"""

    __slots__ = ['logger', 'queue']

    logger: logging.Logger
    queue: Queue[str]

    def __init__(self, q: Queue[str]) -> None:
        self.logger = common.get_logger("scanner")
        self.queue = q

    # pylint: disable-msg=R1702
    def walk_dir(self, path: str) -> None:
        """Walk a single directory tree"""
        db: database.Database = database.Database(common.path.db())
        try:
            for folder, _, files in os.walk(path):
                try:
                    for f in files:
                        full_path: str = os.path.join(folder, f)
                        if _picPat.search(full_path):
                            scur = file_mtime(full_path)
                            sdb = db.file_timestamp(full_path)
                            if (sdb is None) or (scur > sdb):  # type: ignore # noqa: E501
                                self.queue.put(full_path)
                except Exception as e:  # pylint: disable-msg=W0718
                    self.logger.debug("Error scanning %s: %s",
                                      folder,
                                      e)
                    continue
        finally:
            with db:
                db.folder_add(path)

    def scan(self, *args) -> None:
        """Walk a list of folders in parallel.

        Returns when all folders have been processed.
        """
        workers: list[Thread] = []
        for f in args:
            self.logger.debug("Start worker for %s", f)
            w: Thread = Thread(target=self.walk_dir, args=(f, ))
            w.start()
            workers.append(w)

        for w in workers:
            w.join()

# Local Variables: #
# python-indent: 4 #
# End: #
