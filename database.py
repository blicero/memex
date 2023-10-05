#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2023-10-06 00:45:35 krylon>
#
# /data/code/python/memex/database.py
# created on 05. 10. 2023
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
memex.database

(c) 2023 Benjamin Walkenhorst
"""

import logging
import sqlite3
import threading
from enum import Enum, auto
from typing import Final, List

import krylib

from memex import common

INIT_QUERIES: Final[List[str]] = [
    """CREATE TABLE image (
        id INTEGER PRIMARY KEY,
        path TEXT UNIQUE NOT NULL,
        content TEXT,
        timestamp INTEGER NOT NULL)
    """,

    "CREATE UNIQUE INDEX img_path_idx ON image (path)",
    "CREATE INDEX img_time_idx ON image (timestamp)",
    "CREATE INDEX img_content_idx ON image (content)",
    "CREATE VIRTUAL TABLE img_index (path, content)",

    """
CREATE TRIGGER tr_fts_img_add
AFTER INSERT ON image
BEGIN
    INSERT INTO img_index (path, content) VALUES (new.path, new.content);
END;
""",

    """
CREATE TRIGGER tr_fts_img_del
AFTER DELETE ON image
BEGIN
    DELETE FROM img_index WHERE path = old.path;
END;
""",

    """
CREATE TRIGGER tr_fts_img_up
AFTER UPDATE ON image
    UPDATE img_index SET content = new.content WHERE path = new.path;
END;
""",
]

open_lock: threading.Lock = threading.Lock()


class Query(Enum):
    """Query provides symbolic constants for database queries."""
    FILE_ADD = auto()
    FILE_UPDATE = auto()
    FILE_DELETE = auto()


DB_QUERIES: Final[dict[Query, str]] = {
    Query.FILE_ADD:
    "INSERT INTO image (path, content, timestamp) VALUES (?, ?, ?)",
    Query.FILE_DELETE:
    "DELETE FROM image WHERE id = ?",
    Query.FILE_UPDATE:
    "UPDATE image SET content = ?, timestamp = ? WHERE id = ?",
}


class Database:  # pylint: disable-msg=R0903
    """Database wraps the database connection and associated state and
    provides the operations the application needs to perform on persistent
    data."""

    log: logging.Logger
    path: Final[str]  # pylint: disable-msg=C0103
    db: sqlite3.Connection

    def __init__(self, path: str) -> None:
        self.path = path
        self.log = common.get_logger("database")
        with open_lock:
            exist: bool = krylib.fexist(path)
            self.db = sqlite3.connect(path)  # pylint: disable-msg=C0103

            if not exist:
                self.__create_db()

    def __create_db(self) -> None:
        """Initialize a fresh database."""
        with self.db:
            for query in INIT_QUERIES:
                cur: sqlite3.Cursor = self.db.cursor()
                cur.execute(query)

# Local Variables: #
# python-indent: 4 #
# End: #
