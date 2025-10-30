# # agents/orchestrator_run.py
# import sys, os
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# import argparse
# import time
# import logging
# from pathlib import Path

# # Import your existing agents (unchanged)
# from agents.agent_a1_audio_cleaner import AgentA1AudioCleaner
# from agents.agent_a2_script_processor import AgentA2ScriptProcessor
# from agents.agent_a3_voice_cloner import AgentA3VoiceCloner

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
# )

# def run_pipeline(
#     reference_audio_path: str,
#     youtube_video_id: str,
#     gemini_api_key: str | None = None,
#     output_dir: str = ".",
# ):
#     outdir = Path(output_dir)
#     outdir.mkdir(parents=True, exist_ok=True)

#     # Filenames
#     cleaned_path = outdir / "cleaned_audio.wav"
#     final_clone_path = outdir / "cloned_final.wav"

#     logging.info("Starting pipeline")
#     start = time.time()

#     # 1) Audio cleaning (A1)
#     logging.info("Initializing Agent A1 (Audio Cleaner)")
#     a1 = AgentA1AudioCleaner()
#     logging.info("Cleaning audio...")
#     cleaned = a1.process_audio(reference_audio_path, str(cleaned_path))
#     logging.info("Cleaned audio saved to: %s", cleaned)

#     # 2) Script processing (A2)
#     logging.info("Initializing Agent A2 (Script Processor)")
#     # if your AgentA2ScriptProcessor signature expects api key, pass it; otherwise use default constructor
#     try:
#         a2 = AgentA2ScriptProcessor(gemini_api_key)  # keep compatibility
#     except TypeError:
#         a2 = AgentA2ScriptProcessor()
#     logging.info("Fetching transcript and polishing (video id = %s)", youtube_video_id)
#     polished_script = a2.process_youtube(youtube_video_id)
#     logging.info("Polished script length: %d chars", len(polished_script))

#     # Save scripts for traceability
#     (outdir / "raw_transcript.txt").write_text(polished_script)  # option to also save raw text if desired

#     # 3) Voice cloning (A3)
#     logging.info("Initializing Agent A3 (Voice Cloner)")
#     a3 = AgentA3VoiceCloner()
#     logging.info("Generating cloned voice...")
#     cloned = a3.clone_voice(str(cleaned), polished_script, str(final_clone_path))
#     logging.info("Cloned audio written to: %s", cloned)

#     elapsed = time.time() - start
#     logging.info("Pipeline finished in %.1f seconds", elapsed)
#     return {
#         "cleaned_audio": str(cleaned),
#         "final_clone": str(final_clone_path),
#         "polished_script": polished_script,
#         "duration_s": elapsed,
#     }

# def parse_args():
#     p = argparse.ArgumentParser(description="Run Chatterbox pipeline headless")
#     p.add_argument("--audio", required=True, help="Path to reference audio (wav)")
#     p.add_argument("--youtube", required=True, help="YouTube video ID (svx... or full URL - see note)")
#     p.add_argument("--gemini-key", default=None, help="Gemini API key (optional)")
#     p.add_argument("--outdir", default=".", help="Output directory")
#     return p.parse_args()

# if __name__ == "__main__":
#     args = parse_args()

#     # If user passed full URL, try to reduce to ID (simple heuristic)
#     video_id = args.youtube
#     if "youtube.com" in video_id or "youtu.be" in video_id:
#         # simple extraction: keep the 11-char id if present
#         import re
#         m = re.search(r"(?:v=|youtu\.be/|\/)([0-9A-Za-z_-]{11})", video_id)
#         if m:
#             video_id = m.group(1)

#     result = run_pipeline(
#         reference_audio_path=args.audio,
#         youtube_video_id=video_id,
#         gemini_api_key=args.gemini_key,
#         output_dir=args.outdir,
#     )

#     logging.info("Result: %s", result)



import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.agent_a1_audio_cleaner import AgentA1AudioCleaner
from agents.agent_a2_transcriber import AgentA2Transcriber
from agents.agent_a3_voice_cloner import AgentA3VoiceCloner

from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI
from langchain.chains import SequentialChain
from langchain.schema import HumanMessage

# Dummy LLM to satisfy LangChain requirements — not used for real generation
from langchain.llms.fake import FakeListLLM

# ------------------------------------------
# Step 1: Initialize your agent classes
# ------------------------------------------
a1 = AgentA1AudioCleaner()
a2 = AgentA2Transcriber()
a3 = AgentA3VoiceCloner()

# ------------------------------------------
# Step 2: Define them as LangChain Tools
# ------------------------------------------
def clean_audio_tool(input_path):
    print("🧹 [A1] Cleaning audio...")
    cleaned = a1.clean_audio(input_path)
    print("✅ Audio cleaned!")
    return cleaned

def transcribe_tool(cleaned_path):
    print("🧾 [A2] Transcribing...")
    text = a2.get_youtube_transcript("E9lAeMz1DaM")  # example video ID
    print("✅ Transcript done!")
    return text

def clone_voice_tool(text):
    print("🎙️ [A3] Cloning voice...")
    result = a3.clone_voice(text)
    print("✅ Voice cloned!")
    return result

tools = [
    Tool(name="Audio Cleaner", func=clean_audio_tool, description="Cleans uploaded audio."),
    Tool(name="Transcriber", func=transcribe_tool, description="Transcribes and polishes text."),
    Tool(name="Voice Cloner", func=clone_voice_tool, description="Generates cloned voice output."),
]

# ------------------------------------------
# Step 3: Create the simple agent orchestrator
# ------------------------------------------
print("\n🚀 Running Chatterbox Autonomous Agent Workflow\n")

llm = FakeListLLM(responses=["Clean", "Transcribe", "Clone"])

agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description", verbose=True)

# Simulate running each agent in sequence
cleaned_audio = clean_audio_tool("sample-2.wav")
transcribed_text = transcribe_tool(cleaned_audio)
cloned_output = clone_voice_tool(transcribed_text)

print("\n🎯 Workflow Complete!\n")
