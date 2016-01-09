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
        self.image.connect('size-allocate', self.scalePixbufFromAllocation)
        self.image.set_size_request(150,150)
        self.image.connect('notify::position', self.scalePixbuf)
        self.imageTexture = None

    def update(self, tileMapSprite, position, size):
        if not tileMapSprite:
            return
        render = sf.RenderTexture(tileMapSprite.texture.width, tileMapSprite.texture.height)
        render.clear(sf.Color(0,0,0,0))
        if tileMapSprite:
            render.draw(tileMapSprite)

        rectangleShape = sf.RectangleShape()
        rectangleShape.size = size - sf.Vector2(2*10,2*10)
        rectangleShape.position = position + sf.Vector2(10,10)
        rectangleShape.outline_color = sf.Color(255,0,0,255)
        rectangleShape.fill_color = sf.Color(0,0,0,0)
        rectangleShape.outline_thickness = 10

        render.draw(rectangleShape)
        render.display()

        self.renderTexture = render

        self.imageTexture = render.texture.to_image()
        data = self.imageTexture.pixels.data

        self.pixbuf = GdkPixbuf.Pixbuf.new_from_data(data, GdkPixbuf.Colorspace.RGB,\
                True, 8, render.texture.width, render.texture.height, 4*render.texture.width,\
                None, None)

        scale = min(float(self.image.get_allocated_width())/float(render.texture.width),\
                float(self.image.get_allocated_height())/float(render.texture.height))

        pix = self.pixbuf.scale_simple(render.texture.width * scale,\
                render.texture.height*scale, GdkPixbuf.InterpType.NEAREST)
        self.image.set_from_pixbuf(pix)

    def scalePixbuf(self, *args, **kwargs):
        allocation = self.image.get_allocation()
        allocation.width = allocation.width-5
        allocation.height = allocation.height-5
        self.scalePixbufFromAllocation(self.image, allocation)

        return True

    def scalePixbufFromAllocation(self, widget, allocation):
        if not self.pixbuf:
            return


        scale = min(float(allocation.width)/float(self.renderTexture.texture.width),\
                float(allocation.height)/float(self.renderTexture.texture.height))

        size = sf.Vector2(scale, scale) * self.renderTexture.texture.size
        pix = self.pixbuf.scale_simple(size.x, size.y, GdkPixbuf.InterpType.NEAREST)

        self.image.set_from_pixbuf(pix)


