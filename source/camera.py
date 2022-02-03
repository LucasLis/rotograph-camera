
""" Camera system using graphics groups.

Classes:

    Camera
"""

import pyglet
from pyglet.graphics import Group
from pyglet.math import Vec2

from typing import Optional


class Camera(Group):
    """ Pyglet graphics group emulating the behaviour of a camera in 2D space.
    """

    # Define a target viewport resolution
    VIEW_RESOLUTION = Vec2(640, 360)

    # Define a starting window size, this will be immediately overwritten by
    # the on_resize event
    window_size = Vec2(0, 0)

    def __init__(
        self,
        x: float, y: float,  # Position
        zoom: float = 1.0,
        parent_group: Optional[Group] = None
    ):
        """ Initialise group with parent, zoom and position. """
        super().__init__(parent_group)
        self.zoom = zoom

    def on_resize(self, width: float, height: float):
        """ Called (through GameManager) every time the window is resized. """
        # Store window size
        self.window_size = Vec2(width, height)

    def get_viewport_scale(self) -> float:
        """ Get the scale required to resize the viewport to the intended size.

        Use min() here to find the smaller of the two axis' zooms.
        """
        return min(
            self.window_size.x / self.VIEW_RESOLUTION.x,
            self.window_size.y / self.VIEW_RESOLUTION.y
        )

    def set_state(self):
        """ Apply zoom and camera offset to view matrix. """
        # Calculate the total zoom amount
        zoom = self.get_viewport_scale() * self.zoom
        # Move the viewport
        pyglet.gl.glTranslatef(
            self.window_size.x/2,
            self.window_size.y/2,
            0
        )
        # Scale the viewport
        pyglet.gl.glScalef(zoom, zoom, 1)

    def unset_state(self):
        """ Revert zoom and camera offset from view matrix. """
        # Do the inverse of `set_state`
        zoom = self.get_viewport_scale() * self.zoom
        pyglet.gl.glScalef(1 / zoom, 1 / zoom, 1)
        pyglet.gl.glTranslatef(
            -self.window_size.x/2,
            -self.window_size.y/2,
            0
        )
