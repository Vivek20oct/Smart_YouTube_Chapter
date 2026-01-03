import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import streamlit as st
import yt_dlp
from faster_whisper import WhisperModel
from datetime import timedelta
import re

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------
st.set_page_config(
    page_title="Smart Video Chapter Generator",
    layout="wide"
)

st.title("Smart YouTube Chapter Generator")
st.caption(
    "Automatically creates clean, human-readable chapters from any YouTube video"
)

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def seconds_to_timestamp(seconds: int) -> str:
    """Convert seconds into HH:MM:SS format"""
    return str(timedelta(seconds=int(seconds)))


def normalize_text(text: str) -> str:
    """Clean extra spaces and formatting"""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def feels_like_a_section_title(text: str) -> bool:
    """
    Basic logic to detect sentences that sound like
    a new topic or section heading
    """
    text_lower = text.lower()

    common_starters = [
        "how", "why", "what",
        "first", "second", "third",
        "now", "next",
        "let us", "let's",
        "important", "overview"
    ]

    return (
        any(text_lower.startswith(word) for word in common_starters)
        and len(text.split()) <= 10
    )

# --------------------------------------------------
# LOAD WHISPER MODEL (CPU ONLY)
# --------------------------------------------------
@st.cache_resource
def load_speech_model():
    return WhisperModel(
        model_size_or_path="tiny",
        device="cpu",
        compute_type="int8"
    )

# --------------------------------------------------
# DOWNLOAD AUDIO FROM YOUTUBE
# --------------------------------------------------
def fetch_audio_from_youtube(video_url: str):
    os.makedirs("temp", exist_ok=True)

    ydl_options = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": "temp/%(id)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        },
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }]
    }

    with yt_dlp.YoutubeDL(ydl_options) as downloader:
        info = downloader.extract_info(video_url, download=True)
        video_id = info["id"]

    audio_file_path = f"temp/{video_id}.mp3"

    if not os.path.exists(audio_file_path):
        raise RuntimeError("Audio download failed. Please try another video.")

    return audio_file_path, video_id

# --------------------------------------------------
# TRANSCRIPTION
# --------------------------------------------------
def transcribe_audio(model, audio_path):
    segments, _ = model.transcribe(audio_path)
    return list(segments)

# --------------------------------------------------
# CHAPTER CREATION LOGIC
# --------------------------------------------------
def build_chapters_from_transcript(segments):
    chapters = [{
        "time": 0,
        "title": "Introduction"
    }]

    last_added_time = 0

    for segment in segments:
        sentence = normalize_text(segment.text)

        # Avoid chapters too close to each other
        if segment.start - last_added_time < 60:
            continue

        if feels_like_a_section_title(sentence):
            chapters.append({
                "time": int(segment.start),
                "title": sentence.capitalize()
            })
            last_added_time = segment.start

    return chapters

# --------------------------------------------------
# USER INPUT
# --------------------------------------------------
video_url = st.text_input(
    "Paste YouTube Video Link",
    placeholder="https://www.youtube.com/watch?v=XXXXXXXX"
)

# --------------------------------------------------
# MAIN ACTION
# --------------------------------------------------
if st.button("Generate Chapters"):
    if not video_url.strip():
        st.warning("Please paste a valid YouTube video link.")
    else:
        with st.spinner("Analyzing video and generating chapters..."):
            try:
                whisper_model = load_speech_model()
                audio_path, video_id = fetch_audio_from_youtube(video_url)
                transcript_segments = transcribe_audio(
                    whisper_model,
                    audio_path
                )

                generated_chapters = build_chapters_from_transcript(
                    transcript_segments
                )

                st.session_state.video_id = video_id
                st.session_state.chapters = generated_chapters
                st.session_state.seek_time = 0

                st.success("Chapters generated successfully!")

            except Exception as error:
                st.error(f"Something went wrong: {error}")

# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------
if "chapters" in st.session_state:
    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.subheader("Video Chapters")

        for chapter in st.session_state.chapters:
            if st.button(
                f"⏱ {seconds_to_timestamp(chapter['time'])} — {chapter['title']}",
                use_container_width=True
            ):
                st.session_state.seek_time = chapter["time"]

    with right_col:
        st.subheader("Watch Video")
        st.video(
            f"https://youtu.be/{st.session_state.video_id}",
            start_time=st.session_state.get("seek_time", 0)
        )
