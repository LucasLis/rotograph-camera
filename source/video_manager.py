import pygame
from pygame import camera
from pygame import image
from PIL import Image
import pyglet

from typing import Tuple, Optional, List
import os


class VideoManager(pyglet.event.EventDispatcher):
    MAX_FPS = 24
    FORMAT = "RGB"

    camera_available = False

    image: pyglet.image.ImageData

    frames: List[pygame.Surface] = []
    frame_count = -1
    recording = False

    monochrome = False

    _fps: int

    def __init__(self, fps: int, resolution: Tuple[int, int], capture_id=0):
        camera.init()

        self.resolution = resolution
        self.fps = fps

        self.capture_id = capture_id
        cameras = camera.list_cameras()
        self.camera = camera.Camera(
            cameras[capture_id],
            self.resolution
        )
        self.camera.start()

        self.surface = pygame.Surface(self.camera.get_size())

    @property
    def fps(self) -> int:
        return self._fps

    @fps.setter
    def fps(self, new_fps: int):
        if self.recording:
            print("Cannot change fps while recording.")
            return

        if new_fps > self.MAX_FPS:
            print("FPS is too high, setting to max.")
            new_fps = self.MAX_FPS
        if new_fps < 0:
            print("FPS is too low, setting to 0.")
            new_fps = 0

        pyglet.clock.unschedule(self.frame)

        preview_fps = new_fps if new_fps > 0 else self.MAX_FPS
        pyglet.clock.schedule_interval(self.frame, 1/preview_fps)
        self._fps = new_fps

    def start_recording(self):
        if self.recording:
            print("Already recording.")
            return

        self.recording = True
        self.frames = []

    def stop_recording(self):
        if not self.recording:
            print("Not recording.")
            return

        self.recording = False

    def crop_frame(self, surface: pygame.Surface) -> Image:
        data = image.tostring(surface, "RGB")
        pil_image = Image.frombytes("RGB", surface.get_size(), data)
        width, height = pil_image.size

        left = (width - self.resolution[0])//2
        top = (height - self.resolution[1])//2
        right = (width + self.resolution[0])//2
        bottom = (height + self.resolution[1])//2

        # Crop the center of the image
        return pil_image.crop((left, top, right, bottom))

    def frame(self, dt: float = None):
        self.surface = self.camera.get_image()
        data = image.tostring(self.surface, self.FORMAT, True)
        self.image = pyglet.image.ImageData(
            *self.camera.get_size(),
            self.FORMAT,
            data
        )
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2
        self.dispatch_event("on_frame_ready")

        if self.recording:
            self.frames.append(self.surface)

    def save(self, output_path: str, datestring: Optional[str] = None):
        if self.fps == 0:
            self.camera.get_image(self.surface)
            path = os.path.join(output_path, "frame-" + datestring + ".jpg")
            self.crop_frame(self.surface).save(path)
            return

        if len(self.frames) == 0:
            print("No frames to save.")
            return

        frames = list(map(
            lambda frame: self.crop_frame(frame),
            self.frames
        ))

        path = os.path.join(output_path, "frames.gif")
        frames[0].save(
            path,
            save_all=True,
            append_images=frames[1:],
            optimize=True,
            interlace=False,
            duration=1000/self.fps,
        )
        self.frames = []

    def __del__(self):
        self.camera.stop()


VideoManager.register_event_type("on_frame_ready")
VideoManager.register_event_type("on_frame_failed")
