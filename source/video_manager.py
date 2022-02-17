import pygame
from pygame import camera
from pygame import image
from PIL import Image, ImageEnhance
import pyglet

from typing import Tuple, Optional, List
from threading import Thread
import os


class VideoManager(pyglet.event.EventDispatcher):
    MAX_FPS = 24
    FORMAT = "RGB"

    camera_available = False
    camera = None

    image: pyglet.image.ImageData

    frames: List[Image.Image] = []
    frame_count = -1
    recording = False

    monochrome = False

    _fps: int

    def __init__(self, fps: int, resolution: Tuple[int, int], capture_id=0):
        camera.init()

        self.resolution = resolution
        self.fps = fps

        self.capture_id = capture_id

        pyglet.clock.schedule_interval_soft(self.check_camera, 1)

    def check_camera(self, dt: float):
        if self.camera_available:
            return

        if self.camera is None:
            cameras = camera.list_cameras()
            if len(cameras) == 0:
                print("No cameras found.")
                self.dispatch_event("on_camera_unavailable")
                return
            self.camera = camera.Camera(
                cameras[self.capture_id],
                self.resolution
            )

        self.surface = pygame.Surface(self.camera.get_size())
        try:
            self.camera.start()
            self.camera_available = True
        except SystemError as e:
            print("Camera unavailable:", e)
            self.dispatch_event("on_camera_unavailable")
            return

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

    def crop_frame(self, image: Image.Image) -> Image.Image:
        width, height = image.size

        left = (width - self.resolution[0])//2
        top = (height - self.resolution[1])//2
        right = (width + self.resolution[0])//2
        bottom = (height + self.resolution[1])//2

        # Crop the center of the image
        return image.crop((left, top, right, bottom))

    def get_image(self) -> Optional[Image.Image]:
        def get_image():
            self.camera_available = False
            self.surface = self.camera.get_image()
            self.camera_available = True

        thread = Thread(target=get_image, daemon=True)
        thread.start()
        thread.join(1)

        if not self.camera_available:
            self.dispatch_event("on_camera_unavailable")
            print("Frame timed out.")
            return

        data = image.tostring(self.surface, self.FORMAT)
        pil_image = Image.frombytes("RGB", self.surface.get_size(), data)
        # Saturation
        pil_image = ImageEnhance.Color(pil_image)
        pil_image = pil_image.enhance(0 if self.monochrome else 0.8)
        # Contrast
        pil_image = ImageEnhance.Contrast(pil_image).enhance(0.8)
        return pil_image

    def frame(self, dt: float = None):
        if self.camera_available:
            pil_image = self.get_image()
            if pil_image is None:
                return

            data = pil_image.tobytes()

            self.image = pyglet.image.ImageData(
                *self.camera.get_size(),
                self.FORMAT,
                data,
                pitch=-pil_image.width*len(self.FORMAT)
            )
            self.image.anchor_x = self.image.width // 2
            self.image.anchor_y = self.image.height // 2
            self.dispatch_event("on_frame_ready")

            if self.recording:
                self.frames.append(self.crop_frame(pil_image))

    def save(self, output_path: str, datestring: Optional[str] = None):
        if self.fps == 0:
            pil_image = self.get_image()
            if pil_image is None:
                return

            path = os.path.join(output_path, "frame-" + datestring + ".jpg")
            self.crop_frame(pil_image).save(path)
            return

        if len(self.frames) == 0:
            print("No frames to save.")
            return

        path = os.path.join(output_path, "frames.gif")
        self.frames[0].save(
            path,
            save_all=True,
            append_images=self.frames[1:],
            optimize=True,
            interlace=False,
            duration=1000/self.fps,
        )
        self.frames = []

    def __del__(self):
        self.camera.stop()


VideoManager.register_event_type("on_frame_ready")
VideoManager.register_event_type("on_camera_unavailable")
