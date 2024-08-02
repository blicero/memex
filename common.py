#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-07-26 20:04:30 krylon>
#
# /data/code/python/memex/common.py
# created on 28. 09. 2023
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
Common

(c) 2023 Benjamin Walkenhorst

This module contains definitions commonly used throughout the application.
"""

import logging
import logging.handlers
import os
import os.path

from threading import Lock
from typing import Final

APP_NAME: Final[str] = "Memex"
APP_VERSION: Final[str] = "0.2.0"
DEBUG: Final[bool] = True


class Path:
    """Holds the paths of folders and files used by the application"""

    __base: str

    def __init__(self, root: str = os.path.expanduser(f"~/.{APP_NAME.lower()}.d")) -> None:  # noqa
        self.__base = root

    def base(self, folder: str = "") -> str:
        """Return the base directory for application specific files.

        If path is a non-empty string, set the base directory to its value.
        """
        if folder != "":
            self.__base = folder
        return self.__base

    def window(self) -> str:
        """Return the path of the window state file"""
        return os.path.join(self.__base, f"{APP_NAME.lower()}.win")

    def db(self) -> str:  # pylint: disable-msg=C0103
        """Return the path to the database"""
        return os.path.join(self.__base, f"{APP_NAME.lower()}.db")

    def log(self) -> str:
        """Return the path to the log file"""
        return os.path.join(self.__base, f"{APP_NAME.lower()}.log")


path: Path = Path(os.path.expanduser(f"~/.{APP_NAME.lower()}.d"))

_lock: Final[Lock] = Lock()  # pylint: disable-msg=C0103
_cache: Final[dict[str, logging.Logger]] = {}  # pylint: disable-msg=C0103


def set_basedir(folder: str) -> None:
    """Set the base dir to the speficied path."""
    path.base(folder)
    init_app()


def init_app() -> None:
    """Initialize the application environment"""
    print(f"Create base directory {path.base()}")
    if not os.path.isdir(path.base()):
        os.mkdir(path.base())


def get_logger(name: str, terminal: bool = True) -> logging.Logger:
    """Create and return a logger with the given name"""
    with _lock:
        init_app()

        if name in _cache:
            return _cache[name]

        log_format = "%(asctime)s (%(name)-16s / line %(lineno)-4d) " + \
            "- %(levelname)-8s %(message)s"
        max_log_size = 256 * 2**20
        max_log_count = 4

        log_obj = logging.getLogger(name)
        log_obj.setLevel(logging.DEBUG)
        log_file_handler = logging.handlers.RotatingFileHandler(path.log(),
                                                                'a',
                                                                max_log_size,
                                                                max_log_count)

        log_fmt = logging.Formatter(log_format)
        log_file_handler.setFormatter(log_fmt)
        log_obj.addHandler(log_file_handler)

        if terminal:
            log_console_handler = logging.StreamHandler()
            log_console_handler.setFormatter(log_fmt)
            log_console_handler.setLevel(logging.DEBUG)
            log_obj.addHandler(log_console_handler)

        _cache[name] = log_obj
        return log_obj


# Local Variables: #
# python-indent: 4 #
# End: #
