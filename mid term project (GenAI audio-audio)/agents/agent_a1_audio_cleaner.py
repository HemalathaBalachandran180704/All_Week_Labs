import os
import librosa
import soundfile as sf
import noisereduce as nr

class AgentA1AudioCleaner:
    def __init__(self):
        pass

    def process_audio(self, input_path, output_path="cleaned_audio.wav"):
        """Denoise and normalize uploaded audio"""
        audio, sr = librosa.load(input_path, sr=None)
        reduced_noise = nr.reduce_noise(y=audio, sr=sr)
        sf.write(output_path, reduced_noise, sr)
        return output_path
