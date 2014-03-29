from gi.repository import Gtk, Gdk, GObject
import sfml as sf
from TileBox import TileBox
from copy import copy
import functions
import globalVar

class Trace:
    def __init__(self):
        self.show = True
        self.tileMoving = None
        self.posMoving = sf.Vector2(0, 0)

    def update(self):
        if not self.show:
            return False
        return True

    def updateEventTile(self, event):
        if event.type == Gdk.EventType.MOTION_NOTIFY:
            if self.tileMoving:
                self.tileMoving.position = sf.Vector2(event.x, event.y) - self.posMoving

        if event.type == Gdk.EventType.BUTTON_RELEASE:
            if self.tileMoving:
                self.tileMoving = None

    def addTile(self, x, y):
        return

    def drawQuad(self):
        return

class StaticTrace(Trace):
    def __init__(self, tileSize):
        Trace.__init__(self)
        self.listStaticTile = list(list())
        self.tileSize = tileSize
        self.show = True
        self.tileMoving = None
        self.indiceTile = None
        self.posMoving = sf.Vector2(0, 0)
        self.style="Static"

    def drawQuad(self):
        position = globalVar.sfmlArea.render.view.center - globalVar.sfmlArea.render.view.size / 2
        size = globalVar.sfmlArea.render.view.size

        posX = max(self.tileSize.x * int(position.x/self.tileSize.x), 0)
        posY = max(self.tileSize.y * int(position.y/self.tileSize.y), 0)

        lineX = sf.VertexArray(sf.PrimitiveType.LINES, 2)
        lineY = sf.VertexArray(sf.PrimitiveType.LINES, 2)
        lineX[0].color = sf.Color.WHITE
        lineX[1].color = sf.Color.WHITE
        lineX[0].position = sf.Vector2(posX, max(position.y, 0))
        lineX[1].position = sf.Vector2(posX, min(position.y+size.y, globalVar.sfmlArea.size.y))

        while lineX[0].position.x < position.x + size.x and not lineX[0].position.x > globalVar.sfmlArea.size.x:
            globalVar.sfmlArea.render.draw(lineX)
            lineX[0].position += sf.Vector2(self.tileSize.x, 0)
            lineX[1].position += sf.Vector2(self.tileSize.x, 0)

        lineY[0].color = sf.Color.WHITE
        lineY[1].color = sf.Color.WHITE
        lineY[0].position = sf.Vector2(max(position.x, 0), posY)
        lineY[1].position = sf.Vector2(min(position.x+size.x, globalVar.sfmlArea.size.x), posY)

        while lineY[0].position.y < position.y + size.y and not lineY[0].position.y > globalVar.sfmlArea.size.y:
            globalVar.sfmlArea.render.draw(lineY)
            lineY[0].position += sf.Vector2(0, self.tileSize.y)
            lineY[1].position += sf.Vector2(0, self.tileSize.y)

    def addTile(self, x, y):
        dndDatas = TileBox.dndDatas
        indice = sf.Vector2(\
                int(x/self.tileSize.x), int(y/self.tileSize.y))

        if dndDatas['style']=='Static':
            self.listStaticTile[indice.x][indice.y]=StaticTile(dndDatas['tileID'],\
                    indice*self.tileSize, dndDatas['subRect'],\
                    TileBox.textureList[dndDatas['name']], dndDatas['fileName'])

        elif dndDatas['style'] == 'Object':
            self.listStaticTile[indice.x][indice.y]=ObjectTile(dndDatas['objectTexture'],\
                    indice*self.tileSize, dndDatas['name'])

    def updateEventTile(self, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 1:
                self.tileMoving = self.listStaticTile[int(event.x / self.tileSize.x)][int(event.y / self.tileSize.y)]
                if self.tileMoving: 
                    self.indiceTile = sf.Vector2(int(event.x / self.tileSize.x), int(event.y / self.tileSize.y))
                    self.posMoving = sf.Vector2(event.x, event.y) - self.indiceTile * self.tileSize

        if event.type == Gdk.EventType.BUTTON_RELEASE:
            if self.tileMoving:
                self.listStaticTile[self.indiceTile.x][self.indiceTile.y] = None
                self.listStaticTile[int(event.x / self.tileSize.x)][int(event.y / self.tileSize.y)] = self.tileMoving
                self.tileMoving.position = sf.Vector2(self.tileSize.x * int(event.x / self.tileSize.x),\
                        self.tileSize.y * int(event.y / self.tileSize.y))

        Trace.updateEventTile(self, event)

    def update(self):
        if not Trace.update(self):
            return
        self.drawQuad()
        for tile in [tile for content in self.listStaticTile for tile in content]:
            if tile:
                tile.update()

    def initStaticList(self, size):
        for x in range(len(self.listStaticTile), int(size.x/self.tileSize.x)):
            self.listStaticTile.append(list())
            for x in self.listStaticTile:
                for y in range(len(x), int(size.y/self.tileSize.y)):
                    x.append(None)

class DynamicTrace(Trace):
    def __init__(self):
        Trace.__init__(self)
        self.listDynamicTile = list()
        self.style="Dynamic"

    def update(self):
        if not Trace.update(self):
            return
        for tile in self.listDynamicTile:
            if tile:
                tile.update()

    def updateEventTile(self, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 1:
                for tile in self.listDynamicTile[::-1]:
                    if functions.isMouseInRect(sf.Vector2(event.x, event.y),\
                            tile.rect):
                        self.tileMoving = tile
                        self.posMoving = sf.Vector2(event.x, event.y) - tile.position
                        break

        if event.type == Gdk.EventType.BUTTON_RELEASE:
            if self.tileMoving:
                self.tileMoving.position = sf.Vector2(event.x, event.y) - self.posMoving
 
        Trace.updateEventTile(self, event)

    def addTile(self, x, y):
        self.makeAddTileWindowPrompt(x, y)

    def makeAddTileWindowPrompt(self, x, y):
        dndDatas = TileBox.dndDatas
        if dndDatas['style'] == "Static" or dndDatas['style']=='Object':
            return self.addStaticTile(x, y)
        window = Gtk.Window(title="Annimation")
        window.set_property('modal', True)

        accelGroup = Gtk.AccelGroup()
        window.add_accel_group(accelGroup)

        vgrid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        grid = Gtk.Grid()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_halign(Gtk.Align.END)

        vgrid.add(grid)
        vgrid.add(hbox)

        timeLabel = Gtk.Label("Time (ms)")
        adjustmentTime = Gtk.Adjustment(1, 1, 10000, 1, 100, -1)
        timeEntry = Gtk.SpinButton(adjustment = adjustmentTime)

        originLabel = Gtk.Label("Origin")
        xLabel = Gtk.Label('x')
        xAdjustmentOrigin = Gtk.Adjustment(0, 0, 100, 1, 10, -1)
        yAdjustmentOrigin = Gtk.Adjustment(0, 0, 100, 1, 10, -1)
        xOriginEntry = Gtk.SpinButton(adjustment = xAdjustmentOrigin)
        yOriginEntry = Gtk.SpinButton(adjustment = yAdjustmentOrigin)

        widgets = dict()
        widgets['timeEntry'] = timeEntry
        widgets['xOriginEntry'] = xOriginEntry
        widgets['yOriginEntry'] = yOriginEntry
        widgets['position'] = sf.Vector2(x, y)
        widgets['window'] = window

        okButton = Gtk.Button(label='OK')
        cancelButton = Gtk.Button(label="Cancel")

        grid.attach(timeLabel, 0, 0, 1, 1)
        grid.attach_next_to(timeEntry, timeLabel, Gtk.PositionType.RIGHT, 3, 1)
        grid.attach_next_to(originLabel, timeLabel, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(xOriginEntry, originLabel, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(xLabel, xOriginEntry, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(yOriginEntry, xLabel, Gtk.PositionType.RIGHT, 1, 1)

        hbox.pack_start(okButton, False, False, 0)
        hbox.pack_start(cancelButton, False, False, 0)

        window.connect("destroy", lambda event, w : w.destroy(), window)
        okButton.connect('clicked', self.confirmDynamicTile, widgets)
        cancelButton.connect('clicked', lambda button, w : w.destroy(), window)

        cancelButton.add_accelerator("activate", accelGroup, Gdk.KEY_Escape, 0, \
                Gtk.AccelFlags.MASK)
        okButton.add_accelerator("activate", accelGroup, Gdk.KEY_Return, 0, \
                Gtk.AccelFlags.VISIBLE)
        okButton.add_accelerator("activate", accelGroup, Gdk.KEY_KP_Enter, 0, \
                Gtk.AccelFlags.VISIBLE)

        window.add(vgrid)
        window.show_all()

    def addStaticTile(self, x, y):
        dndDatas = TileBox.dndDatas
        if dndDatas == 'Static':
            self.listDynamicTile.append(StaticTile(dndDatas['tileID'],\
                    sf.Vector2(x, y), dndDatas['subRect'],\
                    TileBox.textureList[dndDatas['name']], dndDatas['fileName']))
        elif dndDatas == 'Object':
            self.listDynamicTile.append(ObjectTile(dndDatas['objectTexture'],\
                    sf.Vector2(x, y), dndDatas['name']))


    def confirmDynamicTile(self, button, widgets):
        dndDatas = TileBox.dndDatas
        origin = sf.Vector2(widgets['xOriginEntry'].get_value(), widgets['yOriginEntry'].get_value())
        print(dndDatas['fileName'])
        self.listDynamicTile.append(DynamicTile(dndDatas['tileID'], \
                widgets['timeEntry'].get_value(), origin, widgets['position'],\
                dndDatas['subRect'], TileBox.textureList[dndDatas['fileName']], dndDatas['fileName'],\
                dndDatas['animName']))
        if 'window' in widgets:
            widgets['window'].destroy()

class Tile:
    def __init__(self, tileID, position, subRect, texture, fileName, madeByObject=False, \
            sfmlRenderer='sfmlArea'):
        self.sprite = sf.Sprite(texture)
        self.sprite.texture_rectangle = subRect
        self.tileID = tileID
        self.sprite.position = position
        self.fileName = fileName
        self.madeByObject = madeByObject
        if sfmlRenderer == 'sfmlArea':
            self.sfmlRenderer = globalVar.sfmlArea
        else:
            self.sfmlRenderer = sfmlRenderer

    def update(self):
        self.sfmlRenderer.render.draw(self.sprite)

    def setPosition(self, position):
        self.sprite.position = position

    position = property(lambda self : self.sprite.position, setPosition)
    rect = property(lambda self : self.sprite.global_bounds)

class StaticTile(Tile):
    def __init__(self, tileID, position, subRect, texture, fileName,\
            madeByObject=False, sfmlRenderer='sfmlArea'):
        Tile.__init__(self, tileID, position, subRect, texture, fileName, \
                madeByObject, sfmlRenderer)
        self.style = "Static"

class DynamicTile(Tile):
    def __init__(self, tileID, animTime, origin, position, subRect, texture, fileName, animName,\
            madeByObject=False, sfmlRenderer='sfmlArea'):
        Tile.__init__(self, tileID, position, subRect, texture, fileName, madeByObject, sfmlRenderer)
        self.style = "Dynamic"
        self.animTime = animTime
        self.origin = origin
        self.animName = animName

class ObjectTile():
    def __init__(self, texture, position, name, sfmlRenderer = "sfmlArea"):
        self.name = name
        self.sprite = sf.Sprite(texture)
        if sfmlRenderer == 'sfmlArea':
            self.sfmlRenderer = globalVar.sfmlArea
        else:
            self.sfmlRenderer = sfmlRenderer
        self.position = position

    def update(self):
        self.sfmlRenderer.render.draw(self.sprite)

    def setPosition(self, position):
        self.sprite.position = position

    position = property(lambda self : self.sprite.position, setPosition)
    rect = property(lambda self : self.sprite.global_bounds)

class MakedObjectTile():
    def __init__(self, texture, tileList, sfmlRenderer):
        self.tileList = list()
        for i in range(len(tileList)):
            self.tileList.append(list())
            for j in range(len(tileList[0])):
                self.tileList[-1].append(tileList[i][j])

        self.texture = texture
        self.sprite = sf.Sprite(texture)
        self.sfmlRenderer = sfmlRenderer

    def update(self):
        self.sfmlRenderer.render.draw(self.sprite)

    def setPosition(self, position):
        self.sprite.position = position

    position = property(lambda self : self.sprite.position, setPosition)
    rect = property(lambda self : self.sprite.global_bounds)
