import cv2
import numpy as np
from PIL import Image
import pyglet

from typing import Tuple


class VideoManager(pyglet.event.EventDispatcher):
    TARGET_SIZE = TARGET_WIDTH, TARGET_HEIGHT = (640, 360)
    MAX_FPS = 24
    FPS = 5

    image: pyglet.image.ImageData

    frames = []
    frame_count = 0
    recording = False

    def __init__(self, capture_id=0):
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

    def start_recording(self, time: int):
        self.recording = True
        self.frames = []
        self.frame_count = time * self.FPS

    def get_size(self, frame: np.ndarray) -> Tuple[int, int]:
        shape = frame.shape
        return (shape[1], shape[0])

    def get_data(self, frame: np.ndarray) -> str:
        return frame.flatten().tostring()

    def crop_frame(self, frame: np.ndarray) -> Image:
        pil_image = Image.fromarray(frame)
        width, height = pil_image.size

        left = (width - self.TARGET_WIDTH)//2
        top = (height - self.TARGET_HEIGHT)//2
        right = (width + self.TARGET_WIDTH)//2
        bottom = (height + self.TARGET_HEIGHT)//2

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

    def update(self):
        frame = self.read_frame()
        if frame is not None:
            data = self.get_data(frame)
            self.image.set_data("RGB", self.image.pitch, data)

            if self.recording:
                if self.frame_count > 0:
                    self.frames.append(self.crop_frame(frame))
                    self.frame_count -= 1
                else:
                    if self.FPS == 0:
                        self.frames.append(self.crop_frame(frame))

                    self.dispatch_event("on_recording_finished")
                    self.recording = False

    def save(self):
        if self.FPS == 0:
            self.frames[0].save("frame.jpg")
        else:
            self.frames[0].save(
                "frames.gif",
                save_all=True,
                append_images=self.frames[1:],
                optimize=True,
                interlace=False,
                duration=1000/self.FPS,
            )

    def __del__(self):
        self.vc.release()


VideoManager.register_event_type("on_recording_finished")
