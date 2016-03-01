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
from ObjectManager import *
from MiniMap import *
import xml.etree.ElementTree as ET
import sfml as sf

class TileWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="TileMapEditor")
        self.iconTheme = Gtk.IconTheme.get_default()
        self.iconTheme.append_search_path("Ressources/Icons")
        self.fileManager = FileManager(self)
        self.newContents = CreateMenu(self)
        self.tileBox = TileBox()
        self.traceManager = TraceManager()
        self.objectManager = ObjectManager()
        self.sfmlTilePaned = Gtk.Paned()
        self.sfmlTilePaned.pack1(self.tileBox)

        self.toolNotebook = Gtk.Notebook()
        self.toolNotebook.append_page(self.traceManager, Gtk.Label("Trace Manager"))
        self.toolNotebook.set_size_request(200,200)
        self.miniMap = MiniMap(self.toolNotebook)

        self.toolPaned = Gtk.Paned(orientation = Gtk.Orientation.VERTICAL)
        self.toolPaned.add1(self.toolNotebook)
        self.toolPaned.pack2(self.objectManager)
        self.toolPaned.connect('notify::position', self.handleToolPanedMoving)
        self.toolPaned.set_property('position-set', True)
        self.toolPaned.set_position(300)

        self.sfmlBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.sfmlTilePaned.add2(self.sfmlBox)
        self.sfmlTilePaned.set_size_request(500, 300)

        globalVar.sfmlArea = None

        self.panedSFML_toolPaned = Gtk.Paned()
        self.panedSFML_toolPaned.add1(self.sfmlTilePaned)
        self.panedSFML_toolPaned.pack2(self.toolPaned, False, False)
        self.panedSFML_toolPaned.connect('notify::position', self.handleToolPanedMoving)
        self.panedSFML_toolPaned.set_property('position-set', True)
        self.panedSFML_toolPaned.set_position(600)
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
        hbox.pack_start(self.panedSFML_toolPaned, True, True, 0)
        vbox.pack_start(hbox, True, True, 0)

        self.traceManager.connectToolButton(self)
        self.tileBox.makePopupMenu(self.uiManager)

        self.mode = None

        self.show_all()

    def buildSFMLArea(self, numberCase, size):
        if globalVar.sfmlArea:
            self.traceManager.clearAll()
            self.tileBox.clearAll()
            self.objectManager.clearAll()
            for child in self.sfmlBox:
                self.sfmlBox.remove(child)

        vSlide = Gtk.VScrollbar()
        hSlide = Gtk.HScrollbar()

        globalVar.sfmlArea = SFMLArea(hSlide, vSlide, \
                        numberCase, size, self.miniMap)

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
        for mode in ["Print", "Eraser"]:
            if self.actionGroup.get_action(mode).get_active():
                globalVar.sfmlArea.mode = mode
                self.mode = mode
                break

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
        saveAction.connect("activate", self.manageFile, "save", "xml")

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

        newObjectAction = Gtk.Action("NewObject", "New _Object", None, None)
        actionGroup.add_action_with_accel(newObjectAction, "<Ctrl><Shift>o")
        newObjectAction.connect("activate", self.objectManager.promptAddObject)

        changeSizeAction = Gtk.Action("ChangeSize", "Chan_ge size", None, None)
        changeSizeAction.connect("activaye", self.promptSetSize)

    def makeToolMenuAction(self, actionGroup):
        toolsMenuAction = Gtk.Action("ToolsMenu", "_Tools", None, None)
        actionGroup.add_action(toolsMenuAction)

        changeSizeAction = Gtk.Action("ChangeSize", "Change size", None, None)
        actionGroup.add_action(changeSizeAction)
        self.zoomPlus = Gtk.Action("Zoom+", None, None, Gtk.STOCK_ZOOM_IN)
        actionGroup.add_action_with_accel(self.zoomPlus, None)
        self.zoomOut = Gtk.Action("Zoom-", None, None, Gtk.STOCK_ZOOM_OUT)
        actionGroup.add_action_with_accel(self.zoomOut, None)

        actionGroup.add_radio_actions([("Print", None, None, "p", None, 0), \
                ("Eraser", None, None, "e", None, 0)], "active", self.radioActionManager)

        actionGroup.get_action("Print").set_icon_name("pencil")
        actionGroup.get_action("Eraser").set_icon_name("eraser")

    def makeSFMLMenuAction(self, actionGroup):
        delCase = Gtk.Action("DelCase", "Delete", None, None)
        setTileProperties = Gtk.Action("SetTileProperties", "Set tile properties", None, None)
        actionGroup.add_action(delCase)
        actionGroup.add_action(setTileProperties)
        
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
            elif mime=="xml":
                self.fileManager.openFileXML(self.tileBox, self.traceManager, self.objectManager)

        elif action=="saveAs":
            self.fileManager.saveAsFile(self.tileBox, self.traceManager, self.objectManager)
        elif action=="save":
            self.fileManager.saveFile(self.tileBox, self.traceManager, self.objectManager)

    def handleToolPanedMoving(self, widget, paramSpec):
        self.miniMap.scalePixbuf()
    
    def newFile(self, widget):
        self.newContents.newFile(self.fileManager)

    def promptSetSize(self, widget):
        self.newContents.setSize()

    def getSaveFileElem(self):
        windowElem = ET.Element('Window')
        windowElem.set('numberCases', str(globalVar.sfmlArea.numberCases.x)+'x'+str(globalVar.sfmlArea.numberCases.y))
        windowElem.set('tileSize', str(globalVar.sfmlArea.sizeCase.x)+'x'+str(globalVar.sfmlArea.sizeCase.y))
        windowElem.set('title', str(self.get_title()))

        return windowElem

    def decodeXML(self, windowElement):
        windowValuesElement = dict()
        for item in windowElement.items():
            windowValuesElement[item[0]]=item[1]

        tileSizeSplit = windowValuesElement['tileSize'].split('x')
        windowValuesElement['tileSize'] = sf.Vector2(float(tileSizeSplit[0]), float(tileSizeSplit[1]))

        numberCasesSplit = windowValuesElement['numberCases'].split('x')
        windowValuesElement['numberCases'] = sf.Vector2(float(numberCasesSplit[0]), float(numberCasesSplit[1]))
        self.buildSFMLArea(windowValuesElement['numberCases'], windowValuesElement['tileSize'])

        self.set_title(windowValuesElement['title'])

    def radioActionManager(self, radioAction, current):
        if globalVar.sfmlArea:
            globalVar.sfmlArea.setMode(current.get_name())
        self.mode = current.get_name()
