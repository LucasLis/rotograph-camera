import pyaudio
import pyglet

import os
import wave


class AudioManager:
    SAMPLE_FORMAT = pyaudio.paInt16  # 16 bits per sample
    CHANNELS = 2
    FS = 44100  # Record at 44100 samples per second
    FRAME_TIME = 1/30

    recording = False
    frames = []

    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()  # Create an interface to PortAudio

    def start_recording(self):
        if self.recording:
            print("Already recording!")
            return

        self.stream = self.pyaudio.open(
            frames_per_buffer=int(self.FS*self.FRAME_TIME)*2,
            format=self.SAMPLE_FORMAT,
            channels=self.CHANNELS,
            rate=self.FS,
            input=True
        )
        self.recording = True
        self.frames = []

        pyglet.clock.schedule_interval(self.frame, self.FRAME_TIME)

    def frame(self, dt: float):
        if self.recording:
            data = self.stream.read(self.stream.get_read_available())
            self.frames.append(data)

    def stop_recording(self):
        if not self.recording:
            print("Not currently recording.")
            return
        self.stream.stop_stream()
        self.recording = False

    def save(self, output_path: str):
        if len(self.frames) == 0:
            print("No audio to save!")
            return

        # Save the recorded data as a WAV file
        path = os.path.join(output_path, "audio.wav")
        wf = wave.open(path, "wb")
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.pyaudio.get_sample_size(self.SAMPLE_FORMAT))
        wf.setframerate(self.FS)
        wf.writeframes(b"".join(self.frames))
        wf.close()

        self.frames = []

    def __del__(self):
        self.stream.close()
        self.pyaudio.terminate()
