from gi.repository import Gtk
from os import path
import xml.etree.ElementTree as ET
import globalVar

class FileManager():
    def __init__(self, parent):
        self.parent = parent
        self.xmlFile = str()

    def _getFileName(self, dialog, filt):
        self.setFilter(dialog, filt)
        response = dialog.run()

        filename = None
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
        dialog.destroy()
        return filename

    def _openFile(self, mime):
        dialog = Gtk.FileChooserDialog("Choose a file", self.parent,\
                Gtk.FileChooserAction.OPEN, (Gtk.STOCK_OPEN, Gtk.ResponseType.OK,\
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        return self._getFileName(dialog, mime)

    def openFileXML(self, tileBox, traceManager, objectManager):
        fileName = self._openFile("xml")

        if not fileName:
            return
        xmlTree = ET.parse(fileName)
        xmlRoot = xmlTree.getroot()

        globalVar.tileWindow.decodeXML(xmlRoot.find('Window'))
        tileBox.decodeXML(xmlRoot.find('Files'), path.dirname(fileName))
        objectManager.decodeXML(xmlRoot.find('Objects'), tileBox)
        traceManager.decodeXML(xmlRoot.find('Traces'), tileBox, objectManager)

        self.xmlFile = fileName

    def openFileImage(self):
        return self._openFile('image')

    def saveAsFile(self, tileBox, traceManager, objectManager):
        dialog = Gtk.FileChooserDialog("Where to save the map ?", self.parent, \
                Gtk.FileChooserAction.SAVE, (Gtk.STOCK_SAVE, Gtk.ResponseType.OK, \
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        xmlFile = self._getFileName(dialog, filt="xml")
        if xmlFile:
            self.xmlFile = xmlFile
            self.saveFile(tileBox, traceManager, objectManager)

    def saveFile(self, tileBox, traceManager, objectManager):
        xmlRoot = ET.fromstring('<map></map>')
        xmlRoot.append(globalVar.tileWindow.getSaveFileElem())
        xmlRoot.append(tileBox.getSaveFileElem())
        xmlRoot.append(objectManager.getSaveFileElem(tileBox))
        xmlRoot.append(traceManager.getSaveFileElem(tileBox, objectManager))

        with open(self.xmlFile, 'w') as xmlFile:
            xmlFile.write(str(ET.tostring(xmlRoot).decode()))

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
