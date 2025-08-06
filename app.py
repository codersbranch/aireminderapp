import streamlit as st
import ollama  #
import re
from datetime import datetime

def remove_think_tags(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

def convert_to_24_hour_format(match):
    time_str = match.group(0)
    clean_time = time_str.lower().replace('.', ':').strip()
    try:
        dt = datetime.strptime(clean_time, "%I:%M %p")
        return dt.strftime("%H:%M")
    except ValueError:
        return time_str  # return original if invalid
    
def replace_times_in_text(text):
    # Pattern matches times like 6.28 pm, 12:05 am, etc.
    pattern = r"\b\d{1,2}[:.]\d{2}\s*(am|pm)\b"
    return re.sub(pattern, convert_to_24_hour_format, text, flags=re.IGNORECASE)
    
# Query DeepSeek via Ollama
def query_deepseek(prompt):
    try:
        response = ollama.generate(
            model='deepseek-r1:1.5b',
            prompt=prompt,
            options={
                'temperature': 0.3,
                'max_tokens': 2000
            }
        )
        #response = remove_think_tags(response)
        return response['response'].strip()
    except Exception as e:
        return f"❌ Error running DeepSeek: {e}"

# Streamlit UI
st.title("AI Reminder Scheduler")
st.set_page_config(page_title="AI Schedule Generator", layout="centered")
st.write("Enter a description of your reminder with a specific time, and the AI will generate a schedule for you.")

user_input = st.text_area("📥 Describe your reminder:", height=150)

if st.button("Generate Schedule"):
    if user_input.strip() == "":
        st.warning("Please enter a valid input.")
    else:
        with st.spinner("Generating schedule using DeepSeek..."):
          
            final_prompt = (
                f'Generate a text string based only on this input: "{user_input}".\n\n'
                'The output must be in this exact format only (one line per task):\n\n'
                'HH:MM - "task"\n\n'
                'Follow these rules strictly:\n'
                '1. Use exactly 24-hour time format (e.g., 07:00, 14:30, 22:45).\n'
                '2. Each line must begin with the time, followed by a space, a hyphen, another space, then a task in double quotes.\n'
                '3. Do not include any explanations, greetings, comments, or extra text. Only output lines that follow the format.\n'
                '4. Keep task descriptions short and natural.\n\n'
                'Examples:\n'              
                f'13:00 - {user_input}\n'
               
            )


            result = query_deepseek(final_prompt)
            result = remove_think_tags(result)
            result=replace_times_in_text(result)
            #formatted_lines = re.findall(r"\d{1,2}:\d{2}\s*(AM|PM)?\s*-\s*.*", result, re.IGNORECASE)       
            st.success("✅ Schedule Generated")
            st.text_area("🗓️ Your Schedule", result, height=250)            
     
            valid_lines = re.findall(r'\b\d{1,2}:\d{2}\s*-\s*.+', result)       
            # Save to reminders.txt
            with open("reminders.txt", "a", encoding="utf-8") as f:
                for line in valid_lines:
                    f.write(line.strip() + "\n")
            st.info("Saved to reminders.txt ✅")
