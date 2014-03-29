from gi.repository import Gtk, Gdk,GdkPixbuf
from SFMLArea import *
from TraceTile import *
from TileBox import *
import sfml as sf
import platform
if platform.system() == "Linux":
    from gi.repository import GdkX11
elif platform.system() == "Windows":
    from gi.repository import GdkWin32

class ObjectManager(Gtk.Box):
    objectTexture = dict()
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.objectDict = dict()
        self.expanderDict = dict()
        self.typeList = list()
        self.numColumn = 2
        self.expanderBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.pack_start(self.expanderBox, True, True, 0)
        self.buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.pack_start(self.buttonBox, True, True, 0)

    def promptAddObject(self, button):
        window = Gtk.Window(title="Add Object")
        accelGroup = Gtk.AccelGroup()
        window.add_accel_group(accelGroup)

        vgrid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        grid = Gtk.Grid()

        nameLabel = Gtk.Label("Name")
        tileLabel = Gtk.Label("Tile Size")
        caseLabel = Gtk.Label("Case Size")
        typeLabel = Gtk.Label("Type")
        nameEntered = Gtk.Entry()
        nameEntered.set_text("Object's name")

        typeComboBox = Gtk.ComboBoxText.new_with_entry()
        for t in self.typeList:
            typeModel.append(str(t))

        tileAdjustmentX = Gtk.Adjustment(32, 0, 100, 1, 10, 0)
        tileAdjustmentY = Gtk.Adjustment(32, 0, 100, 1, 10, 0)
        tileSizeX = Gtk.SpinButton()
        tileSizeX.set_adjustment(tileAdjustmentX)
        tileSizeY = Gtk.SpinButton()
        tileSizeY.set_adjustment(tileAdjustmentY)
        xTileLabel = Gtk.Label("x")

        caseAdjustmentX = Gtk.Adjustment(5, 0, 1000, 1, 10, 0)
        caseAdjustmentY = Gtk.Adjustment(5, 0, 1000, 1, 10, 0)
        caseSizeX = Gtk.SpinButton()
        caseSizeX.set_adjustment(caseAdjustmentX)
        caseSizeY = Gtk.SpinButton()
        caseSizeY.set_adjustment(caseAdjustmentY)
        xCaseLabel = Gtk.Label("x")

        grid.attach(nameLabel, 0, 0, 1, 1)
        grid.attach_next_to(typeLabel, nameLabel, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(tileLabel, typeLabel, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(caseLabel, tileLabel, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(nameEntered, nameLabel, Gtk.PositionType.RIGHT, 3, 1)
        grid.attach_next_to(typeComboBox, typeLabel, Gtk.PositionType.RIGHT, 3, 1)
        grid.attach_next_to(tileSizeX, tileLabel, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(xTileLabel, tileSizeX, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(tileSizeY, xTileLabel, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(caseSizeX, caseLabel, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(xCaseLabel, caseSizeX, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(caseSizeY, xCaseLabel, Gtk.PositionType.RIGHT, 1, 1)

        hbox = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        hbox.set_halign(Gtk.Align.END)
        hbox.set_valign(Gtk.Align.END)

        okButton = Gtk.Button(label="OK")
        okButton.connect("clicked", self.makeObject, \
                {'window':window, 'nameEntered':nameEntered,\
                'typeComboBox':typeComboBox,\
                'tileSizeX':tileSizeX,'tileSizeY':tileSizeY,\
                'caseSizeX':caseSizeX, 'caseSizeY':caseSizeY})
        okButton.add_accelerator("activate", accelGroup, Gdk.KEY_Return, 0, \
                Gtk.AccelFlags.VISIBLE)
        okButton.add_accelerator("activate", accelGroup, Gdk.KEY_KP_Enter, 0, \
                Gtk.AccelFlags.VISIBLE)

        cancelButton = Gtk.Button(label="Cancel")
        cancelButton.add_accelerator("activate", accelGroup, Gdk.KEY_Escape, 0, \
                Gtk.AccelFlags.MASK)
        cancelButton.connect("clicked", self.quitWindow, window)

        hbox.pack_start(cancelButton, False, False, 0)
        hbox.pack_start(okButton, False, False, 0)

        vgrid.add(grid)
        vgrid.add(hbox)

        window.add(vgrid)
        window.show_all()
        window.connect("delete_event", self.destroyQuitWindow)

    def makeObject(self, button, widgets):
        widgets['window'].hide()

        window = Gtk.Window(title=widgets['nameEntered'].get_text())
        accelGroup = Gtk.AccelGroup()
        window.add_accel_group(accelGroup)

        typeTreeIter = widgets['typeComboBox'].get_active_iter()
        if typeTreeIter:
            t = widgets['typeModel'][typeTreeIter][0]
            if not t in self.typeList:
                self.typeList.append(t)

        tileSize = sf.Vector2(int(widgets['tileSizeX'].get_value()),\
                int(widgets['tileSizeY'].get_value()))
        caseSize = sf.Vector2(int(widgets['caseSizeX'].get_value()),\
                int(widgets['caseSizeY'].get_value()))
        sfmlMakeObject = SFMLMakeObject(tileSize, caseSize, widgets['nameEntered'].get_text())

        vbox=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_halign(Gtk.Align.END)
        hbox.set_valign(Gtk.Align.END)

        okButton = Gtk.Button(label="OK")
        okButton.connect("clicked", self.addObject, \
                {'windowMakeObject':window, 'widgetsProperties':widgets,\
                'sfmlMakeObject':sfmlMakeObject})
        okButton.add_accelerator("activate", accelGroup, Gdk.KEY_Return, 0, \
                Gtk.AccelFlags.VISIBLE)
        okButton.add_accelerator("activate", accelGroup, Gdk.KEY_KP_Enter, 0, \
                Gtk.AccelFlags.VISIBLE)

        cancelButton = Gtk.Button(label="Cancel")
        cancelButton.add_accelerator("activate", accelGroup, Gdk.KEY_Escape, 0, \
                Gtk.AccelFlags.MASK)
        cancelButton.connect("clicked", self.cancelMakeObject, window, widgets)
        window.connect("delete_event", self.destroyCancelMakeObject, widgets)

        hbox.pack_start(cancelButton, False, False, 0)
        hbox.pack_start(okButton, False, False, 0)

        vbox.pack_start(sfmlMakeObject, True, True, 0)
        vbox.pack_start(hbox, False, False, 0)

        window.add(vbox)
        window.show_all()

        if platform.system() == "Linux":
            sfmlMakeObject.render.create(sfmlMakeObject.get_window().get_xid())
        elif platform.system() == "Windows":
            sfmlMakeObject.render.create(GdkWin32.Win32Window.get_handle(sfmlMakeObject.get_window()))

    def cancelMakeObject(self, button, windowMakeObject, widgets):
        windowMakeObject.destroy()
        widgets['window'].show()

    def destroyCancelMakeObject(self, window, event, widgets):
        window.destroy()
        widgets['window'].show()

    def addObject(self, button, widgets):
        render = sf.RenderTexture(widgets['sfmlMakeObject'].size.x, widgets['sfmlMakeObject'].size.y)
        render.clear(sf.Color(0, 0, 0, 0))
        title = widgets['widgetsProperties']['nameEntered'].get_text()
        typeName = widgets['widgetsProperties']['typeComboBox'].get_active_text()

        for i in range(widgets['sfmlMakeObject'].numberCase.x):
            for j in range(widgets['sfmlMakeObject'].numberCase.y):
                if widgets['sfmlMakeObject'].listTile[i][j]:
                    render.draw(widgets['sfmlMakeObject'].listTile[i][j].sprite)

        render.display()
        self.objectDict[title] = \
                MakedObjectTile(render.texture, widgets['sfmlMakeObject'].listTile, widgets['sfmlMakeObject'])

        if not typeName in self.expanderDict.keys():
            self.expanderDict[typeName] = Gtk.Expander()
            self.expanderDict[typeName].set_label(typeName)
            treeStore = Gtk.TreeStore(GdkPixbuf.Pixbuf)
            viewIcon = ObjectDragIconView(treeStore, self.numColumn, title, typeName)
            viewIcon.set_pixbuf_column(0)
            viewIcon.set_name(title)
            viewIcon.set_columns(self.numColumn)
            self.expanderDict[typeName].add(viewIcon)

        model = self.expanderDict[typeName].get_child().get_model()
        image = render.texture.to_image()
        pix = ObjectTileIcon.new(image.pixels.data, image.width, image.height, title)
        model.append(None, [pix])
        self.expanderBox.pack_start(self.expanderDict[typeName], False, False, 0)

        self.get_toplevel().show_all()

        widgets['windowMakeObject'].destroy()
        widgets['widgetsProperties']['window'].destroy()

        ObjectManager.objectTexture[title] = render.texture.copy()

    def quitWindow(self, button, window):
        window.destroy()

    def destroyQuitWindow(self, window, event):
        window.destroy()

class ObjectTileIcon(GdkPixbuf.Pixbuf):
    def new(data, width, height, name):
        objet = GdkPixbuf.Pixbuf.new_from_data(data, GdkPixbuf.Colorspace.RGB, True, 8, width, height, 4*width, None, None)
        objet.name = name 
        return objet

class ObjectDragIconView(DragIconView):
    def __init__(self, model, numColumn, name, typeName):
        DragIconView.__init__(self, model, numColumn, name)
        self.style = "Object"
        self.name = name
        self.typeName = typeName

    def do_drag_data_get(self, widget, context, selection_data, info, time=None):
        if time:
            selected_path = self.get_selected_items()[0]
            selected_iter = self.get_model().get_iter(selected_path)
            selection_data.set_pixbuf(self.get_model().get_value(selected_iter, 0))

            TileBox.dndDatas = {'from':'ObjectManager',\
                    'name':self.name,\
                    'numColumn':self.numColumn, 'style':self.style,\
                    'objectTexture':ObjectManager.objectTexture[self.name]}
