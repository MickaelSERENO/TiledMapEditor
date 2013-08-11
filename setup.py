#!/usr/bin/python3

from gi.repository import Gtk, GObject, Gdk
from TileWindow import TileWindow

window = TileWindow()
window.connect("delete_event", Gtk.main_quit)
Gtk.main()
