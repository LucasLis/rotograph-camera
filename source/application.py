from .camera import Camera
from .video_manager import VideoManager
from .scissor import ScissorGroup

import pyglet
from pyglet.window import key


pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST
pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST


class Application:
    def __init__(self):
        self.camera = Camera(0, 0)

        self.batch = pyglet.graphics.Batch()

        self.video_manager = VideoManager(0)

        self.scissor = ScissorGroup(0, 0, 640, 360, parent=self.camera)
        self.sprite = pyglet.sprite.Sprite(
            self.video_manager.image,
            0, 0,
            group=self.scissor,
            batch=self.batch,
        )

        self.window = pyglet.window.Window(
            *self.camera.VIEW_RESOLUTION,
            resizable=True
        )
        self.window.set_minimum_size(*self.camera.VIEW_RESOLUTION)
        self.window.push_handlers(self)
        self.window.push_handlers(self.camera)

        self.fps = pyglet.window.FPSDisplay(self.window)

        fps = self.video_manager.FPS
        if fps == 0:
            fps = 24
        pyglet.clock.schedule_interval(self.on_frame, 1/fps)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.video_manager.start_recording(5)
            print("Starting recording")

    def on_draw(self):
        self.window.clear()
        self.batch.draw()
        self.fps.draw()

    def on_frame(self, dt: float):
        self.video_manager.update()
        self.sprite.image = self.video_manager.image

    def on_resize(self, width: int, height: int):
        scale = self.camera.get_viewport_scale()
        t_width, t_height = self.camera.VIEW_RESOLUTION
        self.scissor.width = int(scale * t_width)
        self.scissor.height = int(scale * t_height)
        self.scissor.x = round(width - self.scissor.width) // 2
        self.scissor.y = round(height - self.scissor.height) // 2

    def run(self):
        pyglet.app.run()
