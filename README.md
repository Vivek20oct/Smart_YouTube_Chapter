# 🎬 Smart YouTube Chapters (TubeStamp)

**Smart YouTube Chapters** is an AI-powered tool built with Streamlit that automatically generates meaningful, summarized timestamps for any YouTube video. 

Unlike standard transcription tools that just output text, this app uses a **Dual-AI Architecture**:
1. **OpenAI Whisper (Base):** To listen to the video and extract highly accurate timestamps for every sentence.
2. **DistilBART Summarizer:** To analyze groups of speech and rewrite them into professional, "meaningful" chapter titles.

---

## ✨ Features

- **🎯 Meaningful Titles:** Uses NLP to summarize blocks of text into concise headlines (e.g., "Introduction", "Market Trends Analysis").
- **🚀 One-Click Generation:** Just paste a URL and hit generate.
- **📺 Interactive Player:** The side-by-side view allows you to click a chapter button to jump the video to that exact second.
- **📥 Local Processing:** Runs on your machine—no expensive API keys required.
- **✅ YouTube-Ready:** Generates timestamps in the standard `00:00 - Title` format.

---

## 🛠️ Prerequisites

Before running the application, you must have the following installed on your system:

1. **Python 3.8+**
2. **FFmpeg:** Required for processing the audio files.
   - **Windows:** `choco install ffmpeg`
   - **Mac:** `brew install ffmpeg`
   - **Linux:** `sudo apt install ffmpeg`

---

## 🚀 Installation & Setup

1. **Clone the project folder:**
   ```bash
   cd youtube-chapters
