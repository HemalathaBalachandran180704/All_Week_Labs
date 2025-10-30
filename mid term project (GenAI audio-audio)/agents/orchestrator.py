from agents.agent_a1_audio_cleaner import AgentA1AudioCleaner
from agents.agent_a2_script_processor import AgentA2ScriptProcessor
from agents.agent_a3_voice_cloner import AgentA3VoiceCloner

class Orchestrator:
    def __init__(self, gemini_api_key):
        self.a1 = AgentA1AudioCleaner()
        self.a2 = AgentA2ScriptProcessor(gemini_api_key)
        self.a3 = AgentA3VoiceCloner()

    def run_pipeline(self, raw_audio, youtube_url):
        cleaned_audio = self.a1.process_audio(raw_audio)
        polished_script = self.a2.process_youtube(youtube_url)
        cloned_audio = self.a3.clone_voice(cleaned_audio, polished_script)
        return {
            "cleaned_audio": cleaned_audio,
            "script": polished_script,
            "final_audio": cloned_audio
        }
