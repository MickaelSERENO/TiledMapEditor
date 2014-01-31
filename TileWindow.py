import platform
import globalVar
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
        self.traceManager = TraceManager()
        self.sfmlTilePanned = Gtk.Paned()
        self.sfmlTilePanned.pack1(self.tileBox)

        self.sfmlBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.sfmlTilePanned.add2(self.sfmlBox)
        self.sfmlTilePanned.set_size_request(500, 300)

        globalVar.sfmlArea = None

        panedTraceManager = Gtk.Paned()
        panedTraceManager.add1(self.sfmlTilePanned)
        panedTraceManager.pack2(self.traceManager, False, True)
        self.set_default_size(800, 600)

        self.actionGroup = Gtk.ActionGroup("Actions")
        self.makeSFMLMenuAction(self.actionGroup)
        self.makeFileMenuAction(self.actionGroup)
        self.makeEditionMenuAction(self.actionGroup)
        self.makeToolMenuAction(self.actionGroup)
        self.tileBox.makeActionMenu(self.actionGroup)

        self.uiManager = self.createUIManager()
        self.uiManager.insert_action_group(self.actionGroup)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)
        vbox.pack_start(self.uiManager.get_widget("/MenuBar"), False, False, 0)
        vbox.pack_start(self.uiManager.get_widget("/ToolBar"), False, False, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.pack_start(panedTraceManager, True, True, 0)
        vbox.pack_start(hbox, True, True, 0)

        self.traceManager.connectToolButton(self)
        self.tileBox.makePopupMenu(self.uiManager)

        self.show_all()

    def buildSFMLArea(self, numberCase, size):
        if globalVar.sfmlArea:
            self.traceManager.clearTrace()
            self.tileBox.clearTile()
            for child in self.sfmlBox:
                self.sfmlBox.remove(child)


        vSlide = Gtk.VScrollbar()
        hSlide = Gtk.HScrollbar()

        globalVar.sfmlArea = SFMLArea(hSlide, vSlide, \
                        numberCase, size)

        hBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.eventSFMLBox = Gtk.EventBox()
        self.eventSFMLBox.add(globalVar.sfmlArea)
        hBox.pack_start(self.eventSFMLBox, True, True, 0)
        hBox.pack_start(vSlide, False, False, 0)
        self.sfmlBox.pack_start(hBox, True, True, 0)
        self.sfmlBox.pack_start(hSlide, False, False, 0)

        globalVar.sfmlArea.makePopupAction(self.actionGroup)
        globalVar.sfmlArea.makePopup(self.uiManager, self.eventSFMLBox)
        
        self.show_all()
        if platform.system() == "Linux":
            globalVar.sfmlArea.render.create(globalVar.sfmlArea.get_window().get_xid())
        elif platform.system() == "Windows":
            globalVar.sfmlArea.render.create(GdkWin32.Win32Window.get_handle(globalVar.sfmlArea.get_window()))
        self.zoomPlus.connect("activate", globalVar.sfmlArea.zoom, "in")
        self.zoomOut.connect("activate", globalVar.sfmlArea.zoom, "out")

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

        newTraceAction = Gtk.Action("NewTrace", "New _Trace", None, None)
        actionGroup.add_action_with_accel(newTraceAction, "<Ctrl><Shift>t")
        newTraceAction.connect("activate", self.newContents.newTrace, self.traceManager)

        newImageAction = Gtk.Action("NewImage", "New _Image", None, None)
        actionGroup.add_action_with_accel(newImageAction, "<Ctrl><Shift>i")
        newImageAction.connect("activate", self.manageFile, "open", "image")

        changeSizeAction = Gtk.Action("ChangeSize", "Chan_ge size", None, None)

    def makeToolMenuAction(self, actionGroup):
        toolsMenuAction = Gtk.Action("ToolsMenu", "_Tools", None, None)
        actionGroup.add_action(toolsMenuAction)

        changeSizeAction = Gtk.Action("ChangeSize", "Change size", None, None)
        actionGroup.add_action(changeSizeAction)
        self.zoomPlus = Gtk.Action("Zoom+", None, None, Gtk.STOCK_ZOOM_IN)
        actionGroup.add_action_with_accel(self.zoomPlus, None)
        self.zoomOut = Gtk.Action("Zoom-", None, None, Gtk.STOCK_ZOOM_OUT)
        actionGroup.add_action_with_accel(self.zoomOut, None)

    def makeSFMLMenuAction(self, actionGroup):
        delCase = Gtk.Action("DelCase", "Delete", None, None)
        actionGroup.add_action(delCase)
        
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
        self.newContents.newFile(self.fileManager)
