#!/usr/bin/python3
#-*-coding:utf-8-*-

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkX11', '3.0')

from gi.repository import Gtk, GObject, Gdk
from TileWindow import TileWindow
import globalVar

window = TileWindow()
globalVar.tileWindow = window
window.connect("delete_event", Gtk.main_quit)
Gtk.main()
