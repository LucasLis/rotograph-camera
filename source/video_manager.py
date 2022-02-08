import cv2
import numpy as np
from PIL import Image
import pyglet

from typing import Tuple, Optional
import os


class VideoManager(pyglet.event.EventDispatcher):
    MAX_FPS = 24

    image: pyglet.image.ImageData

    frames = []
    frame_count = -1
    recording = False

    monochrome = False

    _fps: int

    def __init__(self, fps: int, resolution: Tuple[int, int], capture_id=0):
        self.vc = cv2.VideoCapture(capture_id)

        self.init_image()

        self.resolution = resolution
        self.fps = fps

    def init_image(self):
        frame = self.read_frame()
        if frame is not None:
            size = self.get_size(frame)
            data = self.get_data(frame)
            self.image = pyglet.image.ImageData(
                size[0],
                size[1],
                "RGB",
                data
            )
            self.image.anchor_x = self.image.width // 2
            self.image.anchor_y = self.image.height // 2

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

    def get_size(self, frame: np.ndarray) -> Tuple[int, int]:
        shape = frame.shape
        return (shape[1], shape[0])

    def get_data(self, frame: np.ndarray) -> str:
        return frame.flatten().tostring()

    def crop_frame(self, frame: np.ndarray) -> Image:
        pil_image = Image.fromarray(frame[::-1, :, :])
        width, height = pil_image.size

        left = (width - self.resolution[0])//2
        top = (height - self.resolution[1])//2
        right = (width + self.resolution[0])//2
        bottom = (height + self.resolution[1])//2

        # Crop the center of the image
        return pil_image.crop((left, top, right, bottom))

    def read_frame(self) -> None | np.ndarray:
        if not self.vc.isOpened():
            print("Failed to read frame, video capture is not open.")
            return

        rval, frame = self.vc.read()
        if not rval:
            print("Failed to read frame, rval was False.")
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Saturation
        if self.monochrome:
            frame[:, :, 1] = 0
            blacks = 32
            whites = 207
            frame[:, :, 2] = blacks + frame[:, :, 2]/255 * (whites - blacks)
        else:
            frame[:, :, 1] = frame[:, :, 1] * 0.8
            blacks = 0
            whites = 207
            frame[:, :, 2] = blacks + frame[:, :, 2]/255 * (whites - blacks)
        # Value
        return cv2.cvtColor(frame, cv2.COLOR_HSV2RGB)[::-1, :, :]

    def frame(self, dt: float = None):
        frame = self.read_frame()
        if frame is not None:
            data = self.get_data(frame)
            self.image.set_data("RGB", self.image.pitch, data)
            self.dispatch_event("on_frame_ready")

            if self.recording:
                self.frames.append(frame)

    def save(self, output_path: str, datestring: Optional[str] = None):
        if self.fps == 0:
            frame = self.read_frame()
            path = os.path.join(output_path, "frame-" + datestring + ".jpg")
            self.crop_frame(frame).save(path)
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
        self.vc.release()


VideoManager.register_event_type("on_frame_ready")
