import cv2
import numpy as np
from PIL import Image
import pyglet

from typing import Tuple


class VideoManager(pyglet.event.EventDispatcher):
    MAX_FPS = 24

    image: pyglet.image.ImageData

    frames = []
    frame_count = -1
    recording = False

    _fps: int

    def __init__(self, fps: int, resolution: Tuple[int, int], capture_id=0):
        self.vc = cv2.VideoCapture(capture_id)

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
            self.image.get_texture()
            self.image.anchor_x = self.image.width // 2
            self.image.anchor_y = self.image.height // 2

        self.resolution = resolution
        self.fps = fps

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

        pyglet.clock.unschedule(self.frame)

        preview_fps = new_fps if new_fps > 0 else self.MAX_FPS
        pyglet.clock.schedule_interval(self.frame, 1/preview_fps)
        self._fps = new_fps

    def start_recording(self, time: int):
        if self.recording:
            print("Already recording.")
            return

        self.recording = True
        self.frames = []
        self.frame_count = time * self.fps

    def get_size(self, frame: np.ndarray) -> Tuple[int, int]:
        shape = frame.shape
        return (shape[1], shape[0])

    def get_data(self, frame: np.ndarray) -> str:
        return frame.flatten().tostring()

    def crop_frame(self, frame: np.ndarray) -> Image:
        pil_image = Image.fromarray(frame)
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

        return frame[::-1, :, ::-1]  # Flip y axis and flip colours, BGR -> RGB

    def frame(self, dt: float):
        frame = self.read_frame()
        if frame is not None:
            data = self.get_data(frame)
            self.image.set_data("RGB", self.image.pitch, data)
            self.dispatch_event("on_frame_ready")

            if self.frame_count > 0:
                self.frames.append(frame)
                self.frame_count -= 1
            elif self.frame_count == 0:
                if self.fps == 0:
                    self.frames.append(frame)

                self.dispatch_event("on_recording_finished")
                self.recording = False

    def save(self):
        if len(self.frames) == 0:
            print("No frames to save.")
            return

        self.frames = list(map(
            lambda frame: self.crop_frame(frame),
            self.frames
        ))

        if self.fps == 0:
            self.frames[0].save("frame.jpg")
        else:
            self.frames[0].save(
                "frames.gif",
                save_all=True,
                append_images=self.frames[1:],
                optimize=True,
                interlace=False,
                duration=1000/self.fps,
            )

    def __del__(self):
        self.vc.release()


VideoManager.register_event_type("on_recording_finished")
VideoManager.register_event_type("on_frame_ready")
