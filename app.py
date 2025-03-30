import streamlit as st
import google.generativeai as genai
from datetime import datetime
import os
import random
from pathlib import Path
from dotenv import load_dotenv

from utils import auth
from utils.helpers import (
    load_lottiefile, load_prompt_history,
    save_prompt_history, build_prompt
)
from utils.constants import valid_tones, output_types, tips
from utils.prompts import get_flat_templates
from utils.ui import render_header, render_sidebar, render_footer

# --- Setup ---
load_dotenv()
st.set_page_config(page_title="Prompt Synthesizer", page_icon="🧠", layout="wide")

auth.init_session_state()

# --- Auth ---
if st.session_state['user'] is None:
    auth.login()
    st.stop()

# --- Sidebar: Logout + UI ---
st.sidebar.write(f"Logged in as: `{st.session_state['user']}`")
if st.sidebar.button("🚪 Logout"):
    auth.logout()

# --- Load Gemini API Key ---
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("❌ GOOGLE_API_KEY not found.")
    st.stop()

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("models/gemini-1.5-flash")
except Exception as e:
    st.error(f"Gemini model error: {e}")
    st.stop()

# --- Load Lottie ---
lottie_path = Path(__file__).parent / "idea.json"
if not lottie_path.exists():
    lottie_path = Path("idea.json")
lottie_json = load_lottiefile(str(lottie_path))

# --- Tip Setup ---
if st.session_state.random_tip is None:
    st.session_state.random_tip = random.choice(tips)

# --- Prompt History Setup ---
history_dir = Path("prompt_histories")
history_dir.mkdir(exist_ok=True)
history_path = history_dir / f"{st.session_state['user']}_prompt_history.csv"
past_prompts = load_prompt_history(history_path)

# --- Templates ---
templates, _ = get_flat_templates()
selected_template = st.session_state.get("selected_template", "")
template_data = templates.get(selected_template, {})
prefill = template_data if template_data else {}

# --- UI Render ---
render_header()
render_sidebar(lottie_json)

# --- Voice Input ---
st.markdown("### 🎙️ Or speak your idea:")
audio_file = st.file_uploader("Upload voice note (.wav/.mp3)", type=["wav", "mp3"])
transcribed_goal = ""
if audio_file is not None:
    with st.spinner("Transcribing..."):
        audio_bytes = audio_file.read()
        try:
            transcribe_prompt = "Transcribe this voice message into a clear goal for an AI prompt."
            transcription = model.generate_content([transcribe_prompt, audio_bytes])
            transcribed_goal = getattr(transcription, "text", "").strip()
            st.success("Transcribed Goal:")
            st.write(transcribed_goal)
        except Exception as e:
            st.error(f"Error transcribing audio: {e}")

# --- Form ---
with st.form("prompt_form"):
    st.markdown("### ✍️ Your Prompt Details")
    goal = st.text_area("💡 What do you want the AI to do?", value=transcribed_goal or prefill.get("goal", ""))

    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("🎭 Tone", valid_tones,
            index=valid_tones.index(prefill.get("tone", valid_tones[0]))
            if prefill.get("tone") in valid_tones else 0)
    with col2:
        output_type = st.selectbox("🧾 Format", output_types,
            index=output_types.index(prefill.get("output_type", output_types[0]))
            if prefill.get("output_type") in output_types else 0)

    audience = st.text_input("👥 Audience (Optional)", value=prefill.get("audience", ""))
    save_txt = st.checkbox("💾 Save this to history?")
    depth = st.slider("🧬 Prompt Inception Depth", 1, 5, 1)
    god_mode = st.checkbox("🛐 Enable Prompt God Mode")

    submitted = st.form_submit_button("✨ Generate Prompt")

if submitted:
    if not goal.strip():
        st.error("Please enter a goal.")
    else:
        with st.spinner("Synthesizing your prompt..."):
            prompt_template = build_prompt(goal, tone, output_type, audience, depth, god_mode)
            try:
                response = model.generate_content(prompt_template)
                result = getattr(response, "text", "").strip()

                if not result:
                    st.error("Empty response. Try again.")
                    st.stop()

                st.markdown("## 🌟 Your Prompt")
                st.markdown(result)
                st.download_button("📥 Download", result, file_name=f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

                # Save last input for remix
                st.session_state.last_prompt_params = {
                    "goal": goal,
                    "tone": tone,
                    "output_type": output_type,
                    "audience": audience,
                    "depth": depth,
                    "god_mode": god_mode,
                }

                # Feedback buttons
                st.markdown("### ⭐ Rate this result:")
                col1, col2 = st.columns(2)
                if col1.button("👍 Like"):
                    st.toast("Thanks for the thumbs up!")
                if col2.button("👎 Dislike"):
                    st.toast("We’ll try to do better!")

                # Save to history
                if save_txt:
                    new_row = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "goal": goal,
                        "tone": tone,
                        "output_type": output_type,
                        "audience": audience,
                        "prompt": result
                    }
                    success = save_prompt_history(history_path, new_row)
                    if success:
                        st.toast("💾 Saved to history")
                    else:
                        st.error("Failed to save history.")

            except Exception as e:
                st.error(f"Error during generation: {e}")

# --- Remix Feature ---
if "last_prompt_params" in st.session_state and st.button("🔁 Remix This Prompt"):
    remix = st.session_state.last_prompt_params.copy()
    remix["tone"] = random.choice([t for t in valid_tones if t != remix["tone"]])
    remix["output_type"] = random.choice([o for o in output_types if o != remix["output_type"]])

    with st.spinner("Remixing your prompt..."):
        remix_prompt = build_prompt(**remix)
        remix_response = model.generate_content(remix_prompt)
        remix_text = getattr(remix_response, "text", "").strip()

        if remix_text:
            st.markdown("### 🎲 Remixed Prompt")
            st.markdown(remix_text)

# --- Prompt History Viewer ---
if not past_prompts.empty:
    st.markdown("## 🕰️ Prompt History")
    with st.expander("View saved prompts"):
        st.dataframe(past_prompts, use_container_width=True)
        st.download_button("📂 Download History CSV", past_prompts.to_csv(index=False), file_name="prompt_history.csv")

render_footer()
