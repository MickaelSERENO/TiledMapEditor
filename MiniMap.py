from gi.repository import Gtk, GdkPixbuf, Gdk
from SFMLArea import *
from TraceTile import *
import cairo

class MiniMap():
    def __init__(self, notebook):
        self.image = Gtk.Image.new()
        self.pixbuf = None
        self.renderTexture = None
        notebook.append_page(self.image, Gtk.Label("MiniMap"))
        self.image.connect('size-allocate', self.scalePixbuf)
        self.image.set_size_request(150,150)
        self.image.connect('notify::position', self.scalePixbuf)

        self.imageTexture = None

    def update(self, render):
        if not render:
            return

        self.renderTexture = render

        self.imageTexture = render.texture.to_image()
        data = self.imageTexture.pixels.data
        if data:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_data(data, GdkPixbuf.Colorspace.RGB,\
                    True, 8, render.texture.width, render.texture.height, 4*render.texture.width,\
                    None, None)

            self.scalePixbufFromAllocation(self.image, self.image.get_allocation())
        else:
            self.pixbuf = None

    def scalePixbuf(self, *args, **kwargs):
        allocation = self.image.get_allocation()
        self.scalePixbufFromAllocation(self.image, allocation)

        return True

    def scalePixbufFromAllocation(self, widget, allocation):
        if not self.pixbuf or not self.renderTexture:
            return

        scale = min(float(allocation.width)/float(self.renderTexture.texture.width),\
                float(allocation.height)/float(self.renderTexture.texture.height))
        scale*=0.9

        size = sf.Vector2(scale, scale) * self.renderTexture.texture.size

        if size.x > 1 and size.y > 1:
            pix = self.pixbuf.scale_simple(size.x, size.y, GdkPixbuf.InterpType.BILINEAR)
            if pix:
                self.image.set_from_pixbuf(pix)
