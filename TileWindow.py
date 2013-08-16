import platform
from gi.repository import Gtk, GObject, Gdk
if platform.system() == "Linux":
	from gi.repository import GdkX11
elif platform.system() == "Windows":
	from gi.repository import GdkWin32
from SFMLArea import SFMLArea
from FileManager import FileManager
from CreateMenu import CreateMenu
from TileBox import TileBox
from TraceManager import TraceManager
import sfml as sf

class TileWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="TileMapEditor")
		self.fileManager = FileManager(self)
		self.newContents = CreateMenu(self)
		self.tileBox = TileBox()
		self.buildSFMLArea()

		self.set_default_size(800, 600)

		actionGroup = Gtk.ActionGroup("Actions")
		self.makeFileMenuAction(actionGroup)
		self.makeEditionMenuAction(actionGroup)
		self.makeToolMenuAction(actionGroup)
		self.sfmlArea.makePopupAction(actionGroup)

		uiManager = self.createUIManager()
		uiManager.insert_action_group(actionGroup)

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.add(vbox)
		vbox.pack_start(uiManager.get_widget("/MenuBar"), False, False, 0)
		vbox.pack_start(uiManager.get_widget("/ToolBar"), False, False, 0)
		self.sfmlArea.makePopup(uiManager, self.eventSFMLBox)

		self.traceManager = TraceManager()
		panedTraceManager = Gtk.Paned()
		panedTraceManager.add1(self.tileBox)
		panedTraceManager.add2(self.traceManager)

		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.pack_start(panedTraceManager, True, True, 0)
		vbox.pack_start(hbox, True, True, 0)

		self.show_all()
		if platform.system() == "Linux":
			self.sfmlArea.render.create(self.sfmlArea.get_window().get_xid())
		elif paltform.system() == "Windows":
			self.sfmlArea.render.create(GdkWin32.Win32Window.get_handle(self.sfmlArea.get_window()))
#		self.sfmlArea.get_parent().get_parent().get_parent().hide()

	def buildSFMLArea(self):
		vSlide = Gtk.VScrollbar()
		hSlide = Gtk.HScrollbar()

		vBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		hBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

		self.sfmlArea = SFMLArea(hSlide, vSlide, \
				sf.Vector2(110, 110), sf.Vector2(32, 32))
		self.eventSFMLBox = Gtk.EventBox()
		self.eventSFMLBox.add(self.sfmlArea)
		hBox.pack_start(self.eventSFMLBox, True, True, 0)
		hBox.pack_start(vSlide, False, False, 0)
		vBox.pack_start(hBox, True, True, 0)
		vBox.pack_start(hSlide, False, False, 0)

		self.tileBox.add2(vBox)

	def makeFileMenuAction(self, actionGroup):
		fileMenuAction = Gtk.Action("FileMenu", "_File", None, None)
		actionGroup.add_action(fileMenuAction)

		newFileAction = Gtk.Action("NewFile", None, None, Gtk.STOCK_NEW)
		actionGroup.add_action_with_accel(newFileAction, None)
		newFileAction.connect("activate", self.newFile)

		openFileAction = Gtk.Action("OpenFile", None, None, Gtk.STOCK_OPEN)
		openFileAction.connect("activate", self.manageFile, "open", "xml")
		actionGroup.add_action_with_accel(openFileAction, None)

		saveAction = Gtk.Action("Save", None, None, Gtk.STOCK_SAVE)
		actionGroup.add_action_with_accel(saveAction, None)

		saveAsAction = Gtk.Action("SaveAs", None, None, Gtk.STOCK_SAVE_AS)
		actionGroup.add_action_with_accel(saveAsAction, "<Ctrl><Shift>s")
		saveAsAction.connect("activate", self.manageFile, "saveAs", "xml")

	def makeEditionMenuAction(self, actionGroup):
		editionMenuAction = Gtk.Action("EditionMenu", "_Edition", None, None)
		actionGroup.add_action(editionMenuAction)

		newCalcAction = Gtk.Action("NewCalc", "New _Calc", None, None)
		actionGroup.add_action_with_accel(newCalcAction, "<Ctrl><Shift>c")

		newImageAction = Gtk.Action("NewImage", "New _Image", None, None)
		actionGroup.add_action_with_accel(newImageAction, "<Ctrl><Shift>i")
		newImageAction.connect("activate", self.manageFile, "open", "image")

		changeSizeAction = Gtk.Action("ChangeSize", "Chan_ge size", None, None)

	def makeToolMenuAction(self, actionGroup):
		toolsMenuAction = Gtk.Action("ToolsMenu", "_Tools", None, None)
		actionGroup.add_action(toolsMenuAction)

		changeSizeAction = Gtk.Action("ChangeSize", "Change size", None, None)
		actionGroup.add_action(changeSizeAction)
		zoomPlus = Gtk.Action("Zoom+", None, None, Gtk.STOCK_ZOOM_IN)
		zoomPlus.connect("activate", self.sfmlArea.zoom, "in")
		actionGroup.add_action_with_accel(zoomPlus, None)
		zoomOut = Gtk.Action("Zoom-", None, None, Gtk.STOCK_ZOOM_OUT)
		zoomOut.connect("activate", self.sfmlArea.zoom, "out")
		actionGroup.add_action_with_accel(zoomOut, None)
		
	def createUIManager(self):
		with open("Ressources/UI_INFO.xml", 'r') as info:
			ui = Gtk.UIManager()
			ui.add_ui_from_string(info.read())
			self.add_accel_group(ui.get_accel_group())
			return ui

	def manageFile(self, widget, action, mime=""):
		if action=="open":
			if mime=="image":
				self.newContents.createNewImage(self.fileManager, self.tileBox)

		elif action=="saveAs":
			print(self.fileManager.saveFile())

	def newFile(self, widget):
		self.newContents.newFile(self.fileManager, self.sfmlArea)
