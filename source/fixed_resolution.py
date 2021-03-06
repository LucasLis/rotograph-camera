# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

from pyglet.gl import *
import pyglet


class FixedResolution:
    def __init__(self, window, width, height, filtered=False):
        self.window = window
        self.width = width
        self.height = height
        self._filtered = filtered
        self._viewport = 0, 0, 0, 0, 0
        self._calculate_viewport(self.window.width, self.window.height)
        self.clear_color = 0, 0, 0, 1

        self.texture = pyglet.image.Texture.create(
            width, height, rectangle=True)

        if not filtered:
            pyglet.image.Texture.default_min_filter = GL_NEAREST
            pyglet.image.Texture.default_mag_filter = GL_NEAREST
            glTexParameteri(
                self.texture.target,
                GL_TEXTURE_MAG_FILTER, GL_NEAREST
            )
            glTexParameteri(
                self.texture.target,
                GL_TEXTURE_MIN_FILTER, GL_NEAREST
            )

        def on_resize(w, h):
            self._calculate_viewport(w, h)
            self.window_w, self.window_h = w, h

        self.window.on_resize = on_resize

    def _calculate_viewport(self, new_screen_width, new_screen_height):
        aspect_ratio = self.width / self.height
        aspect_width = new_screen_width
        aspect_height = aspect_width / aspect_ratio + 0.5
        if aspect_height > new_screen_height:
            aspect_height = new_screen_height
            aspect_width = aspect_height * aspect_ratio + 0.5

        if not self._filtered:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        self._viewport = (
            int((new_screen_width / 2) - (aspect_width / 2)),     # x
            int((new_screen_height / 2) - (aspect_height / 2)),   # y
            0,                                                    # z
            int(aspect_width),                                    # width
            int(aspect_height)                                    # height
        )

    def __enter__(self):
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -255, 255)
        glMatrixMode(GL_MODELVIEW)

    def __exit__(self, *unused):
        win = self.window
        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        self.texture.blit_into(buffer, 0, 0, 0)

        glViewport(0, 0, win.width, win.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, win.width, 0, win.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)

        glClearColor(*self.clear_color)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        self.texture.blit(*self._viewport)

    def begin(self):
        self.__enter__()

    def end(self):
        self.__exit__()
