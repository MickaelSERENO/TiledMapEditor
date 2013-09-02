from gi.repository import Gtk, Gdk
import sfml as sf

class CreateMenu:
	def __init__(self, parent):
		self.parent = parent

	def newFile(self, fileManager, sfmlArea):
		window = Gtk.Window(title="New File")
		window.set_property("modal",True)
		accelGroup = Gtk.AccelGroup()
		window.add_accel_group(accelGroup)

		vgrid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)

		grid = Gtk.Grid()
		nameLabel = Gtk.Label("Name")
		formatLabel = Gtk.Label("Tile Format")
		numberCases = Gtk.Label("Number Cases")
		imageLabel = Gtk.Label("Image")

		grid.attach(nameLabel, 0, 0, 1, 1)
		grid.attach_next_to(formatLabel, nameLabel, Gtk.PositionType.BOTTOM, 1, 1)
		grid.attach_next_to(numberCases, formatLabel, Gtk.PositionType.BOTTOM, 1, 1)
		grid.attach_next_to(imageLabel, numberCases, Gtk.PositionType.BOTTOM, 1, 1)

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

		imageEntered = Gtk.Entry()
		imageEntered.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, Gtk.STOCK_FILE)
		imageEntered.set_icon_activatable(Gtk.EntryIconPosition.SECONDARY, True)
		imageEntered.connect("icon-press", self.openImage, fileManager)

		grid.attach_next_to(nameEntered, nameLabel, Gtk.PositionType.RIGHT, 3, 1)

		grid.attach_next_to(spinTileLeft, formatLabel, Gtk.PositionType.RIGHT, 1, 1)
		grid.attach_next_to(xLabel, spinTileLeft, Gtk.PositionType.RIGHT, 1, 1)
		grid.attach_next_to(spinTileRight, xLabel, Gtk.PositionType.RIGHT, 1, 1)

		grid.attach_next_to(spinCasesLeft, numberCases, Gtk.PositionType.RIGHT, 1, 1)
		grid.attach_next_to(xBisLabel, spinCasesLeft, Gtk.PositionType.RIGHT, 1, 1)
		grid.attach_next_to(spinCasesRight, xBisLabel, Gtk.PositionType.RIGHT, 1, 1)

		grid.attach_next_to(imageEntered, imageLabel, Gtk.PositionType.RIGHT, 3, 1)

		vgrid.add(grid)
		hbox = Gtk.Box()

		buttonOK = Gtk.Button(label="OK")
		buttonOK.add_accelerator("activate", accelGroup, Gdk.KEY_Return, 0, \
				Gtk.AccelFlags.VISIBLE)
		buttonOK.add_accelerator("activate", accelGroup, Gdk.KEY_KP_Enter, 0, \
				Gtk.AccelFlags.VISIBLE)
		buttonOK.connect("clicked", self.acceptNewFile, \
				{'hTileSize':spinTileLeft, 'vTileSize':spinTileRight, \
				'hNumberCases':spinCasesLeft, 'vNumberCases':spinCasesRight, \
				'nameEntered':nameEntered, 'imageEntered':imageEntered, \
				'sfmlArea':sfmlArea, 'window':window})

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
		for i in range(1, self.parent.sfmlArea.numberCases.x+1):
			xComboBox.append_text(str(i*self.parent.sfmlArea.sizeCase.x))

		yComboBox = Gtk.ComboBoxText()
		for i in range(1, self.parent.sfmlArea.numberCases.y+1):
			yComboBox.append_text(str(i*self.parent.sfmlArea.sizeCase.y))

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
		widgets['tileBox'].cutTileSet(widgets['imageEntered'].get_text(), \
				sf.Vector2(widgets['hTileSize'].get_value(), widgets['vTileSize'].get_value()), \
				sf.Vector2(widgets['hTileSpace'].get_value(), widgets['vTileSpace'].get_value()))
		widgets['window'].destroy()

	def createNewAnnimation(self, window, fileManager, tileBox):
		accelGroup = Gtk.AccelGroup()
		window.add_accel_group(accelGroup)
		grid = Gtk.Grid()
		vgrid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
		vgrid.add(grid)

		fileLabel = Gtk.Label("File")
		startLabel = Gtk.Label("Start point")
		endLabel = Gtk.Label("End point")

		imageEntered = Gtk.Entry()
		imageEntered.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, Gtk.STOCK_FILE)
		imageEntered.set_icon_activatable(Gtk.EntryIconPosition.SECONDARY, True)
		imageEntered.connect("icon-press", self.openImage, fileManager)
		grid.attach(fileLabel, 0, 0, 1, 1)
		grid.attach_next_to(imageEntered, fileLabel, Gtk.PositionType.RIGHT, 3, 1)
		grid.attach_next_to(startLabel, fileLabel, Gtk.PositionType.BOTTOM, 1, 1)
		grid.attach_next_to(endLabel, startLabel, Gtk.PositionType.BOTTOM, 1, 1)

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

		grid.attach_next_to(spinTileLeft, startLabel, Gtk.PositionType.RIGHT, 1, 1)
		grid.attach_next_to(xLabel, spinTileLeft, Gtk.PositionType.RIGHT, 1, 1)
		grid.attach_next_to(spinTileRight, xLabel, Gtk.PositionType.RIGHT, 1, 1)

		grid.attach_next_to(spinSpaceLeft, endLabel, Gtk.PositionType.RIGHT, 1, 1)
		grid.attach_next_to(xBisLabel, spinSpaceLeft, Gtk.PositionType.RIGHT, 1, 1)
		grid.attach_next_to(spinSpaceRight, xBisLabel, Gtk.PositionType.RIGHT, 1, 1)

		hbox = Gtk.Box()
		setTableSize = Gtk.Button(label="Set Table")
		hbox.pack_start(setTableSize, False, False, 0)

		box = Gtk.Box()
		buttonOK = Gtk.Button(label="OK")
		buttonOK.connect("clicked", self.newTileSet)
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

	def newAnnimation(self, button, widgets):
		pass

	def newStaticTrace(self, button, widgets):
		pass

	def newDynamicTrace(self, button, widgets)

	def quitWindow(self, *args, **kwargs):
		args[1].destroy()

	def openImage(self, entry, pos, event, fileManager):
		path = fileManager.openFile("image")
		if path:
			entry.set_text(path)

	def acceptNewFile(self, button, widgets):
		addString = ''
		if widgets['nameEntered'].get_text()[-4:] != ".xml":
			addString = ".xml"
		open("Files/" + widgets['nameEntered'].get_text() + addString, "w").close()
		widgets["sfmlArea"].setSFMLSize(sf.Vector2(\
				widgets["hNumberCases"].get_value(), widgets["vNumberCases"].get_value()),\
				sf.Vector2(widgets["hTileSize"].get_value(), widgets["vTileSize"].get_value()))
		widgets["sfmlArea"].get_toplevel().set_title(\
				widgets['nameEntered'].get_text().replace(".xml", ""))
		widgets["window"].destroy()
