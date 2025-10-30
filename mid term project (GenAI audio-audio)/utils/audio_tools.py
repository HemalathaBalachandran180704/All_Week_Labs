import torch
import torchaudio
import torchaudio.transforms as T
import librosa
import numpy as np
import soundfile as sf

def load_audio(filepath, sr=22050):
    """Load audio and convert to mono."""
    y, _ = librosa.load(filepath, sr=sr, mono=True)
    return y, sr

def save_audio(y, sr, output_path):
    """Save numpy array as WAV."""
    sf.write(output_path, y, sr)

def denoise_audio(y, sr):
    """Simple noise reduction using spectral gating (basic)."""
    # Convert to tensor
    y_tensor = torch.tensor(y).unsqueeze(0)
    # Spectrogram
    spectrogram = T.Spectrogram()(y_tensor)
    # Median filter along time axis to reduce background noise
    median_spec = spectrogram.median(dim=-1, keepdim=True).values
    cleaned_spec = spectrogram - median_spec
    cleaned_spec = torch.clamp(cleaned_spec, min=0.0)
    # Inverse spectrogram
    istft = T.InverseSpectrogram()(cleaned_spec)
    return istft.squeeze().numpy()
