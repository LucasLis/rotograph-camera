import pyglet
from pyglet.math import Vec2
from pyglet.graphics import OrderedGroup

from enum import IntEnum


class Layers(IntEnum):
    PREVIEW = 0
    MAIN_UI = 1
    BUTTONS = 2
    WINDOW = 3
    WINDOW_UI = 4


class Interface:
    _grid = False
    _crosshair = False
    _recording = False
    _about = False
    _settings = False
    _fps = 0

    def __init__(
            self,
            batch: pyglet.graphics.Batch,
            fps: int,
            target_resolution: Vec2
    ):
        self.batch = batch
        self.target_resolution = target_resolution

        self.init_main_ui()
        self.init_about_window()
        self.init_settings_window()

        self.fps = fps

    def init_main_ui(self):
        self.main_ui = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Camera Default.png"),
            0, 0,
            batch=self.batch,
            group=OrderedGroup(Layers.MAIN_UI)
        )
        self.main_ui.scale = 2

        self.grid_sprite = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Grid.png"),
            0, 0,
            batch=self.batch,
            group=OrderedGroup(Layers.MAIN_UI)
        )
        self.grid_sprite.scale = 2
        self.grid_sprite.visible = self.grid

        self.crosshair_sprite = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Crosshair.png"),
            0, 0,
            batch=self.batch,
            group=OrderedGroup(Layers.MAIN_UI)
        )
        self.crosshair_sprite.scale = 2
        self.crosshair_sprite.visible = self.crosshair

        self.fps_display = pyglet.sprite.Sprite(
            pyglet.resource.image(f"assets/{self.fps:02}.png"),
            self.target_resolution.x-32,
            self.target_resolution.y-24,
            batch=self.batch,
            group=OrderedGroup(Layers.BUTTONS)
        )
        self.fps_display.scale = 2

        self.settings_button = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/SettingsIcon.png"),
            self.target_resolution.x-124,
            self.target_resolution.y-26,
            batch=self.batch,
            group=OrderedGroup(Layers.BUTTONS)
        )
        self.settings_button.scale = 2

        self.about_button = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/AboutIcon.png"),
            self.target_resolution.x-100,
            self.target_resolution.y-26,
            batch=self.batch,
            group=OrderedGroup(Layers.BUTTONS)
        )
        self.about_button.scale = 2

    def init_about_window(self):
        self.about_window = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/About.png"),
            0, 0,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW)
        )
        self.about_window.scale = 2
        self.about_window.visible = self.about

    def init_settings_window(self):
        self.settings_window = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Settings.png"),
            0, 0,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW)
        )
        self.settings_window.scale = 2
        self.settings_window.visible = self.settings

    @property
    def grid(self) -> bool:
        return self._grid

    @grid.setter
    def grid(self, value: bool):
        self._grid = value
        self.grid_sprite.visible = value

    @property
    def crosshair(self) -> bool:
        return self._crosshair

    @crosshair.setter
    def crosshair(self, value: bool):
        self._crosshair = value
        self.crosshair_sprite.visible = value

    @property
    def recording(self) -> bool:
        return self._recording

    @recording.setter
    def recording(self, value: bool):
        self._recording = value
        if value:
            image = pyglet.resource.image("assets/Camera Recording.png")
        else:
            image = pyglet.resource.image("assets/Camera Default.png")
        self.main_ui.image = image

    @property
    def about(self) -> bool:
        return self._about

    @about.setter
    def about(self, value: bool):
        if self.settings:
            self.settings = False
        self._about = value
        self.about_window.visible = value

    @property
    def settings(self) -> bool:
        return self._settings

    @settings.setter
    def settings(self, value: bool):
        if self.about:
            self.about = False
        self._settings = value
        self.settings_window.visible = value

    @property
    def fps(self) -> int:
        return self._fps

    @fps.setter
    def fps(self, value: int):
        self._fps = value
        image = pyglet.resource.image(f"assets/{value:02}.png")
        self.fps_display.image = image
