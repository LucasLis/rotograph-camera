import pyglet
from pyglet.gl import *

class ScissorGroup(pyglet.graphics.Group):
    """A Custom Group that defines a "Scissor" area.
    If a Sprite/Label is in this Group, any parts of it that
    fall outside of the specified area will not be drawn.
    NOTE: You should use the same exact group instance
    for every object that will use the group, equal groups
    will still be kept seperate.
    :Parameters:
        `x` : int
            The X coordinate of the Scissor area.
        `x` : int
            The X coordinate of the Scissor area.
        `width` : int
            The width of the Scissor area.
        `height` : int
            The height of the Scissor area.
    """

    def __init__(self, x, y, width, height, parent=None):
        super().__init__(parent)
        self.x, self.y = x, y
        self.width, self.height = width, height

    @property
    def area(self):
        return self.x, self.y, self.width, self.height

    @area.setter
    def area(self, area):
        self.x, self.y, self.width, self.height = area

    def set_state(self):
        glEnable(GL_SCISSOR_TEST)
        glScissor(self.x, self.y, self.width, self.height)

    def unset_state(self):
        glDisable(GL_SCISSOR_TEST)
