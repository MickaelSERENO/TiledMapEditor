from gi.repository import Gtk, Gdk, GdkPixbuf
import globalVar
import sfml as sf
import functions

class CreateMenu:
    def __init__(self, parent):
        self.parent = parent

    def newFile(self, fileManager):
        window = Gtk.Window(title="New File")
        window.set_property("modal",True)
        accelGroup = Gtk.AccelGroup()
        window.add_accel_group(accelGroup)

        vgrid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)

        grid = Gtk.Grid()
        nameLabel = Gtk.Label("Name")
        formatLabel = Gtk.Label("Tile Format")
        numberCases = Gtk.Label("Number Cases")

        grid.attach(nameLabel, 0, 0, 1, 1)
        grid.attach_next_to(formatLabel, nameLabel, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(numberCases, formatLabel, Gtk.PositionType.BOTTOM, 1, 1)

        nameEntered = Gtk.Entry()
        nameEntered.set_text("Tile")

        xLabel = Gtk.Label("x")
        spinTileLeft = Gtk.SpinButton()
        adjustment1 = Gtk.Adjustment(32, 0, 100, 1, 10, 0)
        spinTileLeft.set_adjustment(adjustment1)
        adjustment2 = Gtk.Adjustment(32, 0, 100, 1, 10, 0)
        spinTileRight = Gtk.SpinButton()
        spinTileRight.set_adjustment(adjustment2)

        xBisLabel = Gtk.Label("x")
        spinCasesLeft = Gtk.SpinButton()
        adjustment3 = Gtk.Adjustment(32, 0, 10000, 1, 10, 0)
        spinCasesLeft.set_adjustment(adjustment3)
        adjustment4 = Gtk.Adjustment(32, 0, 10000, 1, 10, 0)
        spinCasesRight = Gtk.SpinButton()
        spinCasesRight.set_adjustment(adjustment4)

        grid.attach_next_to(nameEntered, nameLabel, Gtk.PositionType.RIGHT, 3, 1)

        grid.attach_next_to(spinTileLeft, formatLabel, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(xLabel, spinTileLeft, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(spinTileRight, xLabel, Gtk.PositionType.RIGHT, 1, 1)

        grid.attach_next_to(spinCasesLeft, numberCases, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(xBisLabel, spinCasesLeft, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(spinCasesRight, xBisLabel, Gtk.PositionType.RIGHT, 1, 1)

        vgrid.add(grid)
        hbox = Gtk.Box()

        buttonOK = Gtk.Button(label="OK")
        buttonOK.add_accelerator("activate", accelGroup, Gdk.KEY_Return, 0, \
                Gtk.AccelFlags.VISIBLE)
        buttonOK.add_accelerator("activate", accelGroup, Gdk.KEY_KP_Enter, 0, \
                Gtk.AccelFlags.VISIBLE)
        buttonOK.connect("clicked", self.initNewFile, \
                {'hTileSize':spinTileLeft, 'vTileSize':spinTileRight, \
                'hNumberCases':spinCasesLeft, 'vNumberCases':spinCasesRight, \
                'nameEntered':nameEntered, 'window':window})

        buttonCancel = Gtk.Button(label="Cancel")
        buttonCancel.add_accelerator("activate", accelGroup, Gdk.KEY_Escape, 0, \
                Gtk.AccelFlags.MASK)
        buttonCancel.connect("clicked", self.quitWindow, window)

        hbox.pack_start(buttonCancel, False, False, 0)
        hbox.pack_start(buttonOK, False, False, 0)
        vgrid.add(hbox)
        hbox.set_halign(Gtk.Align.END)
        hbox.set_valign(Gtk.Align.END)

        window.connect("destroy", self.quitWindow, window, "cancel")
        window.add(vgrid)
        window.show_all()

    def createNewImage(self, fileManager, tileBox):
        if globalVar.sfmlArea:
            window = Gtk.Window(title="New image")
            window.set_property("modal",True)

            notebook = Gtk.Notebook()
            notebook.append_page(self.createNewTileSet(window, fileManager, tileBox),\
                    Gtk.Label("Static"))
            notebook.append_page(self.createNewAnnimation(window, fileManager, tileBox),\
	                Gtk.Label("Annimation"))

            window.connect("destroy", self.quitWindow, window, "cancel")
            window.add(notebook)
            window.show_all()

    def createNewTileSet(self, window, fileManager, tileBox):
        accelGroup = Gtk.AccelGroup()
        window.add_accel_group(accelGroup)

        grid = Gtk.Grid()
        vgrid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        vgrid.add(grid)

        path = Gtk.Label("Path")
        size =  Gtk.Label("Tile size")
        spacing = Gtk.Label("Space between tiles")
        grid.attach(path, 0, 0, 1, 1)
        grid.attach_next_to(size, path, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(spacing, size, Gtk.PositionType.BOTTOM, 1, 1)

        imageEntered = Gtk.Entry()
        imageEntered.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, Gtk.STOCK_FILE)
        imageEntered.set_icon_activatable(Gtk.EntryIconPosition.SECONDARY, True)
        imageEntered.connect("icon-press", self.openImage, fileManager)
        grid.attach_next_to(imageEntered, path, Gtk.PositionType.RIGHT, 3, 1)

        xLabel = Gtk.Label("x")
        spinTileLeft = Gtk.SpinButton()
        adjustment1 = Gtk.Adjustment(32, 0, 100, 1, 10, 0)
        spinTileLeft.set_adjustment(adjustment1)
        adjustment2 = Gtk.Adjustment(32, 0, 100, 1, 10, 0)
        spinTileRight = Gtk.SpinButton()
        spinTileRight.set_adjustment(adjustment2)

        xBisLabel = Gtk.Label("x")
        spinSpaceLeft = Gtk.SpinButton()
        adjustment3 = Gtk.Adjustment(32, 0, 100, 1, 10, 0)
        spinSpaceLeft.set_adjustment(adjustment3)
        adjustment4 = Gtk.Adjustment(32, 0, 100, 1, 10, 0)
        spinSpaceRight = Gtk.SpinButton()
        spinSpaceRight.set_adjustment(adjustment4)

        grid.attach_next_to(spinTileLeft, size, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(xLabel, spinTileLeft, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(spinTileRight, xLabel, Gtk.PositionType.RIGHT, 1, 1)

        grid.attach_next_to(spinSpaceLeft, spacing, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(xBisLabel, spinSpaceLeft, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(spinSpaceRight, xBisLabel, Gtk.PositionType.RIGHT, 1, 1)
        hbox = Gtk.Box()
        buttonOK = Gtk.Button(label="OK")
        buttonOK.add_accelerator("activate", accelGroup, Gdk.KEY_Return, 0, \
                Gtk.AccelFlags.VISIBLE)
        buttonOK.add_accelerator("activate", accelGroup, Gdk.KEY_KP_Enter, 0, \
                Gtk.AccelFlags.VISIBLE)
        buttonOK.connect("clicked", self.newTileSet, \
        {'hTileSize':spinTileLeft, 'vTileSize':spinTileRight, \
        'hTileSpace':spinSpaceLeft, 'vTileSpace':spinSpaceRight, \
        'imageEntered':imageEntered, 'fileManager':fileManager, \
                'tileBox':tileBox, 'window':window})
        buttonCancel = Gtk.Button(label="Cancel")
        buttonCancel.connect("clicked", self.quitWindow, window)
        buttonCancel.add_accelerator("activate", accelGroup, Gdk.KEY_Escape, 0, \
                Gtk.AccelFlags.MASK)

        hbox.pack_start(buttonCancel, False, False, 0)
        hbox.pack_start(buttonOK, False, False, 0)
        vgrid.add(hbox)
        hbox.set_halign(Gtk.Align.END)
        hbox.set_valign(Gtk.Align.END)

        return vgrid

    def newTrace(self, widget, traceManager):
        if globalVar.sfmlArea:
            window = Gtk.Window()
            window.set_property("modal", True)
            notebook = Gtk.Notebook()
            notebook.append_page(self.createNewStaticTrace(window, traceManager),\
                    Gtk.Label("Static"))
            notebook.append_page(self.createNewDynamicTrace(window, traceManager),\
                    Gtk.Label("Dynamic"))

            window.connect("destroy", self.quitWindow, window, "cancel")
            window.add(notebook)
            window.show_all()

    def createNewDynamicTrace(self, window, traceManager):
        grid = Gtk.Grid()
        nameLabel = Gtk.Label("Name")
        nameEntered = Gtk.Entry(text="Trace #"+str(traceManager.getNumberOfTraces()))
        return grid

    def createNewStaticTrace(self, window, traceManager):
        accelGroup = Gtk.AccelGroup()
        window.add_accel_group(accelGroup)

        grid = Gtk.Grid()
        vgrid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        vgrid.add(grid)
        nameLabel = Gtk.Label("Name")
        nameEntered = Gtk.Entry(text="Trace #"+str(traceManager.getNumberOfTraces()))

        xComboBox = Gtk.ComboBoxText()
        for i in range(1, globalVar.sfmlArea.numberCases.x+1):
            xComboBox.append_text(str(i*globalVar.sfmlArea.sizeCase.x))

        yComboBox = Gtk.ComboBoxText()
        for i in range(1, globalVar.sfmlArea.numberCases.y+1):
            yComboBox.append_text(str(i*globalVar.sfmlArea.sizeCase.y))

        sizeLabel = Gtk.Label("Size")
        xLabel = Gtk.Label("x")

        grid.attach(nameLabel, 0, 0, 1, 1)
        grid.attach_next_to(nameEntered, nameLabel, Gtk.PositionType.RIGHT, 3, 1)
        grid.attach_next_to(sizeLabel, nameLabel, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(xComboBox, sizeLabel, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(xLabel, xComboBox, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(yComboBox, xLabel, Gtk.PositionType.RIGHT, 1, 1)

        hbox = Gtk.Box()
        buttonOK = Gtk.Button(label="OK")
        buttonOK.add_accelerator("activate", accelGroup, Gdk.KEY_Return, 0, \
                Gtk.AccelFlags.VISIBLE)
        buttonOK.add_accelerator("activate", accelGroup, Gdk.KEY_KP_Enter, 0, \
                Gtk.AccelFlags.VISIBLE)
        buttonOK.connect("clicked", self.newStaticTrace, \
                {'xComboBox':xComboBox, 'yComboBox':yComboBox,\
                'nameEntered':nameEntered, 'traceManager':traceManager, 'window':window})
        buttonCancel = Gtk.Button(label="Cancel")
        buttonCancel.connect("clicked", self.quitWindow, window)
        buttonCancel.add_accelerator("activate", accelGroup, Gdk.KEY_Escape, 0, \
                Gtk.AccelFlags.MASK)

        hbox.pack_start(buttonCancel, False, False, 0)
        hbox.pack_start(buttonOK, False, False, 0)
        vgrid.add(hbox)

        hbox.set_halign(Gtk.Align.END)
        hbox.set_valign(Gtk.Align.END)

        return vgrid

    def newTileSet(self, button, widgets):
        spacing = sf.Vector2(0, 0)
        if 'hTileSize' and 'vTileSpace' in widgets:
            spacing = sf.Vector2(widgets['hTileSpace'].get_value(), widgets['vTileSpace'].get_value())

        widgets['tileBox'].cutTileSet(widgets['imageEntered'].get_text(), \
            sf.Vector2(widgets['hTileSize'].get_value(), widgets['vTileSize'].get_value()), \
            spacing)	
        if 'window' in widgets:
            widgets['window'].destroy()

    def createNewAnnimation(self, window, fileManager, tileBox):
        accelGroup = Gtk.AccelGroup()
        window.add_accel_group(accelGroup)
        grid = Gtk.Grid()
        vgrid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        vgrid.add(grid)

        widgets = dict()
        widgets['table'] = self.newTable()
        widgets['treeStore'] = widgets['table'].get_model()

        fileLabel = Gtk.Label("File")

        imageEntered = Gtk.Entry()
        imageEntered.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, Gtk.STOCK_FILE)
        imageEntered.set_icon_activatable(Gtk.EntryIconPosition.SECONDARY, True)
        imageEntered.connect("icon-press", self.openImage, fileManager)
        grid.attach(fileLabel, 0, 0, 1, 1)
        grid.attach_next_to(imageEntered, fileLabel, Gtk.PositionType.RIGHT, 3, 1)
        widgets['imageEntered'] = imageEntered

        hbox = Gtk.Box()
        setTableSize = Gtk.Button(label="Set Table")
        setTableSize.connect("clicked", self.setTable, widgets)
        hbox.pack_start(setTableSize, False, False, 0)

        box = Gtk.Box()
        buttonOK = Gtk.Button(label="OK")
        buttonOK.connect("clicked", self.cutAnnimation)
        buttonOK.add_accelerator("activate", accelGroup, Gdk.KEY_Return, 0, \
                Gtk.AccelFlags.VISIBLE)
        buttonOK.add_accelerator("activate", accelGroup, Gdk.KEY_KP_Enter, 0, \
                Gtk.AccelFlags.VISIBLE)

        buttonCancel = Gtk.Button(label="Cancel")
        buttonCancel.connect("clicked", self.quitWindow, window)
        buttonCancel.add_accelerator("activate", accelGroup, Gdk.KEY_Escape, 0, \
                Gtk.AccelFlags.MASK)
        box.pack_start(buttonCancel, False, False, 0)
        box.pack_start(buttonOK, False, False, 0)
        box.set_halign(Gtk.Align.END)
        hbox.pack_start(box, True, True, 0)

        vgrid.add(hbox)
        return vgrid

    def newTable(self):
        treeScore = Gtk.TreeStore(str, str, str, str, str)
        treeView = Gtk.TreeView(model=treeScore)

        titleRenderer = Gtk.CellRendererText()
        posXRenderer= Gtk.CellRendererText() 
        posYRenderer= Gtk.CellRendererText() 
        sizeXRenderer= Gtk.CellRendererText() 
        sizeYRenderer= Gtk.CellRendererText() 

        columnTitle = Gtk.TreeViewColumn("Name", titleRenderer, text=0)
        columnPosX = Gtk.TreeViewColumn("Position x", posXRenderer, text=1)
        columnPosY = Gtk.TreeViewColumn("Position y", posYRenderer, text=2)
        columnSizeX = Gtk.TreeViewColumn("Size x", sizeXRenderer, text=3)
        columnSizeY = Gtk.TreeViewColumn("Size y", sizeYRenderer, text=4)

        treeView.append_column(columnTitle)
        treeView.append_column(columnPosX)
        treeView.append_column(columnPosY)
        treeView.append_column(columnSizeX)
        treeView.append_column(columnSizeY)

        return treeView

    def setTable(self, button, widgets):
        if not widgets['imageEntered'].get_text():
            return
        window = Gtk.Window(title="New image")
        widgets['table'].set_model(widgets['treeStore'])
        treeCopy = functions.copyTreeStore(widgets['table'].get_model())
        widgets['treeCopied'] = treeCopy
        widgets['window'] = window

        hBox = Gtk.Box(spacing=6,orientation=Gtk.Orientation.HORIZONTAL)
        hBox.pack_start(widgets['table'], True, True, 0)
        hBox.pack_start(self.insertNewAnnimation(widgets), False, False, 0)

        vBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vBox.pack_start(hBox, True, True, 0)
        vBox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)
        vBox.pack_start(self.actionAnnimation(widgets), False, False, 0)

        window.set_property("modal",True)
        window.add(vBox)
        window.show_all()

    def insertNewAnnimation(self, widgets):
        if not widgets['imageEntered'].get_text():
            return
        grid = Gtk.Grid()
        vGrid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        vGrid.add(grid)
        vGrid.add(hbox)

        imagePixbuf = GdkPixbuf.Pixbuf.new_from_file(widgets['imageEntered'].get_text())
        nameLabel = Gtk.Label("Name")

        titleLabel = Gtk.Label()
        xLabel = Gtk.Label("Position X")
        yLabel = Gtk.Label("Position Y")
        sizeXLabel = Gtk.Label("Size X")
        sizeYLabel = Gtk.Label("Size Y")

        nameEntry = Gtk.Entry()
        positionXAdjustment = Gtk.Adjustment(0, 0, imagePixbuf.get_width(), 1, 10, 0) 
        positionYAdjustment = Gtk.Adjustment(0, 0, imagePixbuf.get_height(), 1, 10, 0) 
        sizeXAdjustment = Gtk.Adjustment(0, 0, imagePixbuf.get_width(), 1, 10, 0) 
        sizeYAdjustment = Gtk.Adjustment(0, 0, imagePixbuf.get_height(), 1, 10, 0) 
        xSpin = Gtk.SpinButton(adjustment=positionXAdjustment)
        ySpin = Gtk.SpinButton(adjustment=positionYAdjustment)
        sizexSpin = Gtk.SpinButton(adjustment=sizeXAdjustment)
        sizeySpin = Gtk.SpinButton(adjustment=sizeYAdjustment)

        addAnnim = Gtk.Button(label="Add")
        addEntity = Gtk.Button(label="Add")
        resetEntity = Gtk.Button(label="Reset")

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

        grid.attach(nameLabel, 0,0,1,1)
        grid.attach_next_to(nameEntry, nameLabel, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(addAnnim, nameEntry, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(separator, nameLabel, Gtk.PositionType.BOTTOM, 3, 1)
        grid.attach_next_to(titleLabel, separator, Gtk.PositionType.BOTTOM, 4, 1)
        grid.attach_next_to(xLabel, titleLabel, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(xSpin, xLabel, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach_next_to(yLabel, xLabel, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(ySpin, yLabel, Gtk.PositionType.RIGHT, 2, 1)

        grid.attach_next_to(sizeXLabel, yLabel, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(sizexSpin, sizeXLabel, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach_next_to(sizeYLabel, sizeXLabel, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(sizeySpin, sizeYLabel, Gtk.PositionType.RIGHT, 2, 1)

        hbox.pack_start(addEntity, False, False, 0)
        hbox.pack_start(resetEntity, False, False, 0)
        hbox.set_halign(Gtk.Align.END)
        hbox.set_valign(Gtk.Align.END)


        widgets['nameAnnimEntered'] = nameEntry
        addAnnim.connect('clicked', self.addAnniInTree, widgets)

        return vGrid

    def addAnniInTree(self, button, widgets):
        parent=widgets['treeStore'].append(None)
        widgets['treeStore'].set_value(parent, 0, widgets['nameAnnimEntered'].get_text())
        
    def cutAnnimation(self, button):
        pass

    def actionAnnimation(self, widgets):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        actionBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        delBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        actionBox.set_halign(Gtk.Align.END)
        actionBox.set_valign(Gtk.Align.END)
        delBox.set_valign(Gtk.Align.END)
        delBox.set_halign(Gtk.Align.START)
        box.set_valign(Gtk.Align.END)

        box.pack_start(delBox, False, False, 0)
        box.pack_start(actionBox, False, False, 0)

        okButton = Gtk.Button(label="OK")
        cancelButton = Gtk.Button(label="Cancel")
        applyButton = Gtk.Button(label="Apply")

        clearAll = Gtk.Button(label="Clear")
        delete = Gtk.Button(label="Delete")

        delBox.pack_start(delete, False, False, 0)
        delBox.pack_start(clearAll, False, False, 0)

        actionBox.pack_start(applyButton, False, False, 0)
        actionBox.pack_start(okButton, False, False, 0)
        actionBox.pack_start(cancelButton, False, False, 0)

        cancelButton.connect('clicked', self.cancelAnnimation, widgets)

        return box

    def cancelAnnimation(self, button, widgets):
        widgets['treeStore'] = widgets['treeCopied']
        widgets['table'].set_model(widgets['treeStore'])
        self.quitWindow(button, widgets['window'])

    def newAnnimation(self, button, widgets):
        print(widgets['xComboBox'].get_active())
            #widgets['traceManager'].addTrace(sf.Vector2(widgets['xComboBox'].get_va

    def newStaticTrace(self, button, widgets):
        widgets['traceManager'].addTrace(sf.Vector2(int(widgets['xComboBox'].get_active_text()),\
            int(widgets['yComboBox'].get_active_text())), widgets['nameEntered'].get_text(), "Normal")
        if 'window' in widgets:
            widgets['window'].destroy()

    def newDynamicTrace(self, button, widgets):
        pass

    def quitWindow(self, *args, **kwargs):
        args[1].destroy()

    def openImage(self, entry, pos, event, fileManager):
        path = fileManager.openFile("image")
        if path:
            entry.set_text(path)

    def initNewFile(self, button, widgets):
        addString = ''
        if widgets['nameEntered'].get_text()[-4:] != ".xml":
            addString = ".xml"
        open("Files/" + widgets['nameEntered'].get_text() + addString, "w").close()

        globalVar.tileWindow.buildSFMLArea(sf.Vector2(\
                int(widgets["hNumberCases"].get_value()), int(widgets["vNumberCases"].get_value())),\
                sf.Vector2(\
				int(widgets["hTileSize"].get_value()), int(widgets["vTileSize"].get_value())))

        globalVar.sfmlArea.get_toplevel().set_title(\
                widgets['nameEntered'].get_text().replace(".xml", ""))
        window = widgets['window']
        del widgets['window']
        window.destroy()
