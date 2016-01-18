from gi.repository import Gtk, Gdk, GObject
import sfml as sf
from TileBox import TileBox
from TraceTile import *
from copy import copy
from TraceTile import StaticTrace, Tile, DynamicTrace
import globalVar
from collections import OrderedDict

class SFMLArea(Gtk.DrawingArea):
    def __init__(self, hslide, vslide, numberCases, sizeCase, miniMap):
        Gtk.DrawingArea.__init__(self)
        self.hslide = hslide
        self.vslide = vslide
        self.render = sf.HandledWindow()
        self.size = numberCases * sizeCase
        self.size.x = float(self.size.x)
        self.size.y = float(self.size.y)
        self.sizeCase = sizeCase
        self.numberCases = numberCases
        self.set_can_focus(True)

        self.miniMap = miniMap
        self.miniMapSprite = None
        self.miniMapRenderTexture = None

        self.connect("drag-data-received", self.do_drag_data_received)
        self.connect("key-press-event", self.keyPressEvent)
        self.connect("key-release-event", self.keyPressEvent)
        self.connect("motion_notify_event", self.mouseMoveEvent) 
        self.connect("button-press-event", self.buttonPressEvent)
        self.connect("button-release-event", self.buttonReleaseEvent)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        targets = Gtk.TargetList.new([])
        targets.add_image_targets(0, True)

        self.drag_dest_set_target_list(targets)
        self.timeoutUpdate = GObject.timeout_add(100, self.draw)

        self.popupFull = None
        self.popupEmpty = None
        self.setSlideProperties()
        self.listTrace = list()
        self.mode = None

        self.popupDict = dict()

        self.typeDict = OrderedDict()

    def setSlideProperties(self):
        self.vslide.connect("value-changed", self.moveView, "vertical")
        self.hslide.connect("value-changed", self.moveView, "horizontal")
        self.hslide.set_slider_size_fixed(False)
        self.vslide.set_slider_size_fixed(False)

    def setSFMLSize(self, numberCases=None):
        if numberCases:
            self.size = numberCases * self.sizeCase
            for trace in self.listTrace:
                trace.initStaticList(self.sizeCase)
        self.render.size.x = float(min(self.render.size.x, self.size.x))
        self.render.size.y = float(min(self.render.size.y, self.size.y))
        self.render.view.size = copy(self.render.size)
        self.get_toplevel().show_all()
        self.updateMiniMap()
        self.updateSlideValues()

    def setMode(self, mode):
        self.mode = mode

    def updateSlideValues(self):
        difSize = self.size - self.render.view.size
        self.vslide.set_adjustment(Gtk.Adjustment(self.render.view.center.y - self.render.view.size.y/2.0,\
                0, difSize.y, difSize.y/self.sizeCase.y, difSize.y, self.sizeCase.y))
        self.hslide.set_adjustment(Gtk.Adjustment(self.render.view.center.x - self.render.view.size.x/2.0,\
                0, difSize.x, difSize.x/self.sizeCase.x, difSize.x, self.sizeCase.x))

        self.miniMap.update(self.miniMapSprite, self.render.view.center - self.render.view.size/2.0,\
                self.render.view.size)
    def moveView(self, scroll, orientation):
        vector = sf.Vector2()
        if orientation == "vertical":
            vector.y = scroll.get_value() - \
                    (self.render.view.center.y - self.render.view.size.y / 2.0)
        elif orientation=="horizontal":
            vector.x = scroll.get_value() - \
                    (self.render.view.center.x - self.render.view.size.x / 2.0)

        self.render.view.move(vector.x, vector.y)
        self.miniMap.update(self.miniMapSprite, self.render.view.center - self.render.view.size/2.0,\
                self.render.view.size)

    def makePopupAction(self, actionGroup):
        actionGroup.get_action("DelCase").connect("activate", self.manageTile, "delete")
        actionGroup.get_action("SetTileProperties").connect(\
                "activate", self.windowSetTileProperties)

    def makePopup(self, uiManager, eventBox):
        self.popupFull = uiManager.get_widget("/SFMLFullCase")
        self.popupEmpty = uiManager.get_widget("/SFMLEmptyCase")
        eventBox.connect("button-press-event", self.buttonPressEvent)

    def do_size_allocate(self, allocation):
        allocation.width = float(min(allocation.width, self.size.x))
        allocation.height = float(min(allocation.height, self.size.y))
        if not 0 in self.render.size:
            self.render.view.size *= sf.Vector2(float(allocation.width), float(allocation.height)) / \
                    sf.Vector2(float(self.get_allocated_width()), float(self.get_allocated_height()))
            self.render.view.move(float(self.hslide.get_value()) -\
                (self.render.view.center.x - self.render.view.size.x/2.0), \
                self.vslide.get_value() - (self.render.view.center.y - self.render.view.size.y/2.0))
            self.checkViewSize()
        else:
            alloc = sf.Vector2(allocation.width, allocation.height)
            self.render.view.size = alloc
            self.render.view.center = alloc/2.0
        self.render.size = sf.Vector2(float(allocation.width), float(allocation.height))
        self.updateSlideValues()
        Gtk.DrawingArea.do_size_allocate(self, allocation)

    def zoom(self, widget, action):
        factorZoom = 1
        if action=="in":
            factorZoom = 0.9
        else:
            factorZoom = 1.1
        self.render.view.zoom(factorZoom)
        self.checkViewSize()

        if self.render.view.center.x - self.render.view.size.x/2.0 < 0:
            self.render.view.center = sf.Vector2(self.render.view.size.x/2.0,\
                    self.render.view.center.y)
        elif self.render.view.center.x + self.render.view.size.x/2.0 > self.size.x:
            self.render.view.center = sf.Vector2(self.size.x - self.render.view.size.x/2.0,\
                    self.render.view.center.y)
        if self.render.view.center.y - self.render.view.size.y/2.0 < 0:
            self.render.view.center = sf.Vector2(self.render.view.center.x, \
                    self.render.view.size.y/2.0)
        elif self.render.view.center.y + self.render.view.size.y/2.0 > self.size.y:
            self.render.view.center = sf.Vector2(self.render.view.center.x, \
                    self.size.y - self.render.view.size.y/2.0)
        self.updateSlideValues()

    def checkViewSize(self):
        print(self.size)
        if self.render.view.size.x > self.size.x or self.render.view.size.y > self.size.y:
            self.render.view.zoom(min(self.size.x / float(self.render.view.size.x),\
                    self.size.y / float(self.render.view.size.y)))
            self.updateSlideValues()

    def draw(self):
        self.render.empty_event_loop()
        self.render.clear()
        for trace in self.listTrace:
            if trace.show:
                trace.update()
        self.render.display()
        return True

    def updateLastEventTrace(self, event):
        for trace in self.listTrace[::-1]:
            if trace.show:
                trace.updateEventTile(event)
                return

    def do_drag_data_received(self, widget, context, x, y, selection_data, info, time=None):
        if time:
            if x > self.size.x or y > self.size.y:
                return

            for trace in self.listTrace[::-1]:
                if trace.show:
                    pos = self.convertCoord(sf.Vector2(x, y))
                    trace.addTile(pos.x, pos.y)
                    return

    def convertCoord(self, coord):
        return self.render.map_pixel_to_coords(coord, self.render.view)

    def manageTile(self, widget, action):
        print(action)

    def buttonPressEvent(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 3:
                for trace in self.listTrace[::-1]:
                    if trace.show:
                        tile = trace.getTile(self.convertCoord(sf.Vector2(event.x, event.y)))
                        if tile:
                            self.popupDict['tile'] = tile
                            self.popupFull.popup(None, None, None, None, event.button, event.time)
                        else:
                            self.popupEmpty.popup(None, None, None, None,event.button, event.time)
            elif event.button == 1:
                self.get_toplevel().set_focus(self)
        self.updateLastEventTrace(event)

    def buttonReleaseEvent(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_RELEASE:
            self.updateLastEventTrace(event)

    def keyPressEvent(self, widget, event):
        if event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Delete:
                self.listTrace[-1].deleteTile()

        self.updateLastEventTrace(event)

    def keyReleaseEvent(self, widget, event):
        self.updateLastEventTrace(event)

    def mouseMoveEvent(self, widget, event):
        if event.type == Gdk.EventType.MOTION_NOTIFY:
            self.updateLastEventTrace(event)

    def addStaticTrace(self, tileSize, shift, name):
        self.listTrace.append(StaticTrace(tileSize, shift, name))
        self.listTrace[-1].initStaticList(self.size - shift)

    def addDynamicTrace(self, name):
        self.listTrace.append(DynamicTrace(name))

    def updateMiniMap(self):
        self.miniMapRenderTexture = sf.RenderTexture(self.size.x, self.size.y)
        self.miniMapRenderTexture.clear(sf.Color(0,0,0,0))
        for trace in self.listTrace:
            if type(trace) == StaticTrace:
                for row in trace.listStaticTile:
                    for tile in row:
                        if tile:
                            self.miniMapRenderTexture.draw(tile.sprite)
            elif type(trace) == DynamicTrace:
                for tile in trace.listDynamicTile:
                    if tile:
                        self.miniMapRenderTexture.draw(tile.sprite)


        self.miniMapRenderTexture.display()
        self.miniMapSprite = sf.Sprite(self.miniMapRenderTexture.texture)
        self.miniMap.update(self.miniMapSprite,self.render.view.center - self.render.view.size/2,\
                self.render.view.size)

    def windowSetTileProperties(self, widget):
        window = Gtk.Window(title="Set tile properties")
        window.set_property("modal", True)
        accelGroup = Gtk.AccelGroup()
        window.add_accel_group(accelGroup)

        vgrid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        grid = Gtk.Grid()
        valueGrid = Gtk.Grid()

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vgrid.add(grid)
        vgrid.add(valueGrid)
        vgrid.add(hbox)

        nameLabel = Gtk.Label("Name")
        typeLabel = Gtk.Label("Type")
        valueLabel = Gtk.Label("Value")

        nameComboBox = Gtk.ComboBoxText.new_with_entry()
        typeComboBox = Gtk.ComboBoxText.new_with_entry()
        for t in self.typeDict.keys():
            nameComboBox.append_text(t)

        for t in ['str', 'int', 'double', 'Vector2']:
            typeComboBox.append_text(t)

        okButton = Gtk.Button(label="OK")
        okButton.add_accelerator("activate", accelGroup, Gdk.KEY_Return, 0, \
                Gtk.AccelFlags.VISIBLE)
        okButton.add_accelerator("activate", accelGroup, Gdk.KEY_KP_Enter, 0, \
                Gtk.AccelFlags.VISIBLE)
        
        okButton.connect("clicked", self.setProperties, \
                {'hNumberCases':spinCasesLeft, 'vNumberCases':spinCasesRight, \
                'nameEntered':nameEntered, 'window':window})

        cancelButton = Gtk.Button(label="Cancel")
        cancelButton.add_accelerator("activate", accelGroup, Gdk.KEY_Escape, 0, \
                Gtk.AccelFlags.MASK)
        cancelButton.connect("clicked", self.quitWindow, window)

        hbox.pack_start(cancelButton, False, False, 0)
        hbox.pack_start(okButton, False, False, 0)
        hbox.set_halign(Gtk.Align.END)
        hbox.set_valign(Gtk.Align.END)

        window.add(vgrid)

        window.connect("destroy", self.destroyWindow, window)

    def destroyWindow(self, widget, window):
        window.destroy()

    def setProperties(self, button, widgets):
        pass

class SFMLMakeObject(Gtk.DrawingArea):
    def __init__(self, tileSize, numberCase, nameObject):
        Gtk.DrawingArea.__init__(self)
        self.set_can_focus(True)
        self.tileSize = tileSize
        self.numberCase = numberCase
        self.render = sf.HandledWindow()
        self.size = tileSize*numberCase
        self.listTile = list()
        self.nameObject = nameObject

        self.tileMoving = None
        self.posMoving = None
        self.indiceTile = None

        self.connect("motion_notify_event", self.mouseMoveEvent) 
        self.connect("button-press-event", self.buttonPressEvent)
        self.connect("button-release-event", self.buttonReleaseEvent)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        for i in range(numberCase.x):
            self.listTile.append(list())
            for j in range(numberCase.y):
                self.listTile[-1].append(None)

        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        targets = Gtk.TargetList.new([])
        targets.add_image_targets(0, True)

        self.drag_dest_set_target_list(targets)
        self.timeoutUpdate = GObject.timeout_add(100, self.update)

        self.set_size_request(self.size.x, self.size.y)

    def update(self):
        self.render.empty_event_loop()
        self.render.clear()
        for listTile in self.listTile:
            for tile in listTile:
                if tile:
                    tile.update()
        self.drawQuad()
        self.render.display()
        return True

    def do_drag_data_received(self, context, x, y, selection_data, info, time=None):
        dndDatas = TileBox.dndDatas
        if dndDatas["style"] == "Object":
            return

        pos = self.render.map_pixel_to_coords(sf.Vector2(x, y), self.render.view)
        indice = sf.Vector2(\
                int(pos.x/self.tileSize.x), int(pos.y/self.tileSize.y))
        
        self.listTile[indice.x][indice.y]=StaticTile(dndDatas['tileID'],\
                indice*self.tileSize, dndDatas['subRect'],\
                TileBox.textureList[dndDatas['name']], dndDatas['fileName'], True, self)

    def mouseMoveEvent(self, widget, event):
        if self.tileMoving:
            self.tileMoving.position = sf.Vector2(event.x, event.y)

    def buttonPressEvent(self, widget, event):
        if event.button == 1:
            print(event.x, event.y)
            if len(self.listTile) and globalVar.tileWindow.mode == "Print":
                b = False
                for i in range(len(self.listTile)):
                    for j in range(len(self.listTile[0])):
                        if self.listTile[i][j]:
                            if isMouseInRect(sf.Vector2(event.x, event.y),\
                                    self.listTile[i][j].rect):
                                self.tileMoving = self.listTile[i][j]
                                self.indiceTile = sf.Vector2(i, j)
                                self.posMoving = sf.Vector2(event.x, event.y) -\
                                        self.tileMoving.position
                                b=True
                                break
                    if b:
                        break

            elif globalVar.tileWindow.mode == "Eraser":
                self.removeTile(event.x, event.y)

    def buttonReleaseEvent(self, widget, event):
        if event.button == 1:
            if self.tileMoving:
                coord = sf.Vector2(event.x, event.y)
                indice = sf.Vector2(int(event.x/self.tileSize.x), int(event.y/self.tileSize.y))

                self.listTile[self.indiceTile.x][self.indiceTile.y] = None
                self.listTile[indice.x][indice.y] = self.tileMoving

                self.tileMoving.position = self.tileSize * indice
                self.tileMoving = None

    def removeTile(self, x, y):
        indice = sf.Vector2(int(x/self.tileSize.x), int(y/self.tileSize.y))

        if len(self.listTile) > indice.x and len(self.listTile[indice.x]) > indice.y:
            self.listTile[indice.x][indice.y] = None

    def drawQuad(self):
        position = sf.Vector2(0, 0)
        size = self.size

        posX = max(self.tileSize.x * int(position.x/self.tileSize.x), 0)
        posY = max(self.tileSize.y * int(position.y/self.tileSize.y), 0)

        lineX = sf.VertexArray(sf.PrimitiveType.LINES, 2)
        lineY = sf.VertexArray(sf.PrimitiveType.LINES, 2)
        lineX[0].color = sf.Color.WHITE
        lineX[1].color = sf.Color.WHITE
        lineX[0].position = sf.Vector2(posX, max(position.y, 0))
        lineX[1].position = sf.Vector2(posX, min(position.y+size.y, self.size.y))

        while lineX[0].position.x < position.x + size.x and not lineX[0].position.x > self.size.x:
            self.render.draw(lineX)
            lineX[0].position += sf.Vector2(self.tileSize.x, 0)
            lineX[1].position += sf.Vector2(self.tileSize.x, 0)

        lineY[0].color = sf.Color.WHITE
        lineY[1].color = sf.Color.WHITE
        lineY[0].position = sf.Vector2(max(position.x, 0), posY)
        lineY[1].position = sf.Vector2(min(position.x+size.x, self.size.x), posY)

        while lineY[0].position.y < position.y + size.y and not lineY[0].position.y > self.size.y:
            self.render.draw(lineY)
            lineY[0].position += sf.Vector2(0, self.tileSize.y)
            lineY[1].position += sf.Vector2(0, self.tileSize.y)

    def do_size_allocate(self, allocation):
        allocation.width = min(allocation.width, self.size.x)
        allocation.height = min(allocation.height, self.size.y)
        if not 0 in self.render.size:
            self.checkViewSize()
        else:
            alloc = sf.Vector2(allocation.width, allocation.height)
            self.render.view.size = alloc
            self.render.view.center = alloc/2
        self.render.size = sf.Vector2(allocation.width, allocation.height)
        Gtk.DrawingArea.do_size_allocate(self, allocation)

    def checkViewSize(self):
        if self.render.view.size.x > self.size.x or self.render.view.size.y > self.size.y:
            self.render.view.zoom(min(self.size.x / self.render.view.size.x,\
                    self.size.y / self.render.view.size.y))
