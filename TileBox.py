from gi.repository import Gtk, GdkPixbuf, Gdk, GObject
from os import path
from copy import copy
import shutil
import sfml as sf
import xml.etree.ElementTree as ET
from collections import OrderedDict

class TileBox(Gtk.ScrolledWindow):
    textureList = OrderedDict()
    dndDatas = None
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.numColumn = 5

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        staticExpander = Gtk.Expander()
        staticExpander.set_label("Static")
        self.staticBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        staticExpander.add(self.staticBox)

        self.box.pack_start(staticExpander, True, True, 0)

        animationExpander = Gtk.Expander()
        animationExpander.set_label("Animation")
        animationBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        animationExpander.add(animationBox)

        staticAnimationExpander = Gtk.Expander()
        staticAnimationExpander.set_label("Static Animation")

        dynamicAnimationExpander = Gtk.Expander()
        dynamicAnimationExpander.set_label("Dynamic Animation")

        self.staticAnimationBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.dynamicAnimationBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        staticAnimationExpander.add(self.staticAnimationBox)
        dynamicAnimationExpander.add(self.dynamicAnimationBox)

        animationBox.pack_start(staticAnimationExpander, True, True, 0)
        animationBox.pack_start(dynamicAnimationExpander, True, True, 0)

        self.dynamicAnimationDict = OrderedDict()
        self.staticAnimation = OrderedDict()
        self.staticList = []

        self.box.pack_start(animationExpander, True, True, 0)

        self.add(self.box)
        self.set_size_request(100, 300)

        self.popupMenu = None
        self.propAction = None

    def makePopupMenu(self, uiManager):
        self.popupMenu =  uiManager.get_widget("/TilePopup")

    def clearAll(self):
        for child in self.staticBox.get_children():
            self.staticBox.remove(child)
        for child in self.dynamicAnimationBox.get_children():
            self.dynamicAnimationBox.remove(child)
        self.staticList = []
        self.dynamicAnimationDict = OrderedDict()
        TileBox.textureList = OrderedDict()

    def makeActionMenu(self, actionGroup):
        self.propAction = Gtk.Action("TileProperties", "Properties", None, None)
        self.propAction.connect("activate", self.makeWindowProperty)
        actionGroup.add_action(self.propAction)

    def cutTileSet(self, tileSetFile, size=sf.Vector2(32, 32), spacing=sf.Vector2(0, 0)):
        if tileSetFile and path.isfile(tileSetFile):
            tileSetFile = path.relpath(path.abspath(tileSetFile), path.abspath(path.dirname(__file__)))
            if path.dirname(tileSetFile) != "Files":
                shutil.copy(tileSetFile, "Files")
            fileName = "Files/"+path.basename(tileSetFile)

            if fileName in TileBox.textureList:
                return
            else:
                TileBox.textureList[fileName] = sf.Texture.from_file(fileName)

            expander = Gtk.Expander()
            expander.set_label(fileName.split('/')[1])

            treeStore = Gtk.TreeStore(GdkPixbuf.Pixbuf, int, int)

            image = Gtk.Image()
            image.set_from_file(tileSetFile)
            originPixbuf = image.get_pixbuf()
            posX = 0
            posY = 0

            tileID = 0

            while posY < originPixbuf.get_height():
                pixbuf = TileIcon.new(GdkPixbuf.Colorspace.RGB, True, 8, size.x, size.y, \
                        sf.Rect(sf.Vector2(posX, posY), size), tileID)

                originPixbuf.copy_area(posX, posY, min(size.x, originPixbuf.get_width() - posX), \
                        min(size.y, originPixbuf.get_height() - posY), pixbuf, 0, 0)
                listPixbuf = [pixbuf, posX, posY]
                posX += size.x + spacing.x
                if posX >= originPixbuf.get_width():
                    posX = 0
                    posY += size.y + spacing.y
                treeStore.append(None, listPixbuf)
                tileID = tileID + 1
            viewIcon = StaticDragIconView(treeStore, size, spacing, self.numColumn, fileName)
            viewIcon.set_columns(self.numColumn)
            viewIcon.set_pixbuf_column(0)
            viewIcon.set_name(fileName)
            viewIcon.connect("button_press_event", self.pressButtonEvent)

            expander.add(viewIcon)
            self.staticBox.pack_start(expander, True, True, 0)
            self.staticList.append(viewIcon)
            self.show_all()

    def cutAnimationTreeStore(self, dynamicTreeStore, staticTreeStore, fileName):
        fileName = "Files/"+path.basename(fileName)
        if fileName in Texture.textureList:
            return

        fileName = path.relpath(path.abspath(fileName), path.abspath(path.dirname(__file__)))
        if path.dirname(fileName) != "Files":
            shutil.copy(fileName, "Files")
        fileName = "Files/"+path.basename(fileName)

        TileBox.textureList[fileName] = sf.Texture.from_file(fileName)

        if dynamicTreeStore:
            for i in range(len(dynamicTreeStore)):
                if dynamicTreeStore.iter_n_children(dynamicTreeStore.get_iter(i)) > 0:
                    self.cutDynamicAnimation(dynamicTreeStore,\
                            dynamicTreeStore.get_iter(i),\
                            fileName)

        if staticTreeStore:
            for i in range(len(dynamicTreeStore)):
                self.cutStaticAnimation(staticTreeStore.get_iter(i), fileName)

    #An animation has the following attributes : name, nX, posX, posY, spacX, spacY, sizeX, sizeY
    def cutStaticAnimation(self, animation, fileName):
        pass

    #An animation have many entity with 4 attributes : position in x and y and size in x and y
    def cutDynamicAnimation(self, treeStoreAnnim, animation, fileName):
        if fileName and path.isfile(fileName):
            if not fileName in self.dynamicAnimationDict:
                self.dynamicAnimationDict[fileName] = []

            expander = Gtk.Expander()
            expander.set_label(treeStoreAnnim.get_value(animation, 0))

            treeStore = Gtk.TreeStore(GdkPixbuf.Pixbuf, int, int)

            image = Gtk.Image()
            image.set_from_file(fileName)
            originPixbuf = image.get_pixbuf()

            for i in range(treeStoreAnnim.iter_n_children(animation)):
                posX = float(treeStoreAnnim.get_value(treeStoreAnnim.iter_nth_child(animation, i), 1))
                posY = float(treeStoreAnnim.get_value(treeStoreAnnim.iter_nth_child(animation, i), 2))
                sizeX = float(treeStoreAnnim.get_value(treeStoreAnnim.iter_nth_child(animation, i), 3))
                sizeY = float(treeStoreAnnim.get_value(treeStoreAnnim.iter_nth_child(animation, i), 4))

                pixbuf = TileIcon.new(GdkPixbuf.Colorspace.RGB, True, 8, sizeX, sizeY, \
                        sf.Rect(sf.Vector2(posX, posY), sf.Vector2(sizeX, sizeY)), \
                        int(treeStoreAnnim.get_value(treeStoreAnnim.iter_nth_child(animation, i), 0)))

                originPixbuf.copy_area(posX, posY, min(sizeX, originPixbuf.get_width() - posX), \
                        min(sizeY, originPixbuf.get_height() - posY), pixbuf, 0, 0)
                listPixbuf = [pixbuf, posX, posY]
                treeStore.append(None, listPixbuf)

            viewIcon = DynamicDragIconView(treeStore, self.numColumn, fileName,\
                    treeStoreAnnim.get_value(animation, 0))
            viewIcon.set_columns(self.numColumn)
            viewIcon.set_pixbuf_column(0)
            viewIcon.set_name(treeStoreAnnim.get_value(animation, 0))
            viewIcon.connect("button_press_event", self.pressButtonEvent)

            expander.add(viewIcon)
            self.dynamicAnimationDict[fileName].append(viewIcon)
            self.dynamicAnimationBox.pack_start(expander, True, True, 0)
            print("ok")
            self.show_all()

    def disconnectAll(self):
        self.propAction.disconnect_by_func(self.makeWindowProperty)

    def connectAll(self, widget, event):
        self.propAction.connect("activate", self.makeWindowProperty, widget, event)

    def pressButtonEvent(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 3:
                if(widget.get_selected_items()):
                    self.disconnectAll()
                    self.connectAll(widget, event)
                    self.popupMenu.popup(None, None, None, None, event.button, event.time)

    def makeWindowProperty(self, button, iconView, event):
        widgets = OrderedDict()
        iterTileSelected = iconView.get_model().get_iter(iconView.get_selected_items()[0])
        tile = iconView.get_model().get_value(iterTileSelected, 0)
        widgets['tile'] = tile

        window = Gtk.Window(title='Tile Properties')
        window.set_property('modal', True)

        grid = Gtk.Grid()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_halign(Gtk.Align.END)
        vgrid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        vgrid.add(grid)
        vgrid.add(hbox)

        typeLabel = Gtk.Label("type")
        nameLabel = Gtk.Label("name")
        typeEntry= Gtk.Entry()
        typeEntry.set_text(tile.type)
        nameEntry = Gtk.Entry()
        nameEntry.set_text(tile.name)

        grid.attach(typeLabel, 0, 0, 1, 1)
        grid.attach_next_to(typeEntry, typeLabel, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach_next_to(nameLabel, typeLabel, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(nameEntry, nameLabel, Gtk.PositionType.RIGHT, 2, 1)

        okButton = Gtk.Button(label="OK")
        cancelButton = Gtk.Button(label="Cancel")

        hbox.pack_start(okButton, False, False, 0)
        hbox.pack_start(cancelButton, False, False, 0)

        window.connect("destroy", lambda e, w : w.destroy(), window)
        okButton.connect('clicked', self.setTileProperty, widgets)
        cancelButton.connect('clicked', lambda b, w : w.destroy(), window)

        widgets['iconView'] = iconView
        widgets['nameEntry'] = nameEntry
        widgets['typeEntry'] = typeEntry
        widgets['window'] = window
        window.add(vgrid)
        window.show_all()

    def setTileProperty(self, button, widgets):
        widgets['tile'].name = widgets['nameEntry'].get_text()
        widgets['tile'].type = widgets['typeEntry'].get_text()
        if 'window' in widgets:
            widgets['window'].destroy()

    def getSaveFileElem(self):
        fileElem = ET.Element('Files')

        for view in self.staticList:
            dragIconSubElem = ET.SubElement(fileElem, 'Static')
            dragIconSubElem.set('file', view.fileName)
            dragIconSubElem.set('tileSize', str(view.size.x)+'x'+str(view.size.y))
            dragIconSubElem.set('spacing', str(view.spacing.x)+'x'+str(view.spacing.y))
            tileIter = view.get_model().get_iter_first()
            test = False
            while tileIter:
                tile = view.get_model().get_value(tileIter, 0)
                tileSubElem = ET.SubElement(dragIconSubElem, 'staticTile')
                tileSubElem.set('name', tile.name)
                tileSubElem.set('type', tile.type)
                tileIter = view.get_model().iter_next(tileIter)

        for viewList in self.dynamicAnimationDict.values():
            dragIconSubElem = ET.SubElement(fileElem, 'Dynamic')
            for view in viewList:
                dragIconSubElem.set('file', view.fileName)
                animationSubElem = ET.SubElement(dragIconSubElem, 'dynamicEntity')
                animationSubElem.set('name', view.name)
                tileIter = view.get_model().get_iter_first()
                while tileIter:
                    tile = view.get_model().get_value(tileIter, 0)
                    tileSubElem = ET.SubElement(animationSubElem, 'dynamicTile')
                    tileSubElem.set('name', tile.name)
                    tileSubElem.set('type', tile.type)
                    pos = str(tile.rect.left)+'x'+str(tile.rect.top)
                    size = str(tile.rect.width)+'x'+str(tile.rect.height)
                    tileSubElem.set('pos', pos)
                    tileSubElem.set('size', size)
                    tileIter = view.get_model().iter_next(tileIter)
        return fileElem

    #return the file ID. The number one is the first static file. 1 ID per file
    def getFileID(self, fileName, style="static"):
        if style == "static":
            for i in range(len(self.staticList)):
                if self.staticList[i].fileName == fileName:
                    return i
        else:
            l = list(self.dynamicAnimationDict.keys())
            if l.count(fileName):
                return len(self.staticList)+l.index(fileName)
        return -1

    def getFileName(self, fileID):
        if fileID < len(self.staticList):
            return self.staticList[fileID].fileName
        
        l=list(self.dynamicAnimationDict.keys())
        i = 0
        for fileName in l:
            if i == fileID - len(self.staticList):
                return l[i]
            i = i+1

    def decodeXML(self, element, path):
        listStaticElement = element.findall('Static')
        listDynamicElement = element.findall('Dynamic')

        for staticElement in listStaticElement:
            elemValues = OrderedDict()
            for staticItems in staticElement.items():
                elemValues[staticItems[0]] = staticItems[1]
            tileSizeSplit = elemValues['tileSize'].split('x')
            elemValues['tileSize'] = sf.Vector2(float(tileSizeSplit[0]), float(tileSizeSplit[1]))

            tileSpacingSplit = elemValues['spacing'].split('x')
            elemValues['spacing'] = sf.Vector2(float(tileSpacingSplit[0]), float(tileSpacingSplit[1]))

            self.cutTileSet(path+'/'+elemValues['file'], elemValues['tileSize'], elemValues['spacing'])

            iterStaticPass = False
            tileIter = self.staticList[-1].get_model().get_iter_first()
            for staticTileElement in staticElement.iter():
                #The first staticTileElement iter is a Static Element and not a staticTile Element
                if iterStaticPass==False:
                    iterStaticPass = True
                    continue

                tile = self.staticList[-1].get_model().get_value(tileIter, 0)

                tileValues = OrderedDict()
                for tileItems in staticTileElement.items(): 
                    tileValues[tileItems[0]] = tileItems[1]

                tile.name = tileValues['name']
                tile.type = tileValues['type']
                tileIter = self.staticList[-1].get_model().iter_next(tileIter)

        for dynamicElement in listDynamicElement:
            dynamicValuesElement = OrderedDict()
            tileValueDict = OrderedDict()
            iterAnimationPassFirst = False

            treeStoreAnnim = Gtk.TreeStore(str, str, str, str, str)

            #collect all items
            for dynamicItem in dynamicElement.items():
                dynamicValuesElement[dynamicItem[0]] = dynamicItem[1]

            for animationEntity in dynamicElement.iter():

                #The first entity is the parent entity and not a child
                if not iterAnimationPassFirst:
                    iterAnimationPassFirst=True
                    continue

                animationValuesEntity = OrderedDict()
                for animationItem in animationEntity.items():
                    animationValuesEntity[animationItem[0]] = animationItem[1]

                tileValueDict[animationValuesEntity['name']] = []

                parent = treeStoreAnnim.append(None)
                treeStoreAnnim.set_value(parent, 0, animationValuesEntity['name'])

                posTileEntity = 0
                iterTilePassFirst = False
                for tileEntity in animationEntity.iter():
                    if not iterTilePassFirst:
                        iterTilePassFirst=True
                        continue

                    tileValuesEntity = OrderedDict()
                    for tileItem in tileEntity.items():
                        tileValuesEntity[tileItem[0]] = tileItem[1]

                    sizeSplit = tileValuesEntity['size'].split('x')
                    tileValuesEntity['size'] = sf.Vector2(sizeSplit[0], sizeSplit[1])

                    tilePosSplit = tileValuesEntity['pos'].split('x')
                    tileValuesEntity['pos'] = sf.Vector2(tilePosSplit[0], tilePosSplit[1])

                    treeStoreAnnim.insert_with_values(parent, -1, [0, 1, 2, 3, 4], \
                            [str(posTileEntity), str(tileValuesEntity['pos'].x), str(tileValuesEntity['pos'].y), \
                            str(tileValuesEntity['size'].x), str(tileValuesEntity['size'].y)])

                    tileValueDict[animationValuesEntity['name']].append(tileValuesEntity)
                    posTileEntity+=1

            self.cutAnimationTreeStore(treeStoreAnnim, None, dynamicValuesElement['file'])

            currentDynamicList = self.dynamicAnimationDict[dynamicValuesElement['file']]
            for iconView in currentDynamicList:
                tileIter = iconView.get_model().get_iter_first()
                for tileDict in tileValueDict[iconView.get_name()]:
                    tile = iconView.get_model().get_value(tileIter, 0)

                    tile.name = tileDict['name']
                    tile.type = tileDict['type']
                    tileIter = iconView.get_model().iter_next(tileIter)

    def getDndDatas(self, tileID, fileID, animName=""):
        if fileID < len(self.staticList):
            return self.staticList[fileID].getDndDatasFromPath(tileID)
        else:
            i=0
            for dynamicIconView in self.dynamicAnimationDict.values():
                if i == fileID-len(self.staticList):
                    for entityID in range(len(dynamicIconView)):
                        if dynamicIconView[entityID].getAnimName() == animName:
                            return dynamicIconView[entityID].getDndDatasFromPath(tileID)
                i=i+1

class DragIconView(Gtk.IconView):
    def __init__(self, model, numColumn, fileName):
        Gtk.IconView.__init__(self, model)
        self.fileName = fileName
        self.numColumn = numColumn
        self.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)
        self.connect("drag-data-get", self.do_drag_data_get)
        self.connect("button-press-event", self.buttonPressEvent)

        targets = Gtk.TargetList.new([])
        targets.add_image_targets(0, True)
        self.drag_source_set_target_list(targets)

    def do_drag_data_get(self, widget, context, selection_data, info, time=None):
        return

    def buttonPressEvent(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 3:
                path = self.get_path_at_pos(event.x, event.y)
                if path:
                    widget.select_path(path)
                else:
                    widget.unselect_all()

    def getWidgetPosition(self, path):
        return self.get_columns() * self.get_item_row(path) +\
                self.get_item_column(path)

    def getXYWidgetPosition(self, path):
        vector = sf.Vector2()
        vector.x = self.get_model().get_value(self.get_model().get_iter(path), 1)
        vector.y = self.get_model().get_value(self.get_model().get_iter(path), 2)
        return vector

    def getIconSubRect(self, path):
        return self.get_model().get_value(self.get_model().get_iter(path), 0).rect

class StaticDragIconView(DragIconView):
    def __init__(self, model, size, spacing, numColumn, fileName):
        DragIconView.__init__(self, model, numColumn, fileName)
        self.set_property("activate-on-single-click", True)
        self.size = size
        self.spacing = spacing
        self.style = "Static"
        self.connect("item_activated", self.manageDndDatas)
        self.connect("selection-changed", self.manageDndDatas, None)

    def do_drag_data_get(self, widget, context, selection_data, info, time=None):
        if time:
            self.setDndDatas()
            selected_path = self.get_selected_items()[0]
            selected_iter = self.get_model().get_iter(selected_path)
            selection_data.set_pixbuf(self.get_model().get_value(selected_iter, 0))

    def setDndDatas(self):
        if not self.get_selected_items():
            TileBox.dndDatas = None
            return
        selected_path = self.get_selected_items()[0]
        selected_iter = self.get_model().get_iter(selected_path)

        TileBox.dndDatas = self.getDndDatasFromPath(selected_path)

    def manageDndDatas(self, widget, path):
        self.setDndDatas()

    def getDndDatasFromPath(self, path):
        selected_iter = self.get_model().get_iter(path)

        return {'from':'TileBox', 'spacing':self.spacing, 'size':self.size, \
                'fileName':self.fileName, 'name':self.get_name(),\
                'numColumn':self.numColumn, 'style':self.style,\
                'subRect':self.get_model().get_value(selected_iter, 0).rect,
                'tileID':self.get_model().get_value(selected_iter, 0).tileID}

class DynamicDragIconView(DragIconView):
    def __init__(self, model, numColumn, fileName, name):
        DragIconView.__init__(self, model, numColumn, fileName)
        self.style = "Dynamic"
        self.name = name

    def getAnimName(self):
        return self.get_name()

    def do_drag_data_get(self, widget, context, selection_data, info, time=None):
        if time:
            selected_path = self.get_selected_items()[0]
            selected_iter = self.get_model().get_iter(selected_path)
            selection_data.set_pixbuf(self.get_model().get_value(selected_iter, 0))

            TileBox.dndDatas = self.getDndDatasFromPath(selected_path)
            print(TileBox.dndDatas)

    def getDndDatasFromPath(self, path):
            selected_iter = self.get_model().get_iter(path)

            return {'tileID':self.get_model().get_value(selected_iter, 0).tileID,\
                    'animName':self.get_name(), 'fileName':self.fileName,\
                    'numColumn':self.numColumn,\
                    'style':self.style,\
                    'subRect':self.get_model().get_value(selected_iter, 0).rect}

class TileIcon(GdkPixbuf.Pixbuf):
    def new(color, tf, deep, sizex, sizey, rect, tileID):
        objet = GdkPixbuf.Pixbuf.new(color, tf, deep, sizex, sizey)
        objet.rect = rect
        objet.tileID = tileID #The tile number in the tile file
        objet.name = "" #The common name for the tile (ground, water, ...)
        objet.type = ""
        return objet
