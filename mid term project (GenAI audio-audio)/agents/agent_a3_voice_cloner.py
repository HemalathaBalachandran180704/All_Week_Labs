from chatterbox.tts import ChatterboxTTS
import torchaudio as ta
import torch

class AgentA3VoiceCloner:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.tts = ChatterboxTTS.from_pretrained(device)

    def clone_voice(self, cleaned_audio, text, output_path="cloned_final.wav"):
        wav = self.tts.generate(text=text, audio_prompt_path=cleaned_audio)
        if isinstance(wav, torch.Tensor):
            if wav.ndim == 3: wav = wav.squeeze(0)
            if wav.ndim == 1: wav = wav.unsqueeze(0)
        ta.save(output_path, wav, self.tts.sr)
        return output_path
