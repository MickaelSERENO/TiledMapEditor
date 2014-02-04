from gi.repository import Gtk, GdkPixbuf, Gdk, GObject
from os import path
from copy import copy
import shutil
import sfml as sf

class TileBox(Gtk.ScrolledWindow):
    textureList = dict()
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

        annimationExpander = Gtk.Expander()
        annimationExpander.set_label("Annimation")
        self.annimationBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        annimationExpander.add(self.annimationBox)

        self.box.pack_start(annimationExpander, True, True, 0)

        self.add(self.box)
        self.set_size_request(100, 300)

        self.popupMenu = None
        self.propAction = None

    def makePopupMenu(self, uiManager):
        self.popupMenu =  uiManager.get_widget("/TilePopup")
        print(self.popupMenu)

    def clearTile(self):
        for child in self.staticBox.get_children():
            self.staticBox.remove(child)
        for child in self.annimationBox.get_children():
            self.annimationBox.remove(child)

    def makeActionMenu(self, actionGroup):
        self.propAction = Gtk.Action("TileProperties", "Properties", None, None)
        self.propAction.connect("activate", self.makeWindowProperty)
        actionGroup.add_action(self.propAction)

    def cutTileSet(self, tileSetFile, size=sf.Vector2(32, 32), spacing=sf.Vector2(0, 0)):
        if tileSetFile and path.isfile(tileSetFile):
            tileSetFile = path.relpath(path.abspath(tileSetFile), path.abspath(path.dirname(__file__)))
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
                        sf.Rectangle(sf.Vector2(posX, posY), size), tileID)

                originPixbuf.copy_area(posX, posY, min(size.x, originPixbuf.get_width() - posX), \
                        min(size.y, originPixbuf.get_height() - posY), pixbuf, 0, 0)
                listPixbuf = [pixbuf, posX, posY]
                posX += size.x + spacing.x
                if posX >= originPixbuf.get_width():
                    posX = 0
                    posY += size.y + spacing.y
                treeStore.append(None, listPixbuf)
                tileID = tileID + 1
            viewIcon = StaticDragIconView(treeStore, size, spacing, self.numColumn)
            viewIcon.set_columns(self.numColumn)
            viewIcon.set_pixbuf_column(0)
            viewIcon.set_name(fileName)
            viewIcon.connect("button_press_event", self.pressButtonEvent)

            expander.add(viewIcon)
            self.staticBox.pack_start(expander, True, True, 0)
            self.show_all()

    #An annimation have many entity with 4 attributes : position in x and y and size in x and y
    def cutTileAnnimation(self, treeStoreAnnim, annimation, fileName):
        if fileName and path.isfile(fileName):
            fileName = path.relpath(path.abspath(fileName), path.abspath(path.dirname(__file__)))
            shutil.copy(fileName, "Files")
            fileName = "Files/"+path.basename(fileName)

            if fileName in TileBox.textureList:
                return
            else:
                TileBox.textureList[treeStoreAnnim.get_value(annimation, 0)] = sf.Texture.from_file(fileName)

            expander = Gtk.Expander()
            expander.set_label(treeStoreAnnim.get_value(annimation, 0))

            treeStore = Gtk.TreeStore(GdkPixbuf.Pixbuf, int, int)

            image = Gtk.Image()
            image.set_from_file(fileName)
            originPixbuf = image.get_pixbuf()

            for i in range(treeStore.iter_n_children(annimation)):
                posX = int(treeStoreAnnim.get_value(treeStoreAnnim.iter_nth_child(annimation, i), 1))
                posY = int(treeStoreAnnim.get_value(treeStoreAnnim.iter_nth_child(annimation, i), 2))
                sizeX = int(treeStoreAnnim.get_value(treeStoreAnnim.iter_nth_child(annimation, i), 3))
                sizeY = int(treeStoreAnnim.get_value(treeStoreAnnim.iter_nth_child(annimation, i), 4))

                pixbuf = TileIcon.new(GdkPixbuf.Colorspace.RGB, True, 8, sizeX, sizeY, \
                        sf.Rectangle(sf.Vector2(posX, posY), sf.Vector2(sizeX, sizeY)), \
                        treeStoreAnnim.get_value(treeStoreAnnim.iter_nth_child(annimation, i), 0))

                originPixbuf.copy_area(posX, posY, min(sizeX, originPixbuf.get_width() - posX), \
                        min(sizeY, originPixbuf.get_height() - posY), pixbuf, 0, 0)
                listPixbuf = [pixbuf, posX, posY]
                treeStore.append(None, listPixbuf)

            viewIcon = DynamicDragIconView(treeStore, self.numColumn)
            viewIcon.set_columns(self.numColumn)
            viewIcon.set_pixbuf_column(0)
            viewIcon.set_name(treeStoreAnnim.get_value(annimation, 0))
            viewIcon.connect("button_press_event", self.pressButtonEvent)

            expander.add(viewIcon)
            self.annimationBox.pack_start(expander, True, True, 0)
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
        widgets = dict()
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
        window.add(vgrid)
        window.show_all()

    def setTileProperty(self, button, widgets):
        widgets['tile'].name = widgets['nameEntry'].get_text()
        widgets['tile'].type = widgets['typeEntry'].get_text()
        if 'window' in widgets:
            widgets['window'].destroy()
            
class DragIconView(Gtk.IconView):
    def __init__(self, model, numColumn):
        Gtk.IconView.__init__(self, model)
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
    def __init__(self, model, size, spacing, numColumn):
        DragIconView.__init__(self, model, numColumn)
        self.size = size
        self.spacing = spacing
        self.style = "Static"

    def do_drag_data_get(self, widget, context, selection_data, info, time=None):
        if time:
            selected_path = self.get_selected_items()[0]
            selected_iter = self.get_model().get_iter(selected_path)
            selection_data.set_pixbuf(self.get_model().get_value(selected_iter, 0))

            TileBox.dndDatas = {'spacing':self.spacing, 'size':self.size, \
                    'name':self.get_name(),\
                    'numColumn':self.numColumn, 'style':self.style,\
                    'subRect':self.get_model().get_value(selected_iter, 0).rect,
                    'tileID':self.get_model().get_value(selected_iter, 0).tileID}

class DynamicDragIconView(DragIconView):
    def __init__(self, model, numColumn):
        DragIconView.__init__(self, model, numColumn)
        self.style = "Dynamic"

    def do_drag_data_get(self, widget, context, selection_data, info, time=None):
        if time:
            print('info', info, '\n selection_data', selection_data)
            selected_path = self.get_selected_items()[0]
            selected_iter = self.get_model().get_iter(selected_path)
            selection_data.set_pixbuf(self.get_model().get_value(selected_iter, 0))

            TileBox.dndDatas = {'tileID':self.get_model().get_value(selected_iter, 0).tileID,\
                    'name':self.get_name(),\
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
