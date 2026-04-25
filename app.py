from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

import ollama
import streamlit as st

REMINDER_FILE = Path("reminders.txt")
THINK_TAGS_RE = re.compile(r"<think>.*?</think>", flags=re.DOTALL)
TWELVE_HOUR_TIME_RE = re.compile(r"\b\d{1,2}[:.]\d{2}\s*(am|pm)\b", flags=re.IGNORECASE)
SCHEDULE_LINE_RE = re.compile(r"\b\d{2}:\d{2}\s*-\s*.+")


def remove_think_tags(text: str) -> str:
    return THINK_TAGS_RE.sub("", text)


def convert_to_24_hour_format(match: re.Match[str]) -> str:
    time_str = match.group(0)
    clean_time = time_str.lower().replace(".", ":").strip()
    try:
        dt = datetime.strptime(clean_time, "%I:%M %p")
        return dt.strftime("%H:%M")
    except ValueError:
        return time_str


def replace_times_in_text(text: str) -> str:
    return TWELVE_HOUR_TIME_RE.sub(convert_to_24_hour_format, text)


def query_deepseek(prompt: str) -> str:
    try:
        response = ollama.generate(
            model="deepseek-r1:1.5b",
            prompt=prompt,
            options={
                "temperature": 0.3,
                "num_predict": 512,
            },
        )
        return response["response"].strip()
    except Exception as exc:  # noqa: BLE001 - surfaced directly in UI
        return f"❌ Error running DeepSeek: {exc}"


def save_valid_schedule_lines(result: str, reminder_file: Path = REMINDER_FILE) -> int:
    valid_lines = SCHEDULE_LINE_RE.findall(result)
    if not valid_lines:
        return 0

    with reminder_file.open("a", encoding="utf-8") as file:
        for line in valid_lines:
            file.write(f"{line.strip()}\n")

    return len(valid_lines)


st.set_page_config(page_title="AI Schedule Generator", layout="centered")
st.title("AI Reminder Scheduler")
st.write(
    "Enter a description of your reminder with a specific time, and the AI will generate a schedule for you."
)

user_input = st.text_area("📥 Describe your reminder:", height=150)

if st.button("Generate Schedule"):
    if not user_input.strip():
        st.warning("Please enter a valid input.")
    else:
        with st.spinner("Generating schedule using DeepSeek..."):
            final_prompt = (
                f'Generate a text string based only on this input: "{user_input}".\n\n'
                "The output must be in this exact format only (one line per task):\n\n"
                'HH:MM - "task"\n\n'
                "Follow these rules strictly:\n"
                "1. Use exactly 24-hour time format (e.g., 07:00, 14:30, 22:45).\n"
                "2. Each line must begin with the time, followed by a space, a hyphen, another space, then a task in double quotes.\n"
                "3. Do not include any explanations, greetings, comments, or extra text. Only output lines that follow the format.\n"
                "4. Keep task descriptions short and natural.\n\n"
                "Example:\n"
                '13:00 - "Send project update"\n'
            )

            result = query_deepseek(final_prompt)
            result = remove_think_tags(result)
            result = replace_times_in_text(result)

            st.success("✅ Schedule Generated")
            st.text_area("🗓️ Your Schedule", result, height=250)

            saved_count = save_valid_schedule_lines(result)
            if saved_count:
                st.info(f"Saved {saved_count} reminder(s) to reminders.txt ✅")
            else:
                st.warning("No valid reminder lines found to save.")
