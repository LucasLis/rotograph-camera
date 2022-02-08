from .audio_manager import AudioManager
from .video_manager import VideoManager
from .fixed_resolution import FixedResolution
from .interface import Interface, Layers

import pyglet
from pyglet.window import key
from pyglet.graphics import OrderedGroup
from pyglet.math import Vec2

import datetime
import json
from json.decoder import JSONDecodeError
import os
from typing import Optional


pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST
pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST


class Application:
    TARGET_RESOLUTION = Vec2(640, 360)
    CONFIG_FOLDER = os.path.join(os.environ["HOME"], ".config", "rotograph")
    CONFIG_FILE = os.path.join(CONFIG_FOLDER, "config.json")
    EMPTY_IMAGE = pyglet.image.ImageData(1, 1, "RGBA", b"\x00\x00\x00\x00")

    storage_device_available = property(
        lambda self: self.get_mount_path() != ""
    )

    def __init__(self):
        if not os.path.exists(self.CONFIG_FOLDER):
            os.makedirs(self.CONFIG_FOLDER)

        try:
            with open(self.CONFIG_FILE, "r") as f:
                self.config = json.load(f)
        except (FileNotFoundError, JSONDecodeError):
            self.config = {}

        if "device-uuid" not in self.config:
            print("No storage device found in config.")
            self.select_storage_device()

        if "output-path" not in self.config:
            print("No output path found in config.")
            self.choose_output_path()

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
            self.EMPTY_IMAGE,
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
        self.check_storage()

        pyglet.clock.schedule_interval_soft(self.check_storage, 1)

    def check_storage(self, dt: float = None):
        self.interface.storage_message = not self.storage_device_available

    def get_mount_path(self, uuid: Optional[str] = None) -> str:
        if uuid is None:
            uuid = self.config["device-uuid"]
        with os.popen(f"findmnt -rn -S UUID={uuid} -o TARGET") as f:
            return f.read().strip().replace("\\x20", " ")

    def choose_output_path(self):
        while True:
            print("\nPlease enter the path to save content to within the selected storage device.")  # noqa: E501
            print("Example: Camera/Rotograph/")
            print("You may leave this blank to just store directly within the storage device.")  # noqa: E501
            path = input("Output path: ").strip()

            choice = "N/A" if path == "" else path
            print(f"You have selected '{choice}' as the storage path.")
            confirmation = ""
            while confirmation not in ["y", "n"]:
                confirmation = input("Is this correct? (y/n): ")
                confirmation = confirmation.strip().lower()

            if confirmation == "y":
                self.config["output-path"] = path
                with open(self.CONFIG_FILE, "w") as f:
                    json.dump(self.config, f)
                break
        print("\n")

    def get_storage_devices(self):
        devices = []
        with open("/proc/mounts", "r") as f:
            mounts = f.readlines()

        for info in mounts:
            if info.startswith("/dev/sd"):
                info = [chunk.strip() for chunk in info.split()]
                with os.popen(f"lsblk {info[0]} -no UUID") as p:
                    uuid = p.read().strip()
                path = self.get_mount_path(uuid)
                devices.append((info[0], path, uuid))

        return devices

    def select_storage_device(self):
        print("\nPlease select a storage device to use:")
        devices = self.get_storage_devices()

        while True:
            for i, device in enumerate(devices):
                print(f"{i+1}: {device[1]}\t({device[0]})")

            choice = 0
            while choice <= 0 or choice > len(devices):
                try:
                    choice = int(input(f"Please choose (1-{len(devices)}): "))
                except ValueError:
                    pass

            choice = devices[choice-1]
            print(f"You have selected {choice[0]} (mounted at '{choice[1]}')")
            confirmation = ""
            while confirmation not in ["y", "n"]:
                confirmation = input("Is this correct? (y/n): ")
                confirmation = confirmation.strip().lower()

            if confirmation == "y":
                self.config["device-uuid"] = choice[2]
                with open(self.CONFIG_FILE, "w") as f:
                    json.dump(self.config, f)
                break
        print("\n")

    def save(self, dt: float = None):
        mount_path = self.get_mount_path()

        outdir = os.path.join(
            mount_path,
            self.config["output-path"]
        )

        datestring = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S %f")
        if self.video_manager.fps != 0:
            path = os.path.join(outdir, "Videos", datestring)
            if not os.path.exists(path):
                os.makedirs(path)
            self.audio_manager.save(path)
            self.video_manager.save(path)
        else:
            path = os.path.join(outdir, "Images")
            if not os.path.exists(path):
                os.makedirs(path)
            self.video_manager.save(path, datestring)
        self.interface.saving = False

    def start_recording(self):
        if not self.storage_device_available:
            print("No storage device found.")
            return

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

        if not self.storage_device_available:
            print("No storage device found.")
            return

        self.interface.saving = True
        pyglet.clock.schedule_once(self.save, 0.2)

    def on_mouse_release(self, x, y, button, modifiers):
        x -= self.viewport._viewport[0]
        y -= self.viewport._viewport[1]
        x *= self.TARGET_RESOLUTION.x / (self.viewport._viewport[3])
        y *= self.TARGET_RESOLUTION.y / (self.viewport._viewport[4])
        self.interface.mouse_released(x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.F11:
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
        self.interface.camera_message = False

    def on_frame_failed(self):
        self.preview_sprite.image = self.EMPTY_IMAGE
        self.interface.camera_message = True

    def run(self):
        pyglet.app.run()
