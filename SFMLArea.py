from gi.repository import Gtk, Gdk, GObject
import sfml as sf
from TileBox import TileBox
from copy import copy

class SFMLArea(Gtk.DrawingArea):
	def __init__(self, hslide, vslide, numberCases, sizeCase):
		Gtk.DrawingArea.__init__(self)
		self.hslide = hslide
		self.vslide = vslide
		self.render = sf.HandledWindow()
		self.size = numberCases * sizeCase
		self.sizeCase = sizeCase

		#self.connect("size-allocate", self.resize)
		self.connect("drag-data-received", self.do_drag_data_received)
		self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
		targets = Gtk.TargetList.new([])
		targets.add_image_targets(0, True)

		self.drag_dest_set_target_list(targets)
		self.timemoutUpdate = GObject.timeout_add(20, self.draw)

		self.popupFull = None
		self.popupEmpty = None
		self.setSlideProperties()

		self.listTrace = list()

	def setSlideProperties(self):
		self.vslide.connect("value-changed", self.moveView, "vertical")
		self.hslide.connect("value-changed", self.moveView, "horizontal")

	def setSFMLSize(self, numberCases=None, tileSize=None):
		if tileSize:
			self.sizeCase = tileSize
		if numberCases:
			self.size = numberCases * self.sizeCase
		self.render.size.x = min(self.render.size.x, self.size.x)
		self.render.size.y = min(self.render.size.y, self.size.y)
		self.render.view.size = copy(self.render.size)
		self.updateSlideValues()
		self.get_toplevel().show_all()

	def updateSlideValues(self):
		self.vslide.set_adjustment(Gtk.Adjustment(min(self.size.y-self.render.view.size.y,\
				self.vslide.get_value()), 0, self.size.y - self.render.view.size.y, 1, 10, 0))
		self.hslide.set_adjustment(Gtk.Adjustment(min(self.size.x-self.render.view.size.x,\
				self.hslide.get_value()), 0, self.size.x - self.render.view.size.x, 1, 10, 0))

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
		delCase = Gtk.Action("DelCase", "Delete", None, None)
		delCase.connect("activate", self.manageTile, "delete")
		actionGroup.add_action(delCase)

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
			self.render.view.size = sf.Vector2(allocation.width, allocation.height)
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
		self.drawQuad()
		for trace in self.listTrace:
			trace.update()
		self.render.display()
		return True
		
	def drawQuad(self):
		position = self.render.view.center - self.render.view.size / 2
		size = self.render.view.size

		posX = max(self.sizeCase.x * int(position.x/self.sizeCase.x), 0)
		posY = max(self.sizeCase.y * int(position.y/self.sizeCase.y), 0)

		lineX = sf.VertexArray(sf.PrimitiveType.LINES, 2)
		lineY = sf.VertexArray(sf.PrimitiveType.LINES, 2)
		lineX[0].color = sf.Color.WHITE
		lineX[1].color = sf.Color.WHITE
		lineX[0].position = sf.Vector2(posX, max(position.y, 0))
		lineX[1].position = sf.Vector2(posX, min(position.y+size.y, self.size.y))

		while lineX[0].position.x < position.x + size.x and not lineX[0].position.x > self.size.x:
			self.render.draw(lineX)
			lineX[0].position += sf.Vector2(self.sizeCase.x, 0)
			lineX[1].position += sf.Vector2(self.sizeCase.x, 0)

		lineY[0].color = sf.Color.WHITE
		lineY[1].color = sf.Color.WHITE
		lineY[0].position = sf.Vector2(max(position.x, 0), posY)
		lineY[1].position = sf.Vector2(min(position.x+size.x, self.size.x), posY)

		while lineY[0].position.y < position.y + size.y and not lineY[0].position.y > self.size.y:
			self.render.draw(lineY)
			lineY[0].position += sf.Vector2(0, self.sizeCase.y)
			lineY[1].position += sf.Vector2(0, self.sizeCase.y)

	def do_drag_data_received(self, widget, context, x, y, selection_data, info, time=None):
		dndDatas = TileBox.dndDatas
		print(dndDatas)

	def manageTile(self, action):
		pass

	def buttonPressEvent(self, widget, event):
		if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
			self.popupEmpty.popup(None, None, None, None, event.button, event.time)

class Trace:
	def __init__(self, sfmlArea):
		self.sfmlArea = sfmlArea
		self.listTile = list(list())

	def update(self):
		for tile in [tile for content in self.listTile for tile in content]:
			tile.update()

class Tile:
	def __init__(self):
		pass
