import sfml as sf

def rectCollision(rect1,rect2):
	return not (rect1.left + rect1.width < rect2.left or \
		rect1.left > rect2.left + rect2.width or \
		rect1.top + rect1.height < rect2.top or \
		rect1.top > rect2.top+rect2.height)

def circle(x, centerx, centery, size):
	y1 = (2*centery + sqrt(4*(-(x-centerx)*(x-centerx)+size*size)))/2
	y2 = (2*centery - sqrt(4*(-(x-centerx)*(x-centerx)+size*size)))/2
	return sf.Vector2f(y1, y2)

def isInEllipse(pos, center, radius):
	return (pos.x - center.x)**2 / radius.x**2 + \
			(pos.y - center.y)**2 / radius.y**2 <= 1

def isMouseInRect(self, rect, mousePos):
	if mousePos.x > rect.left and\
			mousePos.y > rect.top and\
			mousePos.x < rect.left + rect.width and\
			mousePos.y < rect.top + rect.height :
		return True
	return False
