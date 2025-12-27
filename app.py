import streamlit as st
import whisper
import yt_dlp
from transformers import pipeline
from datetime import timedelta

# --- 1. SETUP ---
st.set_page_config(page_title="Meaningful TubeStamp", layout="wide")

@st.cache_resource
def load_pro_models():
    # Whisper for timing, BART for meaningful titles
    return whisper.load_model("base"), pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def format_time(seconds):
    return str(timedelta(seconds=int(seconds)))

# --- 2. UI ---
st.title("📑 Smart YouTube Chapters")
url = st.text_input("YouTube URL", placeholder="https://...")

if st.button("Generate Meaningful Chapters"):
    if url:
        with st.status("🧠 Thinking deeply about the video content...", expanded=True) as status:
            # A. Download
            st.write("📥 Downloading audio...")
            with yt_dlp.YoutubeDL({'format': 'm4a/bestaudio/best', 'outtmpl': 'tmp.m4a', 'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=True)
                v_id = info['id']

            # B. AI Analysis
            asr, summarizer = load_pro_models()
            st.write("🎙️ Understanding speech...")
            result = asr.transcribe("tmp.m4a")

            # C. "Meaningful" Logic: Group segments until they form a new topic
            st.write("📑 Segmenting into topics...")
            chapters = []
            temp_text = ""
            start_time = 0

            for i, segment in enumerate(result['segments']):
                temp_text += segment['text'] + " "
                
                # Logic: Create a chapter if it's the start (0:00) 
                # OR if 3 minutes have passed (topic boundary)
                if i == 0 or (segment['end'] - start_time) > 180:
                    # Summarize the block into a meaningful title
                    if i == 0:
                        title = "Introduction"
                    else:
                        # Feed the last 1000 characters to the summarizer
                        summary = summarizer(temp_text[-1000:], max_length=10, min_length=3, do_sample=False)
                        title = summary[0]['summary_text'].replace(".", "").strip().title()
                    
                    chapters.append({
                        "time": int(segment['start']),
                        "label": format_time(segment['start']),
                        "title": title
                    })
                    start_time = segment['end']
                    temp_text = ""

            st.session_state.data = {"chapters": chapters, "v_id": v_id}
            status.update(label="✅ Meaningful Chapters Ready!", state="complete")

# --- 3. DISPLAY ---
if 'data' in st.session_state:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Interactive Chapters")
        for ch in st.session_state.data["chapters"]:
            if st.button(f"⏳ {ch['label']} - {ch['title']}", use_container_width=True):
                st.session_state.jump = ch['time']
    with col2:
        st.subheader("Video Player")
        st.video(f"https://youtu.be/{st.session_state.data['v_id']}", start_time=st.session_state.get('jump', 0))
