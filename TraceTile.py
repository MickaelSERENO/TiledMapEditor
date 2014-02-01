from gi.repository import Gtk, Gdk, GObject
import sfml as sf
from TileBox import TileBox
from copy import copy
import functions
import globalVar

class Trace:
    def __init__(self, tileSize, style):
        self.style = style
        self.listStaticTile = list(list())
        self.listDynamicTile = list()
        self.tileSize = tileSize
        self.show = True
        self.tileMoving = None
        self.indiceTile = None
        self.posMoving = sf.Vector2(0, 0)

    def update(self):
        if not self.show:
            return
        self.drawQuad()
        if self.style == "Static":
            for tile in [tile for content in self.listStaticTile for tile in content]:
                if tile:
                    tile.update()
        else:
            for tile in self.listDynamicTile:
                if tile:
                    tile.update()

    def updateEventTile(self, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 1:
                print(1)
                if self.style == "Static":
                    self.tileMoving = self.listStaticTile[int(event.x / self.tileSize.x)][int(event.y / self.tileSize.y)]
                    if self.tileMoving: 
                        self.indiceTile = sf.Vector2(int(event.x / self.tileSize.x), int(event.y / self.tileSize.y))
                        self.posMoving = sf.Vector2(event.x, event.y) - self.indiceTile * self.tileSize

                else:
                    for tile in self.listDynamicTile[::-1]:
                        if function.isMouseInRect(sf.Vector2(event.x, event.y), sf.Rect(tile.position, self.tileSize)):
                            self.tileMoving = tile
                            break

        if event.type == Gdk.EventType.MOTION_NOTIFY:
            if self.tileMoving:
                self.tileMoving.position = sf.Vector2(event.x, event.y) - self.posMoving

        if event.type == Gdk.EventType.BUTTON_RELEASE:
            if self.tileMoving:
                if self.style == "Static":
                    self.listStaticTile[self.indiceTile.x][self.indiceTile.y] = None
                    self.listStaticTile[int(event.x / self.tileSize.x)][int(event.y / self.tileSize.y)] = self.tileMoving
                    self.tileMoving.position = sf.Vector2(self.tileSize.x * int(event.x / self.tileSize.x),\
                            self.tileSize.y * int(event.y / self.tileSize.y))
                self.tileMoving = None

    def addTile(self, x, y):
        dndDatas = TileBox.dndDatas
        if self.style=="Static" and dndDatas[style] == "Static":
            indice = sf.Vector2(\
                    int(x/self.tileSize.x), int(y/self.tileSize.y))

            self.listStaticTile[indice.x][indice.y]=Tile(self, indice*self.tileSize, TileBox.dndDatas['subRect'], \
                    TileBox.textureList[TileBox.dndDatas['file']])
        elif self.style=="Dynamic":
            position = sf.Vector2(x, y)

    def initStaticList(self, size):
        for x in range(len(self.listStaticTile), int(size.x/self.tileSize.x)):
            self.listStaticTile.append(list())
            for x in self.listStaticTile:
                for y in range(len(x), int(size.y/self.tileSize.y)):
                    x.append(None)

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

class Tile:
    def __init__(self, parent, position, subRect, texture):
        self.sprite = sf.Sprite(texture)
        self.sprite.texture_rectangle = subRect
        self.sprite.position = position

    def update(self):
        globalVar.sfmlArea.render.draw(self.sprite)

    def setPosition(self, position):
        self.sprite.position = position

    position = property(lambda self : self.sprite.position, setPosition)
