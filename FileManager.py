from gi.repository import Gtk

class FileManager():
	def __init__(self, parent):
		self.parent = parent

	def _getFileName(self, dialog, filt):
		self.setFilter(dialog, filt)
		response = dialog.run()

		filename = None
		if response == Gtk.ResponseType.OK:
			filename = dialog.get_filename()
		dialog.destroy()
		return filename

	def openFile(self, filt="xml"):
		dialog = Gtk.FileChooserDialog("Choose a valid xml file", self.parent,\
				Gtk.FileChooserAction.OPEN, (Gtk.STOCK_OPEN, Gtk.ResponseType.OK,\
				Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

		return self._getFileName(dialog, filt)

	def saveFile(self):
		dialog = Gtk.FileChooserDialog("Where to save the map ?", self.parent, \
				Gtk.FileChooserAction.SAVE, (Gtk.STOCK_SAVE, Gtk.ResponseType.OK, \
				Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

		return self._getFileName(dialog)
	
	def setFilter(self, dialog, filt):
		if filt=="xml":
			filterXML = Gtk.FileFilter()
			filterXML.set_name("XML File")
			filterXML.add_mime_type("application/xml")
			dialog.add_filter(filterXML)
		elif filt=="image":
			filterImage = Gtk.FileFilter()
			filterImage.set_name("Image File")
			filterImage.add_mime_type("image/png")
			filterImage.add_mime_type("image/jpeg")
			filterImage.add_mime_type("image/bmp")
			dialog.add_filter(filterImage)

