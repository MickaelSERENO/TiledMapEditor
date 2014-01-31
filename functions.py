import sfml as sf
from gi.repository import Gtk

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

def isMouseInRect(rect, mousePos):
    if mousePos.x > rect.left and\
            mousePos.y > rect.top and\
            mousePos.x < rect.left + rect.width and\
            mousePos.y < rect.top + rect.height :
        return True
    return False

def copyTreeStore(tree):
    newTree = Gtk.TreeStore()
    newTree.set_column_types([tree.get_column_type(t) for t in range(tree.get_n_columns())])
    if not len(tree):
        return newTree

    parent=newTree.append(None)
    for i in range(tree.get_n_columns()):
        newTree.set_value(parent, i, tree.get_value(tree.get_iter_first(), i))

    getChildrenOfTreeStore(newTree, tree, getTreeStoreChild(tree, tree.get_iter_first()), parent)
        
    return newTree

def getChildrenOfTreeStore(newTree, tree, child, parent):
    for i in range(len(child)):
        numberColumn = tree.get_n_columns()
        newParent = newTree.insert_with_values(parent, -1, range(numberColumn), \
                [tree.get_value(child[i], val) for val in range(numberColumn)])
        getChildrenOfTreeStore(newTree, tree, getTreeStoreChild(tree, child[i]), child[i])

def getTreeStoreChild(tree, parent):
    return [tree.iter_nth_child(parent, i)\
        for i in range(tree.iter_n_children(parent))]
