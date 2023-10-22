#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2023-10-22 22:13:43 krylon>
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

import os
import re
from queue import Queue
from threading import Lock, Thread
from typing import Final

# pylint: disable-msg=C0413,C0103
import gi  # type: ignore

from memex import common, database, image, reader, scanner

gi.require_version("Gtk", "3.0")
from gi.repository import \
    GdkPixbuf as gpb  # noqa: E402,E501 # pylint: disable-msg=C0411
from gi.repository import \
    GLib as glib  # noqa: E402,E501 # pylint: disable-msg=C0411
from gi.repository import Gtk as gtk  # noqa: E402 # pylint: disable-msg=C0411

state_pat: Final[re.Pattern] = re.compile(r"(\d+)x(\d+)@(\d+),(\d+)")


class MemexUI:  # pylint: disable-msg=R0902,R0903
    """MemexUI is the visual frontend of the application."""

    def __init__(self) -> None:  # pylint: disable-msg=R0915
        self.log = common.get_logger("GUI")
        self.queue: Queue[str] = Queue(os.cpu_count())
        self.scanner = scanner.Scanner(self.queue)
        self.reader = reader.Reader(self.queue)
        self.lock = Lock()
        self.scan_active = False
        self.db = database.Database(common.path.db())

        # Create widgets first
        self.mw = gtk.Window()
        self.mbox = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        self.menubar = gtk.MenuBar()
        self.file_menu_item = gtk.MenuItem.new_with_mnemonic("_File")
        self.file_menu = gtk.Menu()
        self.button_box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        self.search_box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        self.search_entry = gtk.Entry()
        self.search_button = gtk.Button.new_from_stock(gtk.STOCK_FIND)  # pylint: disable-msg=E1101 # noqa: E501
        self.clear_button = gtk.Button.new_from_stock(gtk.STOCK_CLEAR)  # pylint: disable-msg=E1101 # noqa: E501
        self.result_view = gtk.ScrolledWindow()
        self.img_box = gtk.FlowBox()
        self.images: list[tuple[image.Image, gtk.Image]] = []

        self.scan_button = gtk.Button.new_from_icon_name("folder", 5)
        self.refresh_button = gtk.Button.new_from_stock(gtk.STOCK_REFRESH)  # pylint: disable-msg=E1101 # noqa: E501

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
        # pylint: disable-msg=E1101
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
        self.button_box.pack_start(self.refresh_button, False, True, 0)

        self.search_box.pack_start(self.search_entry, True, True, 0)
        self.search_box.pack_start(self.search_button, False, True, 0)
        self.search_box.pack_start(self.clear_button, False, True, 0)

        # Set up signal handlers
        self.mw.connect("destroy", gtk.main_quit)
        self.quit_item.connect("activate", gtk.main_quit)
        self.scan_button.connect("clicked", self.scan_folder)
        self.refresh_button.connect("clicked", self.__refresh_all_folders)
        self.scan_item.connect("activate", self.scan_folder)
        self.search_button.connect("clicked", self.search)
        self.search_entry.connect("activate", self.search)
        self.clear_button.connect("clicked", self.__clear_search)
        self.quit_item.connect("activate", gtk.main_quit)
        self.mw.connect("window-state-event", self.__save_pos)

        # self.img_box.connect("button-press-event", self.__handle_img_click)
        self.img_box.connect("child-activated", self.__handle_img_click)

        self.mw.show_all()
        self.__restore_pos()
        self.mw.set_focus(self.search_entry)

    def scan_folder(self, *args) -> None:  # pylint: disable-msg=W0613
        """Scan a folder. Duh."""
        dlg = gtk.FileChooserDialog(
            title="Pick a folder...",
            parent=self.mw,
            action=gtk.FileChooserAction.SELECT_FOLDER)
        dlg.add_buttons(
            gtk.STOCK_CANCEL,
            gtk.ResponseType.CANCEL,
            gtk.STOCK_OPEN,
            gtk.ResponseType.OK)

        try:
            # pylint: disable-msg=E1101
            res = dlg.run()
            if res != gtk.ResponseType.OK:
                self.log.debug("Response from dialog: %s", res)
                return

            path = dlg.get_filename()
            self.log.info("Scan folder %s", path)
            thr = Thread(target=self.__scan_worker, args=(path, ))
            thr.start()
        finally:
            dlg.destroy()

    def search(self, *args) -> None:  # pylint: disable-msg=W0613
        """Search for images."""
        for i in self.images:
            self.img_box.remove(i[1])
            i[1].destroy()
        self.images.clear()

        query: str = self.search_entry.get_text()
        self.log.debug("Search for images containing \"%s\"", query)
        results: list[image.Image] = self.db.file_search(query)
        for img_file in results:
            try:
                pb = gpb.Pixbuf.new_from_file_at_scale(filename=img_file.path,
                                                       width=192,
                                                       height=192,
                                                       preserve_aspect_ratio=True)  # noqa: E501
                img = gtk.Image.new_from_pixbuf(pb)
                self.img_box.add(img)  # pylint: disable-msg=E1101
                self.images.append((img_file, img))
                img.show_all()
            except glib.GError as ex:
                self.log.debug("Error processing %s: %s",
                               img_file.path,
                               ex)

    def __clear_search(self, *args) -> None:  # pylint: disable-msg=W0613
        """Clear the search thingy"""
        for i in self.images:
            self.img_box.remove(i[1])
            i[1].destroy()
        self.images.clear()
        self.search_entry.set_text("")

    def __scan_worker(self, path: str) -> None:
        """Perform the actual scanning of folders in the background."""
        with self.lock:
            self.scan_button.set_sensitive(False)
            self.scan_active = True

        try:
            self.scanner.scan([path])
        finally:
            with self.lock:
                self.scan_button.set_sensitive(True)
                self.scan_active = False
                self.db.folder_add(path)

    def __refresh_all_folders(self, _) -> None:
        """Initiate a scan of all folders previously scanned."""
        folders: list[str] = []
        with self.lock:
            folders = self.db.folder_get_all()
        self.log.debug("Refresh the following folders: %s", folders)
        self.scanner.scan(*folders)

    def __handle_img_click(self, box: gtk.FlowBox, child: gtk.FlowBoxChild) -> None:  # noqa: E501 # pylint: disable-msg=W0613
        """Handle a click into the image box"""
        idx: int = child.get_index()
        img: image.Image = self.images[idx][0]
        self.log.debug("You clicked on %s", img.path)
        menu: gtk.Menu = gtk.Menu.new()
        display_item: gtk.MenuItem = gtk.MenuItem.new_with_mnemonic("_Display")
        edit_item: gtk.MenuItem = gtk.MenuItem.new_with_mnemonic("_Edit")
        display_item.connect("activate", self.__handle_img_display, img)
        edit_item.connect("activate", self.__handle_img_edit, img)
        menu.append(display_item)
        menu.append(edit_item)
        menu.show_all()
        menu.popup_at_pointer(None)

    def __handle_img_display(self, _: gtk.MenuItem, img: image.Image) -> None:  # noqa: E501
        """Display the given image."""
        os.system(f"/usr/bin/xdg-open \"{img.path}\"")

    def __handle_img_edit(self, _: gtk.MenuItem, img: image.Image) -> None:
        """Display a dialog for editing the given image."""
        dlg: gtk.Dialog = gtk.Dialog(
            title="Edit comment",
            parent=self.mw,
        )
        dlg.add_buttons(
            gtk.STOCK_CANCEL,
            gtk.ResponseType.CANCEL,
            gtk.STOCK_OK,
            gtk.ResponseType.OK,
        )
        txt: gtk.TextView = gtk.TextView.new()
        txt.editable = True
        txt.get_buffer().set_text(img.comment)
        # pylint: disable-msg=E1101
        lbl: gtk.Label = gtk.Label.new(img.path)
        dlg.get_content_area().add(lbl)
        dlg.get_content_area().add(txt)
        dlg.show_all()

        try:
            response = dlg.run()
            if response != gtk.ResponseType.OK:
                return

            buf = txt.get_buffer()
            start: gtk.TextIter = buf.get_start_iter()
            end: gtk.TextIter = buf.get_end_iter()
            comment: str = buf.get_text(start, end, True)
            if comment != img.comment:
                # Update database
                with self.db:
                    self.db.file_add(
                        img.path,
                        img.content,
                        comment,
                        img.timestamp,
                    )
        finally:
            dlg.destroy()

    def __save_pos(self, *args) -> None:  # pylint: disable-msg=W0613
        """Save the current size and position of the main window to a file"""
        pos: tuple[int, int] = self.mw.get_position()  # pylint: disable-msg=E1101 # noqa: E501
        size: tuple[int, int] = self.mw.get_size()
        geom: Final[str] = f"{size[0]}x{size[1]}@{pos[0]},{pos[1]}"
        self.log.debug("Save Window state: %s", geom)

        with open(common.path.window(), "w", encoding="UTF-8") as fh:
            fh.write(geom)

    def __restore_pos(self) -> None:
        """Restore the main window's size and position."""
        wfile: Final[str] = common.path.window()
        if not os.path.isfile(wfile):
            return
        with open(wfile, "r", encoding="UTF-8") as fh:
            content = fh.read()
            m = state_pat.match(content)
            if isinstance(m, re.Match):
                # pylint: disable-msg=E1101
                size = [int(x) for x in m.group(1, 2)]
                pos = [int(x) for x in m.group(3, 4)]
                self.mw.move(pos[0], pos[1])
                self.mw.resize(size[0], size[1])


def main() -> None:
    """Display the GUI and run the gtk mainloop"""
    mw = MemexUI()
    mw.log.debug("Let's go")
    gtk.main()


if __name__ == "__main__":
    main()

# Local Variables: #
# python-indent: 4 #
# End: #
