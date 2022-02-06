import pyaudio
import pyglet
import wave


class AudioManager:
    CHUNK_SIZE = 4096  # Record in chunks of 512 samples
    SAMPLE_FORMAT = pyaudio.paInt16  # 16 bits per sample
    CHANNELS = 2
    FS = 44100  # Record at 44100 samples per second
    FILENAME = "audio.wav"

    recording = False
    frames = []

    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()  # Create an interface to PortAudio

        pyglet.clock.schedule_interval(self.frame, self.CHUNK_SIZE/self.FS)

    def start_recording(self):
        if self.recording:
            print("Already recording!")
            return

        self.stream = self.pyaudio.open(
            format=self.SAMPLE_FORMAT,
            channels=self.CHANNELS,
            rate=self.FS,
            frames_per_buffer=self.CHUNK_SIZE,
            input=True
        )
        self.recording = True
        self.frames = []

    def frame(self, _=None):
        if self.recording:
            data = self.stream.read(self.CHUNK_SIZE)
            self.frames.append(data)

    def stop_recording(self):
        if not self.recording:
            print("Not currently recording.")
            return
        self.frame()
        self.recording = False

        # Stop and close the stream
        self.stream.stop_stream()
        self.stream.close()

    def save(self):
        if len(self.frames) == 0:
            print("No audio to save!")
            return

        # Save the recorded data as a WAV file
        wf = wave.open(self.FILENAME, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.pyaudio.get_sample_size(self.SAMPLE_FORMAT))
        wf.setframerate(self.FS)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def __del__(self):
        self.pyaudio.terminate()
