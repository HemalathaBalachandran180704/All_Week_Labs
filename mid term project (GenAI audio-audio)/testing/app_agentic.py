# # app_agentic.py
# # Minimal LangChain v1 agent wrapper using ChatGoogleGenerativeAI (Gemini)
# # Place in chatterbox/testing/ and run: streamlit run testing/app_agentic.py

# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import streamlit as st
# from langchain.tools import tool
# from langchain.agents import create_agent
# from langchain_core.messages import HumanMessage

# # use the official Gemini integration
# from langchain_google_genai import ChatGoogleGenerativeAI

# # Import your existing agent modules (these are your local agent-like classes)
# from agents.agent_a1_audio_cleaner import AgentA1AudioCleaner
# from agents.agent_a2_script_processor import AgentA2ScriptProcessor
# from agents.agent_a3_voice_cloner import AgentA3VoiceCloner

# # ---------- Gemini LLM setup ----------
# os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "AIzaSyCa7Oxs0QgpxkFgQZtYX9iuS53-uPPiZaA")

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0.3,
#     max_output_tokens=512,
#     timeout=60,
#     max_retries=2,
# )

# # ---------- Tools (each MUST have a clear docstring) ----------
# @tool
# def clean_audio_tool(audio_path: str) -> str:
#     """Clean audio at the given path (denoise/normalize) and return path to cleaned WAV."""
#     agent = AgentA1AudioCleaner()
#     out_path = agent.process_audio(audio_path, "cleaned_audio_agentic.wav")
#     return out_path

# @tool
# def process_script_tool(youtube_link_or_id: str) -> str:
#     """Transcribe the YouTube video and return a polished transcript (string)."""
#     agent = AgentA2ScriptProcessor()
#     # AgentA2ScriptProcessor.process_youtube should accept either full URL or ID
#     processed = agent.process_youtube(youtube_link_or_id)
#     return processed

# @tool
# def clone_voice_tool(audio_path: str, script_text: str) -> str:
#     """Clone the voice from audio_path and synthesize script_text; returns output file path."""
#     agent = AgentA3VoiceCloner()
#     out = agent.clone_voice(audio_path, script_text, "final_cloned_agentic.wav")
#     return out

# # ---------- Create agent with a plain system prompt (avoid hub/PromptTemplate complexities) ----------
# SYSTEM_PROMPT = (
#     "You are an orchestration assistant. You have three tools: "
#     "clean_audio_tool(audio_path), process_script_tool(youtube_link_or_id), clone_voice_tool(audio_path, script_text). "
#     "When instructed, invoke the right tools in order and return a short summary of the outputs (file paths or transcript)."
# )

# agent = create_agent(
#     model=llm,
#     tools=[clean_audio_tool, process_script_tool, clone_voice_tool],
#     system_prompt=SYSTEM_PROMPT,
# )

# # ---------- Streamlit UI ----------
# st.title("🤖 LangChain Agentic Workflow — Chatterbox (Gemini-Powered) — Test Agentic")
# st.write("This demos your a1/a2/a3 pipeline wrapped by a LangChain agent (minimal).")

# uploaded_audio = st.file_uploader("Upload audio (WAV) for cleaning", type=["wav"])
# youtube_url = st.text_input("YouTube URL or Video ID (ID works)")

# if st.button("Run Agentic Workflow"):
#     if not uploaded_audio or not youtube_url:
#         st.warning("Upload audio and provide YouTube link or ID.")
#     else:
#         tmp_audio = "temp_agent_audio.wav"
#         with open(tmp_audio, "wb") as f:
#             f.write(uploaded_audio.getbuffer())

#         st.info("Running agent orchestration... this can take a bit")

#         # Create the user query in plain text
#         query = (
#             f"1) Clean the uploaded audio at '{tmp_audio}'. "
#             f"2) Extract and polish transcript from '{youtube_url}'. "
#             f"3) Clone the voice using the cleaned audio and processed transcript. "
#             f"Return a short summary including cleaned audio path, transcript snippet, and cloned audio path."
#         )

#         try:
#             # agent.invoke expects a dict with messages list
#             response = agent.invoke({
#                 "messages": [{"role": "user", "content": query}]
#             })

#             # response may be complex; stringify safely
#             st.success("Agent run finished.")
#             st.text_area("Agent response (raw)", str(response), height=400)

#         except Exception as e:
#             st.error(f"Agentic run failed: {e}")
#             # show a small tip for debugging
#             st.write("Tip: if Gemini/API timed out, try smaller inputs or increase timeout.")




# testing/app_agentic.py
import sys
import os
from pathlib import Path
import streamlit as st
import traceback

# ensure package imports resolve to project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# -----------------------------
# Import existing agents / utils
# -----------------------------
from agents.agent_a1_audio_cleaner import AgentA1AudioCleaner
from agents.agent_a3_voice_cloner import AgentA3VoiceCloner
# transcriber.get_transcript expects a video id (per your working code)
from utils.transcriber import get_transcript, extract_video_id

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Agentic Demo — A1/A2/A3 (No LangChain)", layout="centered")
st.title("🤖 Agentic Demo — A1 (Cleaner) → A2 (Transcriber) → A3 (Cloner)")
st.write("This demo runs your existing agents sequentially (no LangChain). It won't change your main app.")

uploaded_audio = st.file_uploader("Upload audio (WAV) for cleaning", type=["wav"])
youtube_link = st.text_input("YouTube URL or Video ID (both work)", placeholder="https://www.youtube.com/watch?v=svxK22S8Swo")

# temp file names (kept inside project so nothing global breaks)
BASE = Path(".")
TEMP_UPLOAD = BASE / "temp_agent_audio.wav"
CLEANED_PATH = BASE / "cleaned_audio_agentic.wav"
CLONED_PATH = BASE / "final_cloned_agentic.wav"

if st.button("🚀 Run Agentic Pipeline (A1 → A2 → A3)"):
    # Basic input checks
    if (not uploaded_audio) or (not youtube_link):
        st.warning("Please upload a WAV file AND provide a YouTube URL or video ID.")
        st.stop()

    # Save upload
    try:
        with open(TEMP_UPLOAD, "wb") as f:
            f.write(uploaded_audio.getbuffer())
        st.success(f"Saved uploaded file to {TEMP_UPLOAD}")
    except Exception as e:
        st.error(f"Failed to save uploaded audio: {e}")
        st.stop()

    # Initialize agents (they use local logic; safe)
    agent_a1 = AgentA1AudioCleaner()
    agent_a3 = AgentA3VoiceCloner()

    # Step 1 — Audio cleaning
    st.subheader("Step 1 — Audio cleaning (Agent A1)")
    try:
        with st.spinner("Cleaning audio..."):
            cleaned = agent_a1.process_audio(str(TEMP_UPLOAD), str(CLEANED_PATH))
        st.success("Audio cleaned!")
        st.write(f"Cleaned audio path: `{cleaned}`")
        st.audio(str(CLEANED_PATH))
    except Exception as e:
        st.error("Audio cleaning failed.")
        st.text(traceback.format_exc())
        st.stop()

    # Step 2 — Transcription (A2 simplified)
    st.subheader("Step 2 — Transcription (Agent A2 simplified)")
    try:
        # Accept only full URL
        vid = youtube_link.strip()

        with st.spinner("Fetching transcript from YouTube..."):
            transcript = get_transcript(vid)


        st.success("Transcript fetched!")
        st.text_area("Raw transcript (first 1500 chars)", transcript[:1500], height=240)
    except Exception as e:
        st.error(f"Transcript error: {e}")
        st.text(traceback.format_exc())
        st.stop()


    # Step 3 — Voice cloning (Agent A3)
    print("\nStep 3 — Voice cloning (Agent A3)")

    try:
        # Keep transcript within safe limits (e.g., first 800 chars)
        safe_text = transcript.strip()[:800]

        cloned = agent_a3.clone_voice(
            str(CLEANED_PATH),
            safe_text,
            str(CLONED_PATH)
        )
        print("\n✅ Voice cloning completed! Saved at:", CLONED_PATH)

    except Exception as e:
        print(f"\nVoice cloning failed: {e}")

        st.text(traceback.format_exc())
        st.stop()

    # Final summary
    st.markdown("### ✅ Pipeline finished")
    st.write({
        "uploaded": str(TEMP_UPLOAD),
        "cleaned_audio": str(CLEANED_PATH),
        "cloned_audio": str(CLONED_PATH),
    })
