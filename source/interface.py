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


class Interface(pyglet.event.EventDispatcher):
    _grid = False
    _crosshair = False
    _recording = False
    _saving = False
    _storage_message = False
    _about = False
    _settings = False
    _fps = 0
    _mute = False
    _monochrome = False
    _timer = False

    timer_running = False

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

        self.player = pyglet.media.Player()

    def init_main_ui(self):
        self.main_ui = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Main UI.png"),
            0, 0,
            batch=self.batch,
            group=OrderedGroup(Layers.MAIN_UI)
        )
        self.main_ui.scale = 2

        self.rec_button = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Rec Idle.png"),
            6, self.target_resolution.y-24,
            batch=self.batch,
            group=OrderedGroup(Layers.BUTTONS)
        )
        self.rec_button.scale = 2

        self.timer_text = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Countdown 9.png"),
            self.target_resolution.x//2-13, self.target_resolution.y//2+10,
            batch=self.batch,
            group=OrderedGroup(Layers.MAIN_UI)
        )
        self.timer_text.scale = 2
        self.timer_text.visible = False

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

        self.saving_text = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Saving.png"),
            self.target_resolution.x//2 - 43,
            self.target_resolution.y-24,
            batch=self.batch,
            group=OrderedGroup(Layers.BUTTONS)
        )
        self.saving_text.scale = 2
        self.saving_text.visible = self.saving

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

        self.storage_message_text = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/No Storage Found.png"),
            self.target_resolution.x//2 - 128,
            self.target_resolution.y-24,
            batch=self.batch,
            group=OrderedGroup(Layers.BUTTONS)
        )
        self.storage_message_text.scale = 2
        self.storage_message_text.visible = self.storage_message

    def init_about_window(self):
        self.about_window = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/About.png"),
            0, 0,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW)
        )
        self.about_window.scale = 2
        self.about_window.visible = self.about

        self.about_quit_sprite = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Quit.png"),
            20, self.target_resolution.y-58,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW_UI)
        )
        self.about_quit_sprite.scale = 2
        self.about_quit_sprite.visible = self.about

    def init_settings_window(self):
        self.settings_window = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Settings.png"),
            0, 0,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW)
        )
        self.settings_window.scale = 2
        self.settings_window.visible = self.settings

        self.settings_quit_sprite = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Quit.png"),
            20, self.target_resolution.y-58,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW_UI)
        )
        self.settings_quit_sprite.scale = 2
        self.settings_quit_sprite.visible = self.settings

        self.settings_grid_toggle = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Off.png"),
            76, self.target_resolution.y-92,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW_UI)
        )
        self.settings_grid_toggle.scale = 2
        self.settings_grid_toggle.visible = self.settings

        self.settings_centre_toggle = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Off.png"),
            164, self.target_resolution.y-116,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW_UI)
        )
        self.settings_centre_toggle.scale = 2
        self.settings_centre_toggle.visible = self.settings

        self.settings_timer_toggle = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Off.png"),
            148, self.target_resolution.y-140,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW_UI)
        )
        self.settings_timer_toggle.scale = 2
        self.settings_timer_toggle.visible = self.settings

        self.settings_monochrome_toggle = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Off.png"),
            148, self.target_resolution.y-164,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW_UI)
        )
        self.settings_monochrome_toggle.scale = 2
        self.settings_monochrome_toggle.visible = self.settings

        self.settings_fps_more = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/More.png"),
            214, self.target_resolution.y-186,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW_UI)
        )
        self.settings_fps_more.scale = 2
        self.settings_fps_more.visible = self.settings

        self.settings_fps_less = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Less.png"),
            230, self.target_resolution.y-186,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW_UI)
        )
        self.settings_fps_less.scale = 2
        self.settings_fps_less.visible = self.settings

        self.settings_fps_text = pyglet.sprite.Sprite(
            pyglet.resource.image(f"assets/{self.fps:02}.png"),
            246, self.target_resolution.y-188,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW_UI)
        )
        self.settings_fps_text.scale = 2
        self.settings_fps_text.visible = self.settings

        self.settings_mute_toggle = pyglet.sprite.Sprite(
            pyglet.resource.image("assets/Off.png"),
            76, self.target_resolution.y-212,
            batch=self.batch,
            group=OrderedGroup(Layers.WINDOW_UI)
        )
        self.settings_mute_toggle.scale = 2
        self.settings_mute_toggle.visible = self.settings

    @property
    def grid(self) -> bool:
        return self._grid

    @grid.setter
    def grid(self, value: bool):
        self._grid = value
        self.grid_sprite.visible = value
        if value:
            image = pyglet.resource.image("assets/On.png")
        else:
            image = pyglet.resource.image("assets/Off.png")
        self.settings_grid_toggle.image = image

    @property
    def crosshair(self) -> bool:
        return self._crosshair

    @crosshair.setter
    def crosshair(self, value: bool):
        self._crosshair = value
        self.crosshair_sprite.visible = value
        if value:
            image = pyglet.resource.image("assets/On.png")
        else:
            image = pyglet.resource.image("assets/Off.png")
        self.settings_centre_toggle.image = image

    @property
    def mute(self) -> bool:
        return self._mute

    @mute.setter
    def mute(self, value: bool):
        self._mute = value
        if value:
            image = pyglet.resource.image("assets/On.png")
        else:
            image = pyglet.resource.image("assets/Off.png")
        self.settings_mute_toggle.image = image

    @property
    def timer(self) -> bool:
        return self._timer

    @timer.setter
    def timer(self, value: bool):
        self._timer = value
        if value:
            image = pyglet.resource.image("assets/On.png")
        else:
            image = pyglet.resource.image("assets/Off.png")
        self.settings_timer_toggle.image = image

    @property
    def monochrome(self) -> bool:
        return self._monochrome

    @monochrome.setter
    def monochrome(self, value: bool):
        self._monochrome = value
        if value:
            image = pyglet.resource.image("assets/On.png")
        else:
            image = pyglet.resource.image("assets/Off.png")
        self.settings_monochrome_toggle.image = image

    @property
    def recording(self) -> bool:
        return self._recording

    @recording.setter
    def recording(self, value: bool):
        self._recording = value
        if value:
            image = pyglet.resource.image("assets/Rec Recording.png")
        else:
            image = pyglet.resource.image("assets/Rec Idle.png")
        self.rec_button.image = image

    @property
    def about(self) -> bool:
        return self._about

    @about.setter
    def about(self, value: bool):
        if self.settings:
            self.settings = False
        self._about = value
        self.about_window.visible = value
        self.about_quit_sprite.visible = value

    @property
    def settings(self) -> bool:
        return self._settings

    @settings.setter
    def settings(self, value: bool):
        if self.about:
            self.about = False
        self._settings = value
        self.settings_window.visible = value
        self.settings_quit_sprite.visible = value
        self.settings_grid_toggle.visible = value
        self.settings_centre_toggle.visible = value
        self.settings_timer_toggle.visible = value
        self.settings_monochrome_toggle.visible = value
        self.settings_fps_more.visible = value
        self.settings_fps_less.visible = value
        self.settings_fps_text.visible = value
        self.settings_mute_toggle.visible = value

    @property
    def fps(self) -> int:
        return self._fps

    @fps.setter
    def fps(self, value: int):
        self._fps = value
        image = pyglet.resource.image(f"assets/{value:02}.png")
        self.fps_display.image = image
        self.settings_fps_text.image = image

    @property
    def saving(self) -> bool:
        return self._saving

    @saving.setter
    def saving(self, value: bool):
        self._saving = value
        self.saving_text.visible = value

    @property
    def storage_message(self) -> bool:
        return self._storage_message

    @storage_message.setter
    def storage_message(self, value: bool):
        self._storage_message = value
        self.storage_message_text.visible = value

    def start_timer(self):
        self.timer_running = True
        self.update_timer(0, 10)

    def update_timer(self, dt: float, time_remaining: int):
        if time_remaining > 0:
            image = f"assets/Countdown {time_remaining}.png"
            self.timer_text.image = pyglet.resource.image(image)
            self.timer_text.visible = True

            if time_remaining >= 4:
                path = "assets/10-4.ogg"
            else:
                path = "assets/3-1.ogg"

            pyglet.clock.schedule_once(self.update_timer, 1, time_remaining-1)
        else:
            path = "assets/0.ogg"
            self.abort_timer()
            self.dispatch_event("on_timer_complete")

        self.player.queue(pyglet.resource.media(path))
        self.player.play()

    def abort_timer(self):
        self.timer_running = False
        self.timer_text.visible = False
        pyglet.clock.unschedule(self.update_timer)

    def check_click(self, x, y, item: pyglet.sprite.Sprite):
        return (
            item.x < x < item.x + item.width
            and item.y < y < item.y + item.height
            and item.visible
        )

    def mouse_released(self, x, y):
        if self.check_click(x, y, self.rec_button):
            self.dispatch_event("on_rec_pressed")
        elif self.check_click(x, y, self.settings_quit_sprite):
            self.settings = False
        elif self.check_click(x, y, self.settings_grid_toggle):
            self.grid = not self.grid
        elif self.check_click(x, y, self.settings_centre_toggle):
            self.crosshair = not self.crosshair
        elif self.check_click(x, y, self.settings_timer_toggle):
            self.timer = not self.timer
        elif self.check_click(x, y, self.settings_monochrome_toggle):
            self.monochrome = not self.monochrome
            self.dispatch_event("on_monochrome_change", self.monochrome)
        elif self.check_click(x, y, self.settings_fps_more):
            self.dispatch_event("on_fps_change", self.fps + 1)
        elif self.check_click(x, y, self.settings_fps_less):
            self.dispatch_event("on_fps_change", self.fps - 1)
        elif self.check_click(x, y, self.settings_mute_toggle):
            self.mute = not self.mute
        elif self.check_click(x, y, self.about_quit_sprite):
            self.about = False
        elif self.check_click(x, y, self.settings_quit_sprite):
            self.settings = False
        elif self.check_click(x, y, self.settings_button):
            self.settings = not self.settings
        elif self.check_click(x, y, self.about_button):
            self.about = not self.about


Interface.register_event_type("on_fps_change")
Interface.register_event_type("on_rec_pressed")
Interface.register_event_type("on_timer_complete")
Interface.register_event_type("on_monochrome_change")
