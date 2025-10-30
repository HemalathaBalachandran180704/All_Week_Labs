import os
import subprocess
import torch
import librosa
import soundfile as sf
from transformers import pipeline
from pathlib import Path

# -----------------------------
# 1. Audio loading & saving
# -----------------------------
def load_audio(file_path, sr=16000):
    audio, _ = librosa.load(file_path, sr=sr)
    return audio, sr

def save_audio(file_path, audio, sr=16000):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    sf.write(file_path, audio, sr)
    return file_path

# -----------------------------
# 2. Whisper transcription
# -----------------------------
def transcribe_audio(audio_path):
    print(f"🔍 Transcribing {audio_path} ...")
    whisper = pipeline("automatic-speech-recognition", model="openai/whisper-small")
    result = whisper(audio_path)
    text = result["text"]
    print("✅ Transcription complete.")
    return text

# -----------------------------
# 3. Text polishing
# -----------------------------
def polish_text(text):
    # Simple cleanup — later can integrate Gemini here
    cleaned = text.strip().replace("  ", " ")
    return cleaned

# -----------------------------
# 4. Voice synthesis (TTS)
# -----------------------------
def synthesize_speech(text, output_path, voice_model="suno/bark-small"):
    print(f"🗣️ Generating speech for: {text[:60]}...")
    tts = pipeline("text-to-speech", model=voice_model)
    speech = tts(text)
    save_audio(output_path, speech["audio"], sr=speech["sampling_rate"])
    print(f"✅ Saved synthesized audio to {output_path}")
    return output_path

# -----------------------------
# 5. Clone voice placeholder (later replaced with real VC)
# -----------------------------
def clone_voice(reference_audio_path, target_text, output_path):
    print(f"🎙️ Cloning voice using {reference_audio_path} ...")
    # Temporarily just TTS; later integrate with real voice cloning
    synthesize_speech(target_text, output_path)
    return output_path
