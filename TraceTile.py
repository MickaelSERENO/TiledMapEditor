from gi.repository import Gtk, Gdk, GObject
import sfml as sf
from TileBox import TileBox
from copy import copy
import functions
import globalVar

class Trace:
    def __init__(self, name):
        self.show = True
        self.tileMoving = None
        self.posMoving = sf.Vector2(0, 0)
        self.name = name

    def update(self):
        if not self.show:
            return False
        return True

    def updateEventTile(self, event):
        if event.type == Gdk.EventType.MOTION_NOTIFY:
            if self.tileMoving:
                self.tileMoving.position = globalVar.sfmlArea.convertCoord(sf.Vector2(event.x, event.y)) - self.posMoving

        if event.type == Gdk.EventType.BUTTON_RELEASE:
            if self.tileMoving:
                self.tileMoving = None

    def addTile(self, x, y):
        return

    def drawQuad(self):
        return

class StaticTrace(Trace):
    def __init__(self, tileSize, shift, name):
        Trace.__init__(self, name)
        self.listStaticTile = list(list())
        self.tileSize = tileSize
        self.show = True
        self.tileMoving = None
        self.indiceTile = None
        self.posMoving = sf.Vector2(0, 0)
        self.style="Static"
        self.leftMousePress = False
        self.controlKey = False
        self.shift = shift

    def drawQuad(self):
        position = globalVar.sfmlArea.render.view.center -\
                globalVar.sfmlArea.render.view.size / 2
        size = globalVar.sfmlArea.render.view.size

        posX = max(self.tileSize.x * int(position.x/self.tileSize.x), 0) + self.shift.x
        posY = max(self.tileSize.y * int(position.y/self.tileSize.y), 0) + self.shift.y

        lineX = sf.VertexArray(sf.PrimitiveType.LINES, 2)
        lineY = sf.VertexArray(sf.PrimitiveType.LINES, 2)
        lineX[0].color = sf.Color.WHITE
        lineX[1].color = sf.Color.WHITE

        delete = 0
        if self.shift.y > 0:
            delete = self.tileSize.y - self.shift.y
        lineX[0].position = sf.Vector2(posX, max(position.y+max(self.shift.y-position.y, 0), 0))
        lineX[1].position = sf.Vector2(posX, min(position.y+size.y, globalVar.sfmlArea.size.y - \
                delete))

        while lineX[0].position.x < position.x + size.x:
            globalVar.sfmlArea.render.draw(lineX)
            lineX[0].position += sf.Vector2(self.tileSize.x, 0)
            lineX[1].position += sf.Vector2(self.tileSize.x, 0)

        lineY[0].color = sf.Color.WHITE
        lineY[1].color = sf.Color.WHITE

        if self.shift.x > 0:
            delete = self.tileSize.x - self.shift.x
        lineY[0].position = sf.Vector2(max(position.x + max(self.shift.x-position.x, 0), 0), posY)
        lineY[1].position = sf.Vector2(min(position.x+size.x, globalVar.sfmlArea.size.x - delete), posY)

        while lineY[0].position.y < position.y + size.y and not lineY[0].position.y > globalVar.sfmlArea.size.y:
            globalVar.sfmlArea.render.draw(lineY)
            lineY[0].position += sf.Vector2(0, self.tileSize.y)
            lineY[1].position += sf.Vector2(0, self.tileSize.y)

    def addTile(self, x, y, fromDnd = True):
        dndDatas = TileBox.dndDatas
        if not dndDatas:
            return
        if not fromDnd and globalVar.sfmlArea.mode != "Print":
            return

        self.addTileFromDnd(x, y, dndDatas)

    def addTileFromDnd(self, x, y, dndDatas):
        if not dndDatas:
            return

        if x < self.shift.x or x > len(self.listStaticTile) * self.tileSize.x + self.shift.x or\
                y < self.shift.y or y > len(self.listStaticTile[0]) * self.tileSize.y + self.shift.y:
            return
        indice = sf.Vector2(\
                int((x-self.shift.x)/self.tileSize.x), int((y-self.shift.y)/self.tileSize.y))

        if not(len(self.listStaticTile) > indice.x and len(self.listStaticTile[indice.x]) > indice.y):
            return

        if dndDatas['style']=='Static':
            self.listStaticTile[indice.x][indice.y]=StaticTile(dndDatas['tileID'],\
                    indice*self.tileSize+self.shift, dndDatas['subRect'],\
                    TileBox.textureList[dndDatas['name']], dndDatas['fileName'])

        elif dndDatas['style'] == 'Object':
            for x in range(int(dndDatas['numberCase'].x)):
                if indice.x + x < len(self.listStaticTile):
                    for y in range(int(dndDatas['numberCase'].y)):
                        if indice.y + y < len(self.listStaticTile[x]):
                            self.listStaticTile[indice.x + x][indice.y + y] = None
            self.listStaticTile[indice.x][indice.y]=ObjectTile(dndDatas['objectTexture'],\
                    indice*self.tileSize+self.shift, dndDatas['name'], dndDatas['numberCase'])

            print(self.listStaticTile[indice.x][indice.y].position)

    def updateEventTile(self, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 1:
                self.leftMousePress = True
                if len(self.listStaticTile) and not self.controlKey and globalVar.sfmlArea.mode == "Print":
                    b = False
                    for i in range(len(self.listStaticTile)):
                        for j in range(len(self.listStaticTile[0])):
                            if self.listStaticTile[i][j]:
                                if functions.isMouseInRect(globalVar.sfmlArea.convertCoord(sf.Vector2(event.x, event.y)),\
                                        self.listStaticTile[i][j].rect):
                                    self.tileMoving = self.listStaticTile[i][j]
                                    self.indiceTile = sf.Vector2(i, j)
                                    self.posMoving = globalVar.sfmlArea.convertCoord(sf.Vector2(event.x, event.y)) -\
                                            self.tileMoving.position
                                    b=True
                                    break
                        if b:
                            break

                if self.controlKey and self.leftMousePress:
                    coord = globalVar.sfmlArea.convertCoord(sf.Vector2(event.x, event.y))
                    self.addTile(coord.x, coord.y)

                if globalVar.sfmlArea.mode == "Eraser":
                    self.removeTile(event.x, event.y)

        if event.type == Gdk.EventType.BUTTON_RELEASE:
            if event.button == 1:
                self.leftMousePress = False
                if self.tileMoving:
                    coord = globalVar.sfmlArea.convertCoord(sf.Vector2(event.x, event.y))
                    indice = sf.Vector2(min(\
                            int(max((self.tileMoving.position.x, self.shift.x)) / self.tileSize.x),\
                            len(self.listStaticTile)-1),\
                            \
                            min(int(max((self.tileMoving.position.y), self.shift.y) / self.tileSize.y), \
                            len(self.listStaticTile[0])-1))

                    self.listStaticTile[self.indiceTile.x][self.indiceTile.y] = None

                    if type(self.tileMoving) is ObjectTile:
                        print(self.tileMoving.numberCase)
                        for x in range(int(self.tileMoving.numberCase.x)):
                            if indice.x + x < len(self.listStaticTile):
                                for y in range(int(self.tileMoving.numberCase.y)):
                                    if indice.y + y < len(self.listStaticTile[x]):
                                        self.listStaticTile[indice.x + x][indice.y + y] = None

                    self.listStaticTile[indice.x][indice.y] = self.tileMoving


                    self.tileMoving.position = self.tileSize * indice + self.shift


        if event.type == Gdk.EventType.KEY_PRESS:
            if event.get_keyval()[1] ==  Gdk.KEY_Control_L:
                print("val")
                self.controlKey = True

        if event.type == Gdk.EventType.KEY_RELEASE:
            if event.get_keyval()[1] ==  Gdk.KEY_Control_L:
                self.controlKey = False

        if event.type == Gdk.EventType.MOTION_NOTIFY:
            if self.leftMousePress and globalVar.sfmlArea.mode == "Eraser":
                self.removeTile(event.x, event.y)

            elif self.controlKey and self.leftMousePress:
                coord = globalVar.sfmlArea.convertCoord(sf.Vector2(event.x, event.y))
                self.addTile(coord.x, coord.y)

        Trace.updateEventTile(self, event)

    def update(self):
        if not Trace.update(self):
            return
        self.drawQuad()
        for tile in [tile for content in self.listStaticTile for tile in content]:
            if tile and tile is not self.tileMoving:
                tile.update()
        if self.tileMoving:
            self.tileMoving.update()

    def initStaticList(self, size):
        for x in range(0, int(size.x/self.tileSize.x)):
            if self.shift.x + x * self.tileSize.x > size.x:
                break
            self.listStaticTile.append(list())
            for x in self.listStaticTile:
                for y in range(len(x), int(size.y/self.tileSize.y)):
                    if self.shift.y + y * self.tileSize.y > size.y:
                        break
                    x.append(None)

    def removeTile(self, x, y):
        coord = globalVar.sfmlArea.convertCoord(sf.Vector2(x, y))
        indice = sf.Vector2(\
                int((coord.x-self.shift.x)/self.tileSize.x), int((coord.y-self.shift.y)/self.tileSize.y))

        if len(self.listStaticTile) > indice.x and len(self.listStaticTile[indice.x]) > indice.y:
            self.listStaticTile[indice.x][indice.y] = None


class DynamicTrace(Trace):
    def __init__(self, name):
        Trace.__init__(self, name)
        self.listDynamicTile = list()
        self.style="Dynamic"

    def update(self):
        if not Trace.update(self):
            return
        for tile in self.listDynamicTile:
            if tile is not self.tileMoving:
                tile.update()

        if self.tileMoving:
            self.tileMoving.update


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
        print("ok")
        self.makeAddTileWindowPrompt(x, y)

    def makeAddTileWindowPrompt(self, x, y):
        dndDatas = TileBox.dndDatas
        if dndDatas['style'] == "Static" or dndDatas['style']=='Object':
            return self.addStaticTile(x, y)
        window = Gtk.Window(title="Animation")
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
        if dndDatas['style'] == 'Static':
            self.listDynamicTile.append(StaticTile(dndDatas['tileID'],\
                    sf.Vector2(x, y), dndDatas['subRect'],\
                    TileBox.textureList[dndDatas['name']], dndDatas['fileName']))
        elif dndDatas['style'] == 'Object':
            self.listDynamicTile.append(ObjectTile(dndDatas['objectTexture'],\
                    sf.Vector2(x, y), dndDatas['name']))

    def confirmDynamicTile(self, button, widgets):
        dndDatas = TileBox.dndDatas
        origin = sf.Vector2(widgets['xOriginEntry'].get_value(), widgets['yOriginEntry'].get_value())
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
    def __init__(self, texture, position, name, numberCase, sfmlRenderer = "sfmlArea"):
        self.name = name
        self.sprite = sf.Sprite(texture)
        if sfmlRenderer == 'sfmlArea':
            self.sfmlRenderer = globalVar.sfmlArea
        else:
            self.sfmlRenderer = sfmlRenderer
        self.position = position
        self.numberCase = numberCase

    def update(self):
        if self.sfmlRenderer:
            self.sfmlRenderer.render.draw(self.sprite)

    def setPosition(self, position):
        self.sprite.position = position

    position = property(lambda self : self.sprite.position, setPosition)
    rect = property(lambda self : self.sprite.global_bounds)

class MakedObjectTile():
    def __init__(self, texture, tileSize, numberCase, tileID, fileName, name, typeName):
        self.texture = texture
        self.sprite = sf.Sprite(texture)
        self.tileID = tileID
        self.fileName = fileName
        self.typeObject = typeName
        self.nameObject = name
        self.numberCase = numberCase
        self.tileSize = tileSize

    def setPosition(self, position):
        self.sprite.position = position

    rect = property(lambda self : self.sprite.global_bounds)
