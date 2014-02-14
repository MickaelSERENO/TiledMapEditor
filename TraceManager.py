from gi.repository import Gtk, Gdk
from SFMLArea import *
import globalVar
import xml.etree.ElementTree as ET
import io
import csv

class TraceManager(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.listStore = Gtk.ListStore(bool, str)
        self.treeView = Gtk.TreeView(model=self.listStore)
        self.toolButton = dict()

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
        self.toolButton['newTrace'] = buttonNewTrace

        buttonMoveDown = Gtk.ToolButton()
        buttonMoveDown.set_stock_id(Gtk.STOCK_GO_DOWN)
        self.toolButton['moveDown'] = buttonMoveDown

        buttonMoveUp = Gtk.ToolButton()
        buttonMoveUp.set_stock_id(Gtk.STOCK_GO_UP)
        self.toolButton['moveUp'] = buttonMoveUp

        buttonDelete = Gtk.ToolButton()
        buttonDelete.set_stock_id(Gtk.STOCK_DELETE)
        self.toolButton['delete'] = buttonDelete

        box.pack_start(buttonNewTrace, True, False, 0)
        box.pack_start(buttonMoveDown, True, False, 0)
        box.pack_start(buttonMoveUp, True, False, 0)
        box.pack_start(buttonDelete, True, False, 0)

        self.pack_start(box, False, False, 0)

    def connectToolButton(self, window):
        self.toolButton['newTrace'].connect("clicked", window.newContents.newTrace, self)
        self.toolButton['moveDown'].connect("clicked", self.moveTrace, False)
        self.toolButton['moveUp'].connect("clicked", self.moveTrace, True)
        self.toolButton['delete'].connect("clicked", self.deleteTrace)

    def addTrace(self, tileSize, name, style="Static"):
        self.listStore.append([True, name])
        globalVar.sfmlArea.addTrace(tileSize, style)
        self.show_all()

    def getNumberOfTraces(self):
        return len(self.listStore)

    def showTrace(self, widget, path):
        self.listStore[path][0] = not self.listStore[path][0]
        globalVar.sfmlArea.listTrace[int(path)].show = self.listStore[path][0]

    def moveTrace(self, widget, up):
        selected = self.treeView.get_selection().get_selected()[1]
        if not selected:
            return
        place = int(str(self.listStore.get_path(selected)))
        choice = 1
        if up:
            if place == 0:
                return
            choice = -1
            self.listStore.move_before(selected, self.listStore.get_iter(place-1))

        else:
            if place == self.getNumberOfTraces()-1:
                return
            self.listStore.move_after(selected, self.listStore.get_iter(place+1))


        (globalVar.sfmlArea.listTrace[place], globalVar.sfmlArea.listTrace[place+choice]) = \
                (globalVar.sfmlArea.listTrace[place+choice], globalVar.sfmlArea.listTrace[place]) 


    def deleteTrace(self, widget):
        selected = self.treeView.get_selection().get_selected()[1]
        if selected:
            del globalVar.sfmlArea.listTrace[int(str(self.listStore.get_path(selected)))]
            del self.listStore[self.listStore.get_path(selected)]

    def clearTrace(self):
        self.listStore = Gtk.ListStore(bool, str)
        self.treeView.set_model(self.listStore)
        self.show_all()

    def getSaveFileElem(self, tileBox):
        listTrace = globalVar.sfmlArea.listTrace
        traceElem = ET.Element("Trace")
        for trace in listTrace:
            if trace.style == "Static":
                staticTraceElem = ET.SubElement(traceElem, "StaticTrace")
                staticTraceElem.set('size', str(trace.tileSize.x) + 'x' + str(trace.tileSize.y))
                for column in trace.listStaticTile:
                    columnSubElem = ET.SubElement(staticTraceElem, "Column")
                    columnTileID = io.StringIO()
                    columnFileID = io.StringIO()

                    columnTileRow = []
                    columnFileRow = []

                    tileCSV = csv.writer(columnTileID)
                    fileCSV = csv.writer(columnFileID)
                    for tile in column:
                        if tile:
                            columnTileRow.append(str(tile.tileID))
                            columnFileRow.append(str(tileBox.getFileID(tile.fileName, "static")))
                        else:
                            columnTileRow.append('-1')
                            columnFileRow.append('-1')
                    tileCSV.writerow(columnTileRow)
                    fileCSV.writerow(columnFileRow)

                    columnTileSubElem = ET.SubElement(columnSubElem, "tileID")
                    columnTileSubElem.set('code', columnTileID.getvalue())

                    columnFileSubElem = ET.SubElement(columnSubElem, "fileID")
                    columnFileSubElem.set('code', columnFileID.getvalue())
            else:
                dynamicTraceElem = ET.SubElement(traceElem, 'DynamicTrace')
                for tile in trace.listDynamicTile:
                    if tile.style == "Dynamic":
                        tileSubElem = ET.SubElement(dynamicTraceElem, "DynamicTile")  
                        tileSubElem.set('animName', str(tile.animName))
                        tileSubElem.set('animTime', str(tile.animTime))
                        tileSubElem.set('origin', str(tile.origin.x)+'x'+str(tile.origin.y))
                        tileSubElem.set('fileName', str(tileBox.getFileID(tile.fileName, 'dynamic')))
                        tileSubElem.set('tileID', str(tile.tileID))
                        tileSubElem.set('position', str(tile.position.x)+'x'+str(tile.position.y))
                    else:
                        tileSubElem = ET.SubElement(dynamicTraceElem, "StaticTile")
                        tileSubElem.set('fileName', str(tileBox.getFileID(tile.fileName, 'static')))
                        tileSubElem.set('tileID', str(tile.tileID))
                        tileSubElem.set('position', str(tile.position.x)+'x'+str(tile.position.y))

        return traceElem
