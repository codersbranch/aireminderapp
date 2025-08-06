

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-reminder-scheduler.git
cd ai-reminder-scheduler
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

### 4. Make Sure Ollama is Installed and DeepSeek Model is Pulled

Install Ollama from [https://ollama.com](https://ollama.com) if you haven’t already.

Pull the DeepSeek model:

```bash
ollama pull deepseek-r1:1.5b
```

---

## 🚀 Run the App

```bash
streamlit run app.py
```

Replace `app.py` with your Python script filename if different.

---

```bash
python check_reminders.py
```




---

## 🧾 Reminder File

Every valid line generated is automatically saved to:

```
reminders.txt
```


---





