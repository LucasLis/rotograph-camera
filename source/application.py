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
            caption="Rotograph Camera",
            resizable=True
        )
        self.fps = pyglet.window.FPSDisplay(self.window)
        self.window.set_minimum_size(*self.TARGET_RESOLUTION)
        self.window.push_handlers(self)

        self.viewport = FixedResolution(self.window, *self.TARGET_RESOLUTION)
        self.batch = pyglet.graphics.Batch()

        self.video_manager = VideoManager(24, self.TARGET_RESOLUTION)
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
        self.interface.push_handlers(self)

    def save(self, dt: float = None):
        if self.video_manager.fps != 0:
            self.audio_manager.save()
        self.video_manager.save()
        self.interface.saving = False

    def start_recording(self):
        if self.video_manager.fps != 0:
            self.interface.recording = True
            self.video_manager.start_recording()
            if not self.interface.mute:
                self.audio_manager.start_recording()
        else:
            self.interface.saving = True
            pyglet.clock.schedule_once(self.save, 0.2)

    def stop_recording(self):
        self.interface.recording = False

        self.video_manager.stop_recording()
        if self.video_manager.fps != 0:
            self.audio_manager.stop_recording()

        self.interface.saving = True
        pyglet.clock.schedule_once(self.save, 0.2)

    def on_mouse_release(self, x, y, button, modifiers):
        x -= self.viewport._viewport[0]
        y -= self.viewport._viewport[1]
        x *= self.TARGET_RESOLUTION.x / (self.viewport._viewport[3])
        y *= self.TARGET_RESOLUTION.y / (self.viewport._viewport[4])
        self.interface.mouse_released(x, y)

    def on_key_press(self, symbol, modifiers):
        match symbol:
            case key.F11:
                self.window.set_fullscreen(not self.window.fullscreen)

    def on_fps_change(self, new_fps):
        self.video_manager.fps = new_fps
        self.interface.fps = self.video_manager.fps

    def on_rec_pressed(self):
        if self.video_manager.recording:
            self.stop_recording()
        elif self.interface.timer:
            if self.interface.timer_running:
                self.interface.abort_timer()
            else:
                self.interface.start_timer()
        else:
            self.start_recording()

    def on_monochrome_change(self, new_value: bool):
        self.video_manager.monochrome = new_value

    def on_timer_complete(self):
        self.start_recording()

    def on_draw(self):
        self.window.clear()
        with self.viewport:
            self.batch.draw()
        self.fps.draw()

    def on_frame_ready(self):
        self.preview_sprite.image = self.video_manager.image

    def run(self):
        pyglet.app.run()
