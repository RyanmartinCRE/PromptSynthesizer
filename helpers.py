
import json
from pathlib import Path
import pandas as pd
from datetime import datetime

def load_lottiefile(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {}

def load_prompt_history(history_path):
    try:
        return pd.read_csv(history_path) if history_path.exists() else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def save_prompt_history(history_path, new_row):
    try:
        df = load_prompt_history(history_path)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(history_path, index=False)
        return True
    except Exception as e:
        return False

def build_prompt(goal, tone, output_type, audience, depth, god_mode):
    if "prompt" in goal.lower() and goal.lower().count("prompt") >= 3:
        return f"""
You are an AI that creates prompts for creating prompts.
- Recursion depth: {depth}
- God Mode: {"ON" if god_mode else "OFF"}

Write a meta-level prompt that guides another AI to help someone write better prompts.
Include formatting suggestions and a tip at the end.
"""
    return f"""
You are an AI prompt engineer. Your task is to rewrite a rough user idea into a well-structured AI prompt.

Details:
- Goal: {goal}
- Tone: {tone}
- Format: {output_type}
- Audience: {audience}

Structure the prompt clearly, include instructions for tone and format, and add a customization tip at the end.
"""
