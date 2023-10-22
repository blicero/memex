#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2023-10-22 21:40:32 krylon>
#
# /data/code/python/memex/cli.py
# created on 10. 10. 2023
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
memex.cli

(c) 2023 Benjamin Walkenhorst
"""

import argparse
import os
import time
from queue import Queue

from memex import common, database, reader, scanner


def main() -> None:
    """The entry point for the CLI version."""

    argp: argparse.ArgumentParser = argparse.ArgumentParser()
    argp.add_argument("-a", "--action",
                      choices=["scan", "search"],
                      required=True,
                      help="Which action to perform: scan, search")
    argp.add_argument("-f", "--folders",
                      metavar="folders",
                      nargs="*",
                      help="Folders to scan")
    argp.add_argument("-w", "--workers",
                      type=int,
                      default=os.cpu_count(),
                      help="Number of worker threads to use")
    argp.add_argument("-q", "--query",
                      help="Query string")
    argp.add_argument("-v", "--verbose",
                      help="Emit additional messages",
                      action="store_true")

    args = argp.parse_args()

    # if args.verbose:
    #     logging.setLevel(logging.DEBUG)
    # else:
    #     logging.setLevel(logging.INFO)

    common.init_app()

    print(f"Action: {args.action} / Folders: {args.folders}")

    if args.action == "scan":
        # pylint: disable-msg=C0103
        q: Queue[str] = Queue()
        sc = scanner.Scanner(q)
        rdr = reader.Reader(q, args.workers)
        sc.scan(*args.folders)
        print("Done.")
        while rdr.file_queue.qsize() > 0:
            print(f"Waiting for {q.qsize()} files to be processed.")
            time.sleep(1)
    elif args.action == "search":
        # pylint: disable-msg=C0103
        db = database.Database(common.path.db())
        files = db.file_search(args.query)
        for f in files:
            print(f.path)


if __name__ == "__main__":
    main()

# Local Variables: #
# python-indent: 4 #
# End: #
