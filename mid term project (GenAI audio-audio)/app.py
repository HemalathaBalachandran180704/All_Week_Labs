# import streamlit as st
# import os
# from pathlib import Path

# # -----------------------------
# # Ensure utils are imported correctly
# # -----------------------------
# from utils.audio_tools import load_audio, save_audio, denoise_audio
# from utils.filler_remover import remove_fillers
# from utils.polisher import polish_text      # Local polish function, no Gemini API call
# from utils.transcriber import get_transcript

# # -----------------------------
# # Agents
# # -----------------------------
# from agents.agent_a1_audio_cleaner import AgentA1AudioCleaner
# from agents.agent_a2_script_processor import AgentA2ScriptProcessor
# from agents.agent_a3_voice_cloner import AgentA3VoiceCloner

# # -----------------------------
# # Chatterbox device
# # -----------------------------
# import torch

# st.title("Voice Cloning TTS with Chatterbox")
# st.write("CUDA available:", torch.cuda.is_available())
# if torch.cuda.is_available():
#     st.write("Using GPU:", torch.cuda.get_device_name(0))

# # -----------------------------
# # Sidebar inputs
# # -----------------------------
# st.sidebar.header("Inputs")
# uploaded_audio = st.sidebar.file_uploader("Upload raw audio (WAV)", type=["wav"])
# youtube_video_id = st.sidebar.text_input(
#     "YouTube Video ID", 
#     placeholder="e.g., svxK22S8Swo"
# )
# # Gemini API key input is optional now since we're using local polish
# gemini_api_key = st.sidebar.text_input("Gemini API Key (not used)", value="")

# # -----------------------------
# # Initialize agents
# # -----------------------------
# agent_a1 = AgentA1AudioCleaner()
# agent_a2 = AgentA2ScriptProcessor()  # No API key needed for local polish
# agent_a3 = AgentA3VoiceCloner()

# # -----------------------------
# # Paths
# # -----------------------------
# BASE_DIR = Path(".")
# CLEAN_AUDIO_PATH = BASE_DIR / "cleaned_audio.wav"
# FINAL_AUDIO_PATH = BASE_DIR / "cloned_final.wav"

# # -----------------------------
# # Process pipeline
# # -----------------------------
# if st.button("Generate Cloned Voice"):

#     if not uploaded_audio or not youtube_video_id:
#         st.warning("Please upload audio and enter a YouTube video ID.")
#     else:
#         # 1️⃣ Save uploaded audio temporarily
#         raw_audio_path = BASE_DIR / uploaded_audio.name
#         with open(raw_audio_path, "wb") as f:
#             f.write(uploaded_audio.getbuffer())

#         st.info("Cleaning audio...")
#         cleaned_path = agent_a1.process_audio(raw_audio_path, CLEAN_AUDIO_PATH)
#         st.success("Audio cleaned!")
#         st.audio(cleaned_path, format="audio/wav")

#         # 2️⃣ Process YouTube script
#         st.info("Processing YouTube script...")
#         try:
#             raw_script = get_transcript(youtube_video_id)   # Use video ID
#         except Exception as e:
#             st.error(f"Transcript error: {e}")
#             raw_script = ""

#         if raw_script:
#             no_fillers = remove_fillers(raw_script)
#             polished_script = polish_text(no_fillers)  # Local polishing
#             st.text_area("Polished Script", polished_script, height=200)
#             st.success("Script processed!")

#             # 3️⃣ Clone voice
#             st.info("Generating cloned voice...")
#             final_audio_path = agent_a3.clone_voice(
#                 str(cleaned_path),
#                 polished_script,
#                 FINAL_AUDIO_PATH
#             )
#             st.success("Cloned voice generated!")
#             st.audio(final_audio_path, format="audio/wav")



import streamlit as st
import os
from pathlib import Path
import torch
import librosa
import soundfile as sf
import numpy as np
import google.generativeai as genai

# -----------------------------
# Utility imports
# -----------------------------
from utils.audio_tools import load_audio, save_audio, denoise_audio
from utils.filler_remover import remove_fillers
from utils.transcriber import get_transcript
from agents.agent_a1_audio_cleaner import AgentA1AudioCleaner
from agents.agent_a2_script_processor import AgentA2ScriptProcessor
from agents.agent_a3_voice_cloner import AgentA3VoiceCloner

# -----------------------------
# Gemini setup
# -----------------------------
GEMINI_API_KEY = "AIzaSyCa7Oxs0QgpxkFgQZtYX9iuS53-uPPiZaA"
genai.configure(api_key=GEMINI_API_KEY)

def polish_text_with_gemini(raw_text: str) -> str:
    """Polish transcript using Gemini."""
    if not raw_text or not raw_text.strip():
        return ""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = (
            f"Polish this raw transcript keeping it context-aware and natural, "
            f"without dropping any sentences. Output only the polished script, nothing else.\n\n{raw_text}"
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini failed: {e}]"

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🎙️ Voice Cloning TTS with Chatterbox")
st.write("**An AI-driven system to clean, process, and clone voices from custom audio + YouTube transcripts.**")

st.write("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    st.write("Using GPU:", torch.cuda.get_device_name(0))

# -----------------------------
# Sidebar inputs
# -----------------------------
st.sidebar.header("Inputs")
uploaded_audio = st.sidebar.file_uploader("Upload raw audio (WAV)", type=["wav"])
youtube_url = st.sidebar.text_input("YouTube video link", placeholder="https://www.youtube.com/watch?v=svxK22S8Swo")

# -----------------------------
# Audio tuning options BEFORE the process
# -----------------------------
st.subheader("🎚️ Audio Fine-Tuning Preferences (before generation)")

# Audio styles
audio_styles = {
    "None (original)": {"pitch": 0, "speed": 1.0, "gain": 0, "bass": 0, "treble": 0, "reverb": 0},
    "Deep Movie Star (stylized)": {"pitch": -4, "speed": 0.98, "gain": 1.5, "bass": 3.5, "treble": -2, "reverb": 0.28},
    "Pop Star Bright (stylized)": {"pitch": 3, "speed": 1.02, "gain": 0.5, "bass": -1, "treble": 4, "reverb": 0.32},
    "Older Deep Voice (stylized)": {"pitch": -6, "speed": 0.95, "gain": 2, "bass": 5, "treble": -3.5, "reverb": 0.18},
    "Cartoonish / Chipmunk (stylized)": {"pitch": 7.5, "speed": 1.4, "gain": 0, "bass": -6, "treble": 5, "reverb": 0.05},
}

mode = st.radio("Choose tuning method:", ["Preset Styles", "Manual Tuning"], key="tune_mode")

if mode == "Preset Styles":
    style_choice = st.selectbox("Select a preset style:", list(audio_styles.keys()), key="preset_style")
    st.session_state["tune_params"] = audio_styles[style_choice]
else:
    st.write("Adjust manually:")
    st.session_state["tune_params"] = {
        "pitch": st.slider("Pitch (semitones)", -12.0, 12.0, 0.0, key="pitch"),
        "speed": st.slider("Speed", 0.5, 1.5, 1.0, key="speed"),
        "gain": st.slider("Gain (dB)", -10.0, 10.0, 0.0, key="gain"),
        "bass": st.slider("Bass Boost", -10.0, 10.0, 0.0, key="bass"),
        "treble": st.slider("Treble Boost", -10.0, 10.0, 0.0, key="treble"),
        "reverb": st.slider("Reverb Intensity", 0.0, 1.0, 0.0, key="reverb"),
    }

# Show current selected tuning
st.info(f"🎵 Selected tuning: {st.session_state['tune_params']}")

# -----------------------------
# Initialize agents
# -----------------------------
agent_a1 = AgentA1AudioCleaner()
agent_a2 = AgentA2ScriptProcessor()
agent_a3 = AgentA3VoiceCloner()

BASE_DIR = Path(".")
CLEAN_AUDIO_PATH = BASE_DIR / "cleaned_audio.wav"
FINAL_AUDIO_PATH = BASE_DIR / "cloned_final.wav"

# -----------------------------
# Processing pipeline
# -----------------------------
if st.button("🚀 Generate Cloned Voice"):
    if not uploaded_audio or not youtube_url:
        st.warning("⚠️ Please upload an audio file and enter a valid YouTube link.")
    else:
        # 1️⃣ Audio Cleaning
        st.subheader("🧹 Step 1: Audio Cleaning (Agent A1)")
        raw_audio_path = BASE_DIR / uploaded_audio.name
        with open(raw_audio_path, "wb") as f:
            f.write(uploaded_audio.getbuffer())
        st.info("Cleaning audio using Agent A1...")
        cleaned_path = agent_a1.process_audio(raw_audio_path, CLEAN_AUDIO_PATH)
        st.audio(cleaned_path, format="audio/wav")
        st.success("✅ Audio cleaned successfully!")

        # 2️⃣ Apply Fine-Tuning (using saved params)
        st.subheader("🎧 Step 2: Applying Fine-Tuning")
        params = st.session_state["tune_params"]
        y, sr = librosa.load(cleaned_path, sr=None)
        if params["pitch"] != 0:
            y = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=params["pitch"])
        if params["speed"] != 1.0:
            y = librosa.effects.time_stretch(y, rate=params["speed"])
        y = y * (10 ** (params["gain"] / 20))
        tuned_path = BASE_DIR / "tuned_audio.wav"
        sf.write(tuned_path, y, sr)
        st.audio(tuned_path, format="audio/wav")
        st.success(f"✅ Applied tuning: {params}")

        # 3️⃣ Transcript
        st.subheader("🧾 Step 3: YouTube Transcript Processing (Agent A2)")
        try:
            st.info("Extracting transcript...")
            raw_transcript = get_transcript(youtube_url)
            st.text_area("🗒️ Raw Transcript", raw_transcript, height=200)
            no_fillers = remove_fillers(raw_transcript)
            st.info("Polishing with Gemini...")
            polished_script = polish_text_with_gemini(no_fillers)
            st.text_area("✨ Polished Transcript", polished_script, height=200)
        except Exception as e:
            st.error(f"Transcript error: {e}")
            polished_script = ""

        # 4️⃣ Voice Cloning
        if polished_script:
            st.subheader("🧬 Step 4: Voice Cloning (Agent A3)")
            st.info("Generating cloned voice...")
            final_audio_path = agent_a3.clone_voice(str(tuned_path), polished_script, FINAL_AUDIO_PATH)
            st.audio(final_audio_path, format="audio/wav")
            st.success("🎯 Cloned voice generation complete!")
