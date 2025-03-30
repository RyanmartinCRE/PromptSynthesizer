
import streamlit as st
import random
import re
from streamlit_lottie import st_lottie
from utils.constants import category_emojis, sign_offs, tips
from utils.prompts import templates_by_category, get_flat_templates

def render_header():
    st.markdown("""
        <div style="background: linear-gradient(135deg, #6e8efb, #a777e3); padding: 2rem 1rem; border-radius: 1.5rem; text-align: center; color: white; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem;">💡 Prompt Synthesizer</h1>
            <p style="font-size: 1.1rem;">Turn your rough idea into a polished AI prompt</p>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar(lottie_json):
    st_lottie(lottie_json, width=200, height=200, key="idea")
    st.markdown("### 💡 Prompt Toolkit")
    st.markdown(f"📌 *Tip of the Day:* **{st.session_state.random_tip}**")
    st.markdown("---")

    templates, _ = get_flat_templates()

    if st.button("🎲 Surprise Me!"):
        st.session_state.selected_template = random.choice(list(templates.keys()))

    st.markdown("### 📁 Templates")
    for category, entries in templates_by_category.items():
        emoji = category_emojis.get(category, "")
        st.markdown(f"**{emoji} {category}**")
        for name in entries:
            key_safe = re.sub(r'\W+', '_', name)
            if st.button(name, key=f"btn_{key_safe}"):
                st.session_state.selected_template = name

def render_footer():
    st.markdown(f"<div style='text-align: center; font-size: 0.9rem; color: gray;'>{random.choice(sign_offs)}</div>", unsafe_allow_html=True)
