#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2023-10-17 14:49:08 krylon>
#
# /data/code/python/memex/gui.py
# created on 14. 10. 2023
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
memex.gui

(c) 2023 Benjamin Walkenhorst
"""

from typing import Final

# pylint: disable-msg=C0413,C0103
import gi  # type: ignore

from memex import common

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk  # noqa: E402 # pylint: disable-msg=C0411


class MemexUI:  # pylint: disable-msg=R0902,R0903
    """MemexUI is the visual frontend of the application."""

    def __init__(self) -> None:
        # Create widgets first
        self.mw = gtk.Window()
        self.mbox = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        self.menubar = gtk.MenuBar()
        self.file_menu_item = gtk.MenuItem.new_with_mnemonic("_File")
        self.file_menu = gtk.Menu()
        self.button_box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        self.search_box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        self.search_entry = gtk.Entry()
        self.search_button = gtk.Button.new_with_mnemonic("_Search")
        self.clear_button = gtk.Button.new_with_mnemonic("_x")
        self.result_view = gtk.ScrolledWindow()
        self.img_box = gtk.FlowBox()

        self.scan_button = gtk.Button.new_with_mnemonic("_Scan")

        self.scan_item = gtk.MenuItem.new_with_mnemonic("_Scan Folder")
        self.quit_item = gtk.MenuItem.new_with_mnemonic("_Quit")

        # Apply settings
        title: Final[str] = f"{common.APP_NAME} {common.APP_VERSION}"
        self.mw.set_title(title)

        self.result_view.set_policy(gtk.PolicyType.NEVER, gtk.PolicyType.AUTOMATIC)  # noqa: E501
        self.img_box.set_valign(gtk.Align.START)
        self.img_box.set_max_children_per_line(3)
        self.img_box.set_selection_mode(gtk.SelectionMode.NONE)

        # Build window
        self.mw.add(self.mbox)
        self.mbox.pack_start(self.menubar, False, True, 0)

        self.mbox.pack_start(self.button_box, False, True, 0)
        self.mbox.pack_start(self.search_box, False, True, 0)
        self.mbox.pack_start(self.result_view, True, True, 0)
        self.result_view.add(self.img_box)

        self.menubar.append(self.file_menu_item)
        self.file_menu_item.set_submenu(self.file_menu)
        self.file_menu.append(self.scan_item)
        self.file_menu.append(self.quit_item)

        self.button_box.pack_start(self.scan_button, False, True, 0)

        self.search_box.pack_start(self.search_entry, True, True, 0)
        self.search_box.pack_start(self.search_button, False, True, 0)
        self.search_box.pack_start(self.clear_button, False, True, 0)

        # Set up signal handlers
        self.mw.connect("destroy", gtk.main_quit)
        self.quit_item.connect("activate", gtk.main_quit)

        self.mw.show_all()


# Local Variables: #
# python-indent: 4 #
# End: #
