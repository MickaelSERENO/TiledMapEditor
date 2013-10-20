from gi.repository import Gtk, GdkPixbuf, Gdk, GObject
from os import path
from copy import copy
import sfml as sf

class TileBox(Gtk.Paned):
	textureList = dict()
	dndDatas = None
	def __init__(self):
		scrolledWindow = Gtk.ScrolledWindow()
		Gtk.Paned.__init__(self)
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

		self.set_size_request(500, 300)
		scrolledWindow.add(self.box)
		scrolledWindow.set_size_request(100, 300)
		self.pack1(scrolledWindow)

	def cutTileSet(self, tileSetFile, size=sf.Vector2(32, 32), spacing=sf.Vector2(0, 0)):
		if tileSetFile and path.isfile(tileSetFile):
			tileSetFile = path.relpath(path.abspath(tileSetFile), path.abspath(path.dirname(__file__)))

			if tileSetFile in TileBox.textureList:
				return
			else:
				TileBox.textureList[tileSetFile] = sf.Texture.from_file(tileSetFile)

			expander = Gtk.Expander()
			expander.set_label(tileSetFile)

			treeStore = Gtk.TreeStore(GdkPixbuf.Pixbuf, int, int)

			image = Gtk.Image()
			image.set_from_file(tileSetFile)
			originPixbuf = image.get_pixbuf()
			posX = 0
			posY = 0

			while posY < originPixbuf.get_height():
				pixbuf = TileIcon.new(GdkPixbuf.Colorspace.RGB, True, 8, size.x, size.y, \
						sf.Rectangle(sf.Vector2(posX, posY), size))

				originPixbuf.copy_area(posX, posY, min(size.x, originPixbuf.get_width() - posX), \
						min(size.y, originPixbuf.get_height() - posY),	pixbuf, 0, 0)
				listPixbuf = [pixbuf, posX, posY]
				posX += size.x + spacing.x
				if posX >= originPixbuf.get_width():
					posX = 0
					posY += size.y + spacing.y
				treeStore.append(None, listPixbuf)
			viewIcon = DragIconView(model=treeStore, size=size, spacing=spacing, numColumn=self.numColumn)
			viewIcon.set_columns(self.numColumn)
			viewIcon.set_pixbuf_column(0)
			viewIcon.set_name(tileSetFile)

			expander.add(viewIcon)
			self.staticBox.pack_start(expander, True, True, 0)
			self.show_all()
			
class DragIconView(Gtk.IconView):
	def __init__(self, model, size, spacing, numColumn):
		Gtk.IconView.__init__(self, model)
		self.size = size
		self.spacing = spacing
		self.numColumn = numColumn
		self.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)
		self.connect("drag-data-get", self.do_drag_data_get)

		targets = Gtk.TargetList.new([])
		targets.add_image_targets(0, True)
		self.drag_source_set_target_list(targets)

	def do_drag_data_get(self, widget, context, selection_data, info, time=None):
		if time:
			selected_path = self.get_selected_items()[0]
			selected_iter = self.get_model().get_iter(selected_path)
			selection_data.set_pixbuf(self.get_model().get_value(selected_iter, 0))

			TileBox.dndDatas = {'spacing':self.spacing, 'size':self.size, \
					'position':self.getWidgetPosition(selected_path), 'file':self.get_name(),\
					'numColumn':self.numColumn, 'subRect':self.get_model().get_value(selected_iter, 0).rect}

	def getWidgetPosition(self, path):
		return self.get_columns() * self.get_item_row(path) +\
				self.get_item_column(path)

	def getXYWidgetPosition(self, path):
		vector = sf.Vector2()
		vector.x = self.get_model().get_value(self.get_model().get_iter(path), 1)
		vector.y = self.get_model().get_value(self.get_model().get_iter(path), 2)
		return vector

	def getIconSubRect(self, path):
		vector = self.getXYWidgetPosition(self, path)
		rect = sf.Rectangle()
		rect.pos = (vector)*(self.spacing+self.size)
		rect.size = copy(self.size)
		return rect

class TileIcon(GdkPixbuf.Pixbuf):
	def new(color, tf, deep, sizex, sizey, rect):
		objet = GdkPixbuf.Pixbuf.new(color, tf, deep, sizex, sizey)
		objet.rect = rect
		return objet
