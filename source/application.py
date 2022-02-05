from .audio_manager import AudioManager
from .video_manager import VideoManager
from .fixed_resolution import FixedResolution

import pyglet
from pyglet.window import key
from pyglet.math import Vec2


pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST
pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST


class Application:
    LENGTH = 3
    TARGET_RESOLUTION = Vec2(640, 360)

    def __init__(self):
        self.window = pyglet.window.Window(
            *self.TARGET_RESOLUTION,
            resizable=True
        )
        self.fps = pyglet.window.FPSDisplay(self.window)
        self.window.set_minimum_size(*self.TARGET_RESOLUTION)
        self.window.push_handlers(self)

        self.viewport = FixedResolution(self.window, *self.TARGET_RESOLUTION)
        self.batch = pyglet.graphics.Batch()

        self.video_manager = VideoManager(0, self.TARGET_RESOLUTION)
        self.video_manager.push_handlers(self)

        self.audio_manager = AudioManager()

        self.preview_sprite = pyglet.sprite.Sprite(
            self.video_manager.image,
            self.TARGET_RESOLUTION.x // 2, self.TARGET_RESOLUTION.y // 2,
            batch=self.batch,
        )

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.video_manager.start_recording(self.LENGTH)
            if self.video_manager.fps != 0:
                self.audio_manager.start_recording()
            print("Starting recording")

    def on_draw(self):
        self.window.clear()
        with self.viewport:
            self.batch.draw()
        self.fps.draw()

    def on_frame_ready(self):
        self.preview_sprite.image = self.video_manager.image

    def on_recording_finished(self):
        if self.video_manager.fps != 0:
            self.audio_manager.stop_recording()
            self.audio_manager.save()
        self.video_manager.save()
        print("Video (and audio) saved")

    def run(self):
        pyglet.app.run()
