#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2023-09-28 20:54:54 krylon>
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
import os
import os.path

from typing import Final

# Base path for application-specific files
BASE_DIR: Final[str] = os.path.expanduser("~/.memex.d")

# Path of the database
DB_PATH: Final[str] = os.path.join(BASE_DIR, "memex.db")

# Path of the log file
LOG_PATH: Final[str] = os.path.join(BASE_DIR, "memex.log")

APP_NAME: Final[str] = "Memex"
APP_VERSION: Final[str] = "0.0.1"
DEBUG: Final[bool] = True


def init_app():
    """Initialize the application environment"""
    if not os.path.isdir(BASE_DIR):
        os.mkdir(BASE_DIR)

def get_logger(name):
    """Create and return a logger with the given name"""
    pass

# Local Variables: #
# python-indent: 4 #
# End: #
