#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2023-10-19 20:16:02 krylon>
#
# /data/code/python/memex/test_database.py
# created on 06. 10. 2023
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
memex.test_database

(c) 2023 Benjamin Walkenhorst
"""

# pylint: disable-msg=C0103

import os
import unittest
from datetime import datetime
from typing import Final, Optional

from memex import common, database

TMP_ROOT: Final[str] = "/data/ram"

TEST_DIR: Final[str] = os.path.join(
    TMP_ROOT,
    datetime.now().strftime("memex_test_database_%Y%m%d_%H%M%S"))


class DatabaseTest(unittest.TestCase):
    """Test the database."""

    conn: Optional[database.Database] = None

    @classmethod
    def setUpClass(cls) -> None:
        common.set_basedir(TEST_DIR)

    @classmethod
    def tearDownClass(cls) -> None:
        os.system(f'rm -rf "{TEST_DIR}"')

    @classmethod
    def db(cls, db: Optional[database.Database] = None) -> database.Database:
        """Set or return the database connection."""
        if db is not None:
            cls.conn = db
        if cls.conn is not None:
            return cls.conn
        raise ValueError("conn is None")

    def test_01_db_open(self) -> None:
        """Test opening the database."""
        db: database.Database = database.Database(common.path.db())
        self.assertIsNotNone(db)
        DatabaseTest.db(db)

    def test_02_image_add(self) -> None:
        """Test adding one image to the database."""
        path = "/tmp/img001.jpg"
        content = "Wer das liest, ist doof"
        timestamp = datetime.now()
        db: database.Database = DatabaseTest.db()
        try:
            with db:
                img = db.file_add(path, content, "", timestamp)
                self.assertGreater(img.dbid, 0)
        except Exception as ex:  # pylint: disable-msg=W0718
            self.fail(f"Failed adding image: {ex}")

    def test_03_image_search(self) -> None:
        """Test searching for images"""
        query: Final[str] = "doof"
        db: database.Database = DatabaseTest.db()
        try:
            results = db.file_search(query)
            self.assertGreater(len(results), 0)
        except Exception as ex:  # pylint: disable-msg=W0718
            self.fail(f"Failed searching for image: {ex}")

    def test_04_image_timestamp(self) -> None:
        """Test getting image's timestamp."""
        path: Final[str] = "/tmp/img001.jpg"
        db = self.__class__.db()
        stamp = db.file_timestamp(path)
        self.assertIsNotNone(stamp)
        stamp = db.file_timestamp(path + ".png")
        self.assertIsNone(stamp)

# Local Variables: #
# python-indent: 4 #
# End: #
