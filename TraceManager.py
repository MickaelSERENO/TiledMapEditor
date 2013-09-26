from gi.repository import Gtk, Gdk
from SFMLArea import *
import globalVar

class TraceManager(Gtk.Box):
	def __init__(self):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
		self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.pack_start(self.vbox, True, True, 0)
		self.buildMenu()
		self.set_size_request(100, 300)

	def buildMenu(self):
		box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		buttonNewTrace = Gtk.ToolButton()
		buttonNewTrace.set_stock_id(Gtk.STOCK_NEW)
		buttonMoveDown = Gtk.ToolButton()
		buttonMoveDown.set_stock_id(Gtk.STOCK_GO_DOWN)
		buttonMoveUp = Gtk.ToolButton()
		buttonMoveUp.set_stock_id(Gtk.STOCK_GO_UP)
		buttonDelete = Gtk.ToolButton()
		buttonDelete.set_stock_id(Gtk.STOCK_DELETE)

		box.pack_start(buttonNewTrace, True, False, 0)
		box.pack_start(buttonMoveDown, True, False, 0)
		box.pack_start(buttonMoveUp, True, False, 0)
		box.pack_start(buttonDelete, True, False, 0)

		self.pack_start(box, False, False, 0)

	def addTrace(self, tileSize, name, style="Normal"):
		box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		seeTrace = Gtk.CheckButton(label="Show trace", active=True)
		box.pack_start(seeTrace, False, False, 0)
		box.pack_start(Gtk.Label(name), False, False, 0)
		self.vbox.pack_start(box, False, False, 0)

		globalVar.sfmlArea.addTrace(tileSize, style)
		self.show_all()

	def getNumberOfTraces(self):
		return len(self.vbox)
