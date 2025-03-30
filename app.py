
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
IS_DEV = os.getenv("APP_MODE") == "dev"
st.set_page_config(page_title="Prompt Synthesizer", page_icon="🧠", layout="centered")

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
    if IS_DEV:
        st.success("Gemini model loaded")
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

# --- Form ---
with st.form("prompt_form"):
    st.markdown("### ✍️ Your Prompt Details")
    goal = st.text_area("💡 What do you want the AI to do?", value=prefill.get("goal", ""))
    
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
                if IS_DEV:
                    st.exception(e)

# --- Prompt History Viewer ---
if not past_prompts.empty:
    st.markdown("## 🕰️ Prompt History")
    with st.expander("View saved prompts"):
        st.dataframe(past_prompts, use_container_width=True)
        st.download_button("📂 Download History CSV", past_prompts.to_csv(index=False), file_name="prompt_history.csv")

render_footer()
