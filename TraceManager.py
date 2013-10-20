from gi.repository import Gtk, Gdk
from SFMLArea import *
import globalVar

class TraceManager(Gtk.Box):
	def __init__(self):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
		self.listStore = Gtk.ListStore(bool, str)
		self.treeView = Gtk.TreeView(model=self.listStore)

		rendererText = Gtk.CellRendererText()
		rendererToggle = Gtk.CellRendererToggle()
		rendererToggle.connect("toggled", self.showTrace)
		columnText = Gtk.TreeViewColumn("Name",rendererText, text=1)
		columnToggle = Gtk.TreeViewColumn("Show", rendererToggle, active=0)

		self.treeView.append_column(columnToggle)
		self.treeView.append_column(columnText)
		self.pack_start(self.treeView, True, True, 0)

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
		self.listStore.append([True, name])
		globalVar.sfmlArea.addTrace(tileSize, style)
		self.show_all()

	def getNumberOfTraces(self):
		return len(self.listStore)

	def showTrace(self, widget, path):
		self.listStore[path][0] = not self.listStore[path][0]
		globalVar.sfmlArea.listTrace[int(path)].show = self.listStore[path][0]
