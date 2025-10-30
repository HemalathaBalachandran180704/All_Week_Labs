import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

print(torch.cuda.is_available())     
print(torch.cuda.get_device_name(0))   

device = "cuda:0" 

REFERENCE_AUDIO = "Consistency over Obsession.wav"
OUTPUT_AUDIO = "cloned_speech.wav"

SCRIPT = "You know, I am quite aware that I have proved myself over the last decade or so throughout my International and Domestic carrer but I am definitely not planning on retiring and will continue to dominate in the I P L and hopefully lift that sixth trophy for Chennai Super Kings next year"

# Load TTS model
tts_model = ChatterboxTTS.from_pretrained(device)

# Generate audio
wav = tts_model.generate(
    text=SCRIPT,
    audio_prompt_path=REFERENCE_AUDIO
)



# --- Ensure wav is 2D (channels, samples) for torchaudio ---
if isinstance(wav, torch.Tensor):
    # Remove batch dimension if exists
    if wav.ndim == 3:
        wav = wav.squeeze(0)   # (1, samples)
    if wav.ndim == 1:
        wav = wav.unsqueeze(0) # (1, samples)
    # wav is now guaranteed to be 2D



# Save audio
ta.save(OUTPUT_AUDIO, wav, tts_model.sr)

print(f"Done! Audio saved at {OUTPUT_AUDIO}")
