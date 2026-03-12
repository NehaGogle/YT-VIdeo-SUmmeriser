## ⚠️ Prerequisites
- **FFmpeg** required for videos without captions
  - Windows: https://www.gyan.dev/ffmpeg/builds/
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
  
# 🎬 YouTube Video Summarizer

An AI-powered tool that summarizes any YouTube video in seconds!

## ✨ Features
- Paste any YouTube URL and get instant summary
- Choose summary language: English, Hindi, Hinglish
- Choose summary length: Short, Medium, Detailed
- View full transcript

## 🛠️ Tech Stack
- **Groq + LLaMA 3.3** — Fast LLM
- **YouTube Transcript API** — Fetch video captions
- **LangChain** — Prompt chaining
- **Streamlit** — Web UI

## ⚙️ Setup

```bash
git clone https://github.com/your_username/youtube-summarizer.git
cd youtube-summarizer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:
```
GROQ_API_KEY=your_groq_api_key
```

Run:
```bash
streamlit run app.py
```

## 🔑 Get Free API Keys
- Groq: https://console.groq.com

## 📁 Project Structure
```
youtube-summarizer/
├── app.py          # Streamlit UI
├── summarizer.py   # Core logic
├── requirements.txt
└── README.md
```
