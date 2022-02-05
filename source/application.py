from .audio_manager import AudioManager
from .video_manager import VideoManager
from .fixed_resolution import FixedResolution
from .interface import Interface, Layers

import pyglet
from pyglet.window import key
from pyglet.graphics import OrderedGroup
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

        self.video_manager = VideoManager(10, self.TARGET_RESOLUTION)
        self.video_manager.push_handlers(self)

        self.audio_manager = AudioManager()

        self.preview_sprite = pyglet.sprite.Sprite(
            self.video_manager.image,
            self.TARGET_RESOLUTION.x // 2, self.TARGET_RESOLUTION.y // 2,
            group=OrderedGroup(Layers.PREVIEW),
            batch=self.batch,
        )

        self.interface = Interface(
            self.batch,
            self.video_manager.fps,
            self.TARGET_RESOLUTION
        )

    def on_key_press(self, symbol, modifiers):
        match symbol:
            case key.SPACE:
                self.video_manager.start_recording(self.LENGTH)
                if self.video_manager.fps != 0:
                    self.audio_manager.start_recording()
                print("Starting recording")
                self.interface.recording = True
            case key.PERIOD:
                self.interface.crosshair = not self.interface.crosshair
            case key.COMMA:
                self.interface.grid = not self.interface.grid
            case key.EQUAL:
                self.video_manager.fps += 1
                self.interface.fps = self.video_manager.fps
            case key.MINUS:
                self.video_manager.fps -= 1
                self.interface.fps = self.video_manager.fps
            case key.A:
                self.interface.about = not self.interface.about
            case key.S:
                self.interface.settings = not self.interface.settings

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
        self.interface.recording = False

    def run(self):
        pyglet.app.run()
