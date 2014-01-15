from gi.repository import Gtk, Gdk, GObject
import sfml as sf
from TileBox import TileBox
from copy import copy
from TraceTile import Trace, Tile
import globalVar

class SFMLArea(Gtk.DrawingArea):
	def __init__(self, hslide, vslide, numberCases, sizeCase):
		Gtk.DrawingArea.__init__(self)
		self.hslide = hslide
		self.vslide = vslide
		self.render = sf.HandledWindow()
		self.size = numberCases * sizeCase
		self.sizeCase = sizeCase
		self.numberCases = numberCases
		self.set_can_focus(True)

		self.connect("drag-data-received", self.do_drag_data_received)
		self.connect("key-press-event", self.keyPressEvent)
		self.connect("motion_notify_event", self.mouseMoveEvent) 
		self.connect("button-press-event", self.buttonPressEvent)
		self.connect("button-release-event", self.buttonReleaseEvent)
		self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
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

	def setSFMLSize(self, numberCases=None):
		if numberCases:
			self.size = numberCases * self.sizeCase
			for trace in self.listTrace:
				trace.initStaticList(self.sizeCase)
		self.render.size.x = min(self.render.size.x, self.size.x)
		self.render.size.y = min(self.render.size.y, self.size.y)
		self.render.view.size = copy(self.render.size)
		self.updateSlideValues()
		self.get_toplevel().show_all()

	def updateSlideValues(self):
		self.vslide.set_adjustment(Gtk.Adjustment(self.render.view.center.y - self.render.view.size.y/2,\
				0, self.size.y - self.render.view.size.y, 1, 10, 0))
		self.hslide.set_adjustment(Gtk.Adjustment(self.render.view.center.x - self.render.view.size.x/2,\
				0, self.size.x - self.render.view.size.x, 1, 10, 0))

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
		actionGroup.get_action("DelCase").connect("activate", self.manageTile, "delete")

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
			alloc = sf.Vector2(allocation.width, allocation.height)
			self.render.view.size = alloc
			self.render.view.center = alloc/2
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
		for trace in self.listTrace:
			if trace.show:
				trace.update()
		self.render.display()
		return True

	def updateLastEventTrace(self, event):
		for trace in self.listTrace[::-1]:
			if trace.show:
				trace.updateEventTile(event)
				return
		

	def do_drag_data_received(self, widget, context, x, y, selection_data, info, time=None):
		if time:
			for trace in self.listTrace[::-1]:
				if trace.show:
					pos = self.render.map_pixel_to_coords(sf.Vector2(x, y), self.render.view)
					trace.addTile(pos.x, pos.y)
					return

	def manageTile(self, action):
		pass

	def buttonPressEvent(self, widget, event):
		if event.type == Gdk.EventType.BUTTON_PRESS:
			if event.button == 3:
				self.popupEmpty.popup(None, None, None, None, event.button, event.time)
			elif event.button == 1:
				self.get_toplevel().set_focus(self)
		self.updateLastEventTrace(event)

	def buttonReleaseEvent(self, widget, event):
		if event.type == Gdk.EventType.BUTTON_RELEASE:
			self.updateLastEventTrace(event)

	def keyPressEvent(self, widget, event):
		if event.type == Gdk.EventType.KEY_PRESS:
			if event.keyval == Gdk.KEY_Delete:
				self.listTrace[-1].deleteTile()

	def mouseMoveEvent(self, widget, event):
		if event.type == Gdk.EventType.MOTION_NOTIFY:
			self.updateLastEventTrace(event)


	def addTrace(self, tileSize, style):
		self.listTrace.append(Trace(tileSize, style))
		self.listTrace[-1].initStaticList(self.size)

