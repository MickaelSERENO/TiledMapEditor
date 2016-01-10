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
        self.set_size_request(100, 250)

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

    def addStaticTrace(self, tileSize, shift, name):
        self.listStore.append([True, name])
        globalVar.sfmlArea.addStaticTrace(tileSize, shift, name)
        self.show_all()

    def addDynamicTrace(self, name):
        self.listStore.append([True, name])
        globalVar.sfmlArea.addDynamicTrace(name)

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

    def clearAll(self):
        self.listStore = Gtk.ListStore(bool, str)
        self.treeView.set_model(self.listStore)
        self.show_all()

    def getSaveFileElem(self, tileBox, objectManager):
        listTrace = globalVar.sfmlArea.listTrace
        traceElem = ET.Element("Traces")
        for trace in listTrace:
            if trace.style == "Static":
                staticTraceElem = ET.SubElement(traceElem, "StaticTrace")
                staticTraceElem.set('size', str(trace.tileSize.x) + 'x' + str(trace.tileSize.y))
                staticTraceElem.set('shift', str(trace.shift.x) + 'x' + str(trace.shift.y))
                staticTraceElem.set('name', trace.name)
                for column in trace.listStaticTile:
                    columnSubElem = ET.SubElement(staticTraceElem, "Column")
                    columnTileID = io.StringIO()
                    columnFileID = io.StringIO()
                    columnObjectID = io.StringIO()

                    columnTileRow = []
                    columnFileRow = []
                    columnObjectRow = []

                    tileCSV = csv.writer(columnTileID)
                    fileCSV = csv.writer(columnFileID)
                    objectCSV = csv.writer(columnObjectID)

                    for tile in column:
                        if tile:
                            if type(tile)==StaticTile:
                                columnTileRow.append(str(tile.tileID))
                                columnFileRow.append(str(tileBox.getFileID(tile.fileName, "static")))
                                columnObjectRow.append('0')
                            elif type(tile)==ObjectTile:
                                columnTileRow.append(objectManager.getObjectID(tile.name))
                                columnFileRow.append('-1')
                                columnObjectRow.append('1')
                        else:
                            columnTileRow.append('-1')
                            columnFileRow.append('-1')
                            columnObjectRow.append('0')
                    tileCSV.writerow(columnTileRow)
                    fileCSV.writerow(columnFileRow)
                    objectCSV.writerow(columnObjectRow)

                    columnSubElem.set('tileID', columnTileID.getvalue())
                    columnSubElem.set('fileID', columnFileID.getvalue())
                    columnSubElem.set('objectID', columnObjectID.getvalue())
            else:
                dynamicTraceElem = ET.SubElement(traceElem, 'DynamicTrace')
                dynamicTraceElem.set('name', trace.name)
                for tile in trace.listDynamicTile:
                    if tile.style == "Dynamic":
                        tileSubElem = ET.SubElement(dynamicTraceElem, "DynamicTile")  
                        tileSubElem.set('animName', str(tile.animName))
                        tileSubElem.set('animTime', str(tile.animTime))
                        tileSubElem.set('origin', str(tile.origin.x)+'x'+str(tile.origin.y))
                        tileSubElem.set('fileID', str(tileBox.getFileID(tile.fileName, 'dynamic')))
                        tileSubElem.set('tileID', str(tile.tileID))
                        tileSubElem.set('position', str(tile.position.x)+'x'+str(tile.position.y))
                    else:
                        tileSubElem = ET.SubElement(dynamicTraceElem, "StaticTile")
                        tileSubElem.set('fileID', str(tileBox.getFileID(tile.fileName, 'static')))
                        tileSubElem.set('tileID', str(tile.tileID))
                        tileSubElem.set('position', str(tile.position.x)+'x'+str(tile.position.y))

        return traceElem

    def decodeXML(self, elem, tileBox, objectManager):
        staticTraceList = elem.findall('StaticTrace')
        dynamicTraceList = elem.findall('DynamicTrace')

        for staticTraceElem in staticTraceList:
            traceValues = dict()
            for items in staticTraceElem.items():
                traceValues[items[0]] = items[1]

            tileSizeSplit = traceValues['size'].split('x')
            traceValues['size'] = sf.Vector2(float(tileSizeSplit[0]), float(tileSizeSplit[1]))
            tileShiftSplit = traceValues['shift'].split('x')
            traceValues['shift'] = sf.Vector2(float(tileShiftSplit[0]), float(tileShiftSplit[1]))

            self.addStaticTrace(traceValues['size'], traceValues['shift'], traceValues['name'])

            staticTrace = globalVar.sfmlArea.listTrace[-1]

            x=0
            for columnElem in staticTraceElem.findall('Column'):
                columnValues = dict()
                for items in columnElem.items():
                    columnValues[items[0]] = items[1]

                tileIDListElement = [columnValues['tileID']]
                tileIDListElement = list(csv.reader(tileIDListElement))

                fileIDListElement = [columnValues['fileID']]
                fileIDListElement = list(csv.reader(fileIDListElement))

                objectIDListElement = [columnValues['objectID']]
                objectIDListElement = list(csv.reader(objectIDListElement))

                y=0
                for tileID, fileID, objectID in\
                        zip(tileIDListElement[0], fileIDListElement[0], objectIDListElement[0]):
                    if int(tileID) != -1:
                        dndDatas = None
                        if int(fileID) != -1:
                            dndDatas = tileBox.getDndDatas(int(tileID), int(fileID))
                        elif int(objectID) == 1:
                           dndDatas = objectManager.getDndDatas(int(tileID))
                        staticTrace.addTileFromDnd(x*traceValues['size'].x + traceValues['shift'].x,\
                                    y*traceValues['size'].y+traceValues['shift'].y, dndDatas)
                    y=y+1
                x=x+1

        for dynamicTraceElem in dynamicTraceList:
            traceValues = dict()
            for items in dynamicTraceElem.items():
                traceValues[items[0]] = items[1]

            self.addDynamicTrace(traceValues['name'])
            dynamicTrace = globalVar.sfmlArea.listTrace[-1]

            for dynamicTileElem in dynamicTraceElem.findall('DynamicTile'):
                dynamicValue = dict()
                for items in dynamicTileElem.items():
                    dynamicValue[items[0]] = items[1]

                origin   = dynamicValue['origin'].split('x')
                origin   = sf.Vector2(float(origin[0]), float(origin[1]))
                position = dynamicValue['position'].split('x')
                position = sf.Vector2(float(position[0]), float(position[1]))

                dndDatas = tileBox.getDndDatas(int(dynamicValue['tileID']), int(dynamicValue['fileID']))
                dynamicTraceWidgets = {"origin" : origin, "position" : position,\
                        "timeEntry" : int(float(dynamicValue['animTime']))}
                TileBox.dndDatas = dndDatas

                dynamicTrace.addDynamicTile(dynamicTraceWidgets)

            for staticTileElem in dynamicTraceElem.findall('StaticTile'):
                staticValues = dict()
                for items in staticTileElem.items():
                    staticValues[items[0]] = items[1]

                dndDatas = tileBox.getDndDatas(int(staticValues['tileID']), int(staticValues['fileID']))
                TileBox.dndDatas = dndDatas

                position = staticValues['position'].split('x')
                position = sf.Vector2(float(position[0]), float(position[1]))

                dynamicTrace.addStaticTile(position.x, position.y)
