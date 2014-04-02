#!/usr/bin/python3
#-*-coding:utf-8-*-

from gi.repository import Gtk, GObject, Gdk
from TileWindow import TileWindow
import globalVar

window = TileWindow()
globalVar.tileWindow = window
window.connect("delete_event", Gtk.main_quit)
Gtk.main()
