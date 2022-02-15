import pyaudio
import pyglet

import os
import wave


class AudioManager:
    CHUNK_SIZE = 4096  # Record in chunks of 4096 samples
    SAMPLE_FORMAT = pyaudio.paInt16  # 16 bits per sample
    CHANNELS = 2
    FS = 44100  # Record at 44100 samples per second

    recording = False
    frames = []

    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()  # Create an interface to PortAudio

        pyglet.clock.schedule(self.frame)

    def start_recording(self):
        if self.recording:
            print("Already recording!")
            return

        self.stream = self.pyaudio.open(
            format=self.SAMPLE_FORMAT,
            channels=self.CHANNELS,
            rate=self.FS,
            input=True
        )
        self.recording = True
        self.frames = []

    def frame(self, dt: float):
        if self.recording:
            data = self.stream.read(int(dt*self.FS)+1)
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
