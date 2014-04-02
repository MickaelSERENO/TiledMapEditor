from gi.repository import Gtk, Gdk, GObject
import sfml as sf
from TileBox import TileBox
from TraceTile import *
from copy import copy
from TraceTile import StaticTrace, Tile, DynamicTrace
import globalVar

class SFMLArea(Gtk.DrawingArea):
    def __init__(self, hslide, vslide, numberCases, sizeCase):
        Gtk.DrawingArea.__init__(self)
        self.hslide = hslide
        self.vslide = vslide
        self.render = sf.HandledWindow()
        self.size = numberCases * sizeCase
        self.sizeCase = sizeCase
        self.numberCases = numberCases
        self.set_can_focus(True)

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

    def setSlideProperties(self):
        self.vslide.connect("value-changed", self.moveView, "vertical")
        self.hslide.connect("value-changed", self.moveView, "horizontal")
        self.vslide.connect("size-allocate", self.setScrollSizeAllocated, "vertical")
        self.hslide.connect("size-allocate", self.setScrollSizeAllocated, "horizontal")
        self.hslide.set_slider_size_fixed(True)
        self.vslide.set_slider_size_fixed(True)

    def setSFMLSize(self, numberCases=None):
        if numberCases:
            self.size = numberCases * self.sizeCase
            for trace in self.listTrace:
                trace.initStaticList(self.sizeCase)
        self.render.size.x = min(self.render.size.x, self.size.x)
        self.render.size.y = min(self.render.size.y, self.size.y)
        self.render.view.size = copy(self.render.size)
        self.get_toplevel().show_all()
        self.updateSlideValues()

    def setScrollSizeAllocated(self, widget, allocation, scroll):
        if scroll == "vertical":
            self.vslide.set_min_slider_size(allocation.height*self.render.view.size.y/self.size.y)

        else:
            self.hslide.set_min_slider_size(allocation.width*self.render.view.size.x/self.size.x)


    def setMode(self, mode):
        self.mode = mode

    def updateSlideValues(self):
        self.vslide.set_adjustment(Gtk.Adjustment(self.render.view.center.y - self.render.view.size.y/2,\
                0, self.size.y - self.render.view.size.y, 1, 10, 0))
        self.hslide.set_adjustment(Gtk.Adjustment(self.render.view.center.x - self.render.view.size.x/2,\
                0, self.size.x - self.render.view.size.x, 1, 10, 0))

        self.setScrollSizeAllocated(self.vslide, self.vslide.get_allocation(), "vertical")
        self.setScrollSizeAllocated(self.hslide, self.hslide.get_allocation(), "horizontal")

    def moveView(self, scroll, orientation):
        vector = sf.Vector2()
        if orientation == "vertical":
            vector.y = scroll.get_value() - \
                    (self.render.view.center.y - self.render.view.size.y / 2)
        elif orientation=="horizontal":
            vector.x = scroll.get_value() - \
                    (self.render.view.center.x - self.render.view.size.x / 2)

        self.render.view.move(vector.x, vector.y)

    def makePopupAction(self, actionGroup):
        actionGroup.get_action("DelCase").connect("activate", self.manageTile, "delete")

    def makePopup(self, uiManager, eventBox):
        self.popupFull = uiManager.get_widget("/SFMLFullCase")
        self.popupEmpty = uiManager.get_widget("/SFMLEmptyCase")
        eventBox.connect("button-press-event", self.buttonPressEvent)

    def do_size_allocate(self, allocation):
        allocation.width = min(allocation.width, self.size.x)
        allocation.height = min(allocation.height, self.size.y)
        if not 0 in self.render.size:
            self.render.view.size *= sf.Vector2(allocation.width, allocation.height) / \
                    sf.Vector2(self.get_allocated_width(), self.get_allocated_height())
            self.render.view.move(self.hslide.get_value() -\
                (self.render.view.center.x - self.render.view.size.x/2), \
                self.vslide.get_value() - (self.render.view.center.y - self.render.view.size.y/2))
            self.checkViewSize()
        else:
            alloc = sf.Vector2(allocation.width, allocation.height)
            self.render.view.size = alloc
            self.render.view.center = alloc/2
        self.render.size = sf.Vector2(allocation.width, allocation.height)
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

        if self.render.view.center.x - self.render.view.size.x/2 < 0:
            self.render.view.center = sf.Vector2(self.render.view.size.x/2,\
                    self.render.view.center.y)
        elif self.render.view.center.x + self.render.view.size.x/2 > self.size.x:
            self.render.view.center = sf.Vector2(self.size.x - self.render.view.size.x/2,\
                    self.render.view.center.y)
        if self.render.view.center.y - self.render.view.size.y/2 < 0:
            self.render.view.center = sf.Vector2(self.render.view.center.x, \
                    self.render.view.size.y/2)
        elif self.render.view.center.y + self.render.view.size.y/2 > self.size.y:
            self.render.view.center = sf.Vector2(self.render.view.center.x, \
                    self.size.y - self.render.view.size.y/2)
        self.updateSlideValues()

    def checkViewSize(self):
        if self.render.view.size.x > self.size.x or self.render.view.size.y > self.size.y:
            self.render.view.zoom(min(self.size.x / self.render.view.size.x,\
                    self.size.y / self.render.view.size.y))
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
            for trace in self.listTrace[::-1]:
                if trace.show:
                    pos = self.convertCoord(sf.Vector2(x, y))
                    trace.addTile(pos.x, pos.y)
                    return

    def convertCoord(self, coord):
        return self.render.map_pixel_to_coords(coord, self.render.view)

    def manageTile(self, action):
        pass

    def buttonPressEvent(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 3:
                self.popupEmpty.popup(None, None, None, None, event.button, event.time)
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


    def addStaticTrace(self, tileSize, shift):
        self.listTrace.append(StaticTrace(tileSize, shift))
        self.listTrace[-1].initStaticList(self.size - shift)

    def addDynamicTrace(self):
        self.listTrace.append(DynamicTrace())

class SFMLMakeObject(Gtk.DrawingArea):
    def __init__(self, tileSize, numberCase, nameObject):
        Gtk.DrawingArea.__init__(self)
        self.tileSize = tileSize
        self.numberCase = numberCase
        self.render = sf.HandledWindow()
        self.size = tileSize*numberCase
        self.listTile = list()
        self.nameObject = nameObject

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
        for tileList in self.listTile:
            for tile in tileList:
                if tile:
                    tile.update()
        self.drawQuad()
        self.render.display()
        return True

    def do_drag_data_received(self, context, x, y, selection_data, info, time=None):
        pos = self.render.map_pixel_to_coords(sf.Vector2(x, y), self.render.view)
        dndDatas = TileBox.dndDatas
        indice = sf.Vector2(\
                int(pos.x/self.tileSize.x), int(pos.y/self.tileSize.y))

        self.listTile[indice.x][indice.y]=StaticTile(dndDatas['tileID'],\
                indice*self.tileSize, dndDatas['subRect'],\
                TileBox.textureList[dndDatas['name']], dndDatas['fileName'], True, self)

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
