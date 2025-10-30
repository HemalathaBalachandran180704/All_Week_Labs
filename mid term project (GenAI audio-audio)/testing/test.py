import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib

modules_to_test = [
    "streamlit",
    "langchain",
    "langchain.tools",
    "langchain_google_genai",
    "langchain_core.language_models.chat_models",
    "langchain_core.outputs",
    "langchain_core.messages",
    "pydantic",
    "agents.agent_a1_audio_cleaner",
    "agents.agent_a2_script_processor",
    "agents.agent_a3_voice_cloner",
    "langchain.agents",
    "langchain_classic.hub",  # ✅ replace old hub import with this
]

print("🔍 Checking imports...\n")

for module_name in modules_to_test:
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} — OK")
    except Exception as e:
        print(f"❌ {module_name} — {type(e).__name__}: {e}")

print("\n✅ Import check completed.")
