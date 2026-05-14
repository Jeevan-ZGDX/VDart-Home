"""Streamlit Dashboard for CMFH
AI TEDX Speech Coach - Voice, Text, and Camera Input
"""

import streamlit as st
import requests
import json
import time
import base64
import cv2
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import asyncio
from io import BytesIO

API_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title="CMFH - AI Speech Coach",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)


class CMFHClient:
    """Client for CMFH API"""

    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url

    def transcribe_audio_file(self, audio_data: bytes, filename: str = "audio.webm"):
        """Transcribe audio file"""
        try:
            files = {"audio_file": (filename, audio_data, "audio/webm")}
            response = requests.post(f"{self.base_url}/transcribe", files=files, timeout=120)
            return response.json()
        except Exception as e:
            return {"text": "", "success": False, "error": str(e)}

    def transcribe_text(self, text: str):
        """Transcribe text directly"""
        try:
            response = requests.post(f"{self.base_url}/transcribe", data={"text": text}, timeout=30)
            return response.json()
        except Exception as e:
            return {"text": "", "success": False, "error": str(e)}

    def analyze(self, text: str):
        """Analyze text"""
        return requests.post(f"{self.base_url}/analyze", json={"text": text}, timeout=30).json()

    def complete_analysis(self, text: str):
        """Complete analysis with NLP, TEDX, and rewrite"""
        return requests.post(f"{self.base_url}/analyze/complete", json={"text": text}, timeout=60).json()

    def rewrite(self, text: str, style: str = "professional"):
        """Rewrite text"""
        return requests.post(f"{self.base_url}/rewrite", json={"text": text, "style": style}, timeout=60).json()

    def feedback(self, text: str):
        """Get feedback"""
        return requests.post(f"{self.base_url}/feedback", json={"text": text}, timeout=30).json()

    def analyze_tedx(self, text: str):
        """TEDX analysis"""
        return requests.post(f"{self.base_url}/analyze/tedx", json={"text": text}, timeout=30).json()

    def analyze_pose(self, file):
        """Analyze pose from image"""
        files = {"file": file}
        return requests.post(f"{self.base_url}/vision/analyze/pose", files=files, timeout=30).json()

    def history(self, limit: int = 10):
        """Get history"""
        return requests.get(f"{self.base_url}/history?limit={limit}", timeout=10).json()

    def health(self):
        """Health check"""
        return requests.get(f"{self.base_url}/health", timeout=10).json()


client = CMFHClient()


def init_session_state():
    """Initialize session state"""
    if "transcript" not in st.session_state:
        st.session_state.transcript = ""
    if "analysis" not in st.session_state:
        st.session_state.analysis = None
    if "rewritten" not in st.session_state:
        st.session_state.rewritten = None
    if "feedback" not in st.session_state:
        st.session_state.feedback = None
    if "audio_data" not in st.session_state:
        st.session_state.audio_data = None


def render_header():
    """Render header"""
    st.title("🎤 CMFH - Call Me For Help")
    st.markdown("**AI TEDX Speech Coach & Professional Communication Assistant**")
    st.markdown("---")


def render_sidebar():
    """Render sidebar"""
    st.sidebar.title("📊 Dashboard")

    try:
        history = client.history(limit=5)
        stats = history.get("statistics", {})
        with st.sidebar.expander("📈 Session Stats", expanded=True):
            st.metric("Total Sessions", stats.get("total_sessions", 0))
            st.metric("Average Score", stats.get("average_score", 0))
            st.metric("Recent Average", stats.get("recent_average", 0))
    except:
        pass

    with st.sidebar.expander("ℹ️ System Status"):
        try:
            health = client.health()
            st.success(f"Status: {health.get('status', 'unknown')}")
            st.info(f"Whisper: {health.get('whisper_model', 'unknown')}")
            st.info(f"Ollama: {'✅' if health.get('ollama_available') else '❌'}")
        except:
            st.error("Backend not connected")


def render_voice_input():
    """Render voice input section"""
    st.subheader("🎙️ Voice Input")

    tab1, tab2 = st.tabs(["📁 Upload Audio File", "🎤 Real-time Recording"])

    with tab1:
        st.markdown("**Upload audio file (.mp3, .wav, .m4a, .webm)**")
        audio_file = st.file_uploader("Choose audio file", type=["mp3", "wav", "m4a", "ogg", "webm", "flac"])

        if audio_file:
            if st.button("🔄 Transcribe Audio", type="primary"):
                with st.spinner("Transcribing audio... This may take a while..."):
                    try:
                        audio_bytes = audio_file.getvalue()
                        result = client.transcribe_audio_file(audio_bytes, audio_file.name)

                        if result.get("success") and result.get("text"):
                            st.session_state.transcript = result["text"]
                            st.success(f"✅ Transcribed: {result['text'][:200]}...")
                            st.session_state.audio_processed = True
                        else:
                            st.error(f"Transcription failed: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    with tab2:
        st.markdown("**Real-time Microphone Recording**")

        st.info("🎤 Click the button below to record your voice")

        if st.button("🎤 Start Real-time Recording", type="primary", use_container_width=True):
            st.session_state.recording = True
            st.info("🔴 Recording started! Speak now...")

        if st.session_state.get("recording", False):
            st.warning("Recording in progress... Click 'Stop & Transcribe' when done.")

            if st.button("⏹️ Stop & Transcribe"):
                st.session_state.recording = False
                st.warning("Processing recorded audio...")

                st.info("📝 For real-time recording, please use the audio file upload feature.")
                st.info("💡 Tip: Record your voice using any voice recorder app, save as .wav/.mp3, then upload above!")

        st.markdown("---")
        st.markdown("**Supported formats:** MP3, WAV, M4A, OGG, WebM, FLAC")
        st.markdown("**Tip:** Use your phone or computer voice recorder, save the file, and upload above!")


def render_text_input():
    """Render text input section"""
    st.subheader("📝 Text Input")

    text_input = st.text_area(
        "Enter your speech:",
        value=st.session_state.transcript,
        height=150,
        placeholder="Type or paste your speech here to analyze and rewrite as a TEDX speaker..."
    )

    if text_input != st.session_state.transcript:
        st.session_state.transcript = text_input

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Analyze Speech", type="primary", use_container_width=True):
            if st.session_state.transcript.strip():
                analyze_speech()
            else:
                st.warning("Please enter some text")

    with col2:
        if st.button("✍️ Rewrite as TEDX", use_container_width=True):
            if st.session_state.transcript.strip():
                rewrite_speech()
            else:
                st.warning("Please enter some text")

    with col3:
        if st.button("🎯 Complete Analysis", use_container_width=True):
            if st.session_state.transcript.strip():
                complete_analysis()
            else:
                st.warning("Please enter some text")

    if st.button("📝 Clear"):
        st.session_state.transcript = ""
        st.session_state.analysis = None
        st.session_state.rewritten = None
        st.session_state.feedback = None
        st.rerun()


def render_camera_input():
    """Render camera/pose input section"""
    st.subheader("📸 Camera / Pose Analysis")

    tab1, tab2 = st.tabs(["📁 Upload Image/Video", "📹 About Camera"])

    with tab1:
        st.markdown("**Upload image or video for pose analysis**")
        pose_file = st.file_uploader("Choose file", type=["jpg", "jpeg", "png", "mp4", "avi", "mov"])
        if pose_file:
            if st.button("🔄 Analyze Pose", type="primary"):
                with st.spinner("Analyzing pose..."):
                    try:
                        files = {"file": (pose_file.name, pose_file.getvalue(), pose_file.type)}
                        response = requests.post(f"{API_URL}/vision/analyze/pose", files=files, timeout=30)
                        if response.status_code == 200:
                            result = response.json()
                            display_pose_results(result)
                        else:
                            st.error("Pose analysis failed")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    with tab2:
        st.markdown("**📹 Live Camera Information**")
        st.info("""
        For live camera feed with real-time pose detection:

        1. **Streamlit limitation**: Streamlit doesn't support continuous webcam streaming natively

        2. **Workaround options**:
           - Record yourself on your phone/computer
           - Take photos while practicing
           - Upload the recording/image above

        3. **Features available**:
           - ✅ Upload images (JPG, PNG)
           - ✅ Upload videos (MP4, AVI)
           - ✅ Pose detection & analysis
           - ✅ Posture scoring
           - ✅ Hand gesture detection
           - ✅ Body language suggestions
        """)


def display_pose_results(result: dict):
    """Display pose analysis results"""
    if not result.get("detected", False):
        st.warning(result.get("message", "No person detected"))
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Posture", f"{result.get('posture_score', 0)}%")

    with col2:
        st.metric("Shoulder Balance", f"{result.get('shoulder_balance', 0)}%")

    with col3:
        st.metric("Hand Gesture", result.get('hand_gesture', 'N/A'))

    with col4:
        st.metric("Confidence", result.get('confidence_level', 'N/A').upper())

    st.markdown("**💡 Suggestions:**")
    for suggestion in result.get("suggestions", []):
        st.write(f"- {suggestion}")


def analyze_speech():
    """Analyze speech"""
    with st.spinner("Analyzing your speech..."):
        try:
            analysis = client.analyze(st.session_state.transcript)
            st.session_state.analysis = analysis
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")


def rewrite_speech():
    """Rewrite speech"""
    with st.spinner("Generating professional TEDX-style rewrite..."):
        try:
            rewrite = client.rewrite(st.session_state.transcript, "tedx")
            st.session_state.rewritten = rewrite
        except Exception as e:
            st.error(f"Rewrite failed: {str(e)}")


def complete_analysis():
    """Complete analysis with all features"""
    with st.spinner("Performing complete analysis..."):
        try:
            result = client.complete_analysis(st.session_state.transcript)
            st.session_state.analysis = result
            st.session_state.rewritten = {"rewritten": result.get("rewritten", ""), "source": "llm"}
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")


def render_results():
    """Render analysis results"""
    if not st.session_state.analysis:
        return

    analysis = st.session_state.analysis

    if isinstance(analysis, dict):
        if "scores" in analysis:
            render_complete_results(analysis)
        else:
            render_nlp_results(analysis)
    else:
        st.warning("No results to display")


def render_nlp_results(analysis: dict):
    """Render NLP analysis results"""
    st.subheader("📊 Analysis Results")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        score = analysis.get("overall_score", 0)
        st.metric("Overall Score", f"{score}/100")

    with col2:
        grammar = analysis.get("grammar", {})
        errors = grammar.get("error_count", 0)
        st.metric("Grammar Errors", errors)

    with col3:
        filler = analysis.get("filler", {})
        filler_ratio = filler.get("filler_ratio", 0)
        st.metric("Filler Ratio", f"{filler_ratio}%")

    with col4:
        conf = analysis.get("confidence", {})
        conf_score = conf.get("confidence_score", 0)
        st.metric("Confidence", f"{conf_score}/100")

    with col5:
        vocab = analysis.get("vocabulary", {})
        vocab_score = vocab.get("vocabulary_score", 0)
        st.metric("Vocabulary", f"{vocab_score}/100")


def render_complete_results(result: dict):
    """Render complete analysis results"""
    st.subheader("📊 Complete Analysis Results")

    scores = result.get("scores", {})
    nlp = result.get("nlp_analysis", {})
    tedx = result.get("tedx_analysis", {})
    feedback = result.get("feedback", {})

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Overall", f"{scores.get('overall_score', 0)}/100", scores.get('grade', 'N/A'))

    with col2:
        filler_data = nlp.get('filler', {})
        st.metric("Filler", f"{filler_data.get('filler_ratio', 0)}%", f"Count: {filler_data.get('filler_count', 0)}")

    with col3:
        conf_data = nlp.get('confidence', {})
        st.metric("Confidence", f"{conf_data.get('confidence_score', 0)}/100")

    with col4:
        st.metric("TEDX Score", f"{tedx.get('score', 0)}/100")

    with col5:
        vocab_data = nlp.get('vocabulary', {})
        st.metric("Vocabulary", f"{vocab_data.get('vocabulary_score', 0)}/100")

    with st.expander("📋 Detailed TEDX Analysis", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**TEDX Scores:**")
            st.write(f"- Story Score: {tedx.get('story_score', 0)}")
            st.write(f"- Persuasion: {tedx.get('persuasion_score', 0)}")
            st.write(f"- Rhythm: {tedx.get('rhythm_score', 0)}")
            st.write(f"- Structure: {tedx.get('structure_score', 0)}")

        with col2:
            st.markdown("**Strengths:**")
            for s in tedx.get("strengths", []):
                st.write(f"- {s}")

    if tedx.get("improvements"):
        with st.expander("🎯 Improvements"):
            for imp in tedx.get("improvements", []):
                st.write(f"- {imp}")

    if feedback:
        with st.expander("💡 Feedback"):
            st.write(f"**Summary:** {feedback.get('summary', '')}")
            st.write("**Encouragement:**", feedback.get('encouragement', ''))


def render_rewrite():
    """Render rewrite results"""
    if not st.session_state.rewritten:
        return

    st.subheader("✍️ Professional TEDX Rewrite")

    rewritten = st.session_state.rewritten.get("rewritten", "")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Your Speech:**")
        orig = st.session_state.transcript
        st.info(orig[:300] + "..." if len(orig) > 300 else orig)

    with col2:
        st.markdown("**TEDX-Style Rewrite:**")
        st.success(rewritten[:300] + "..." if len(rewritten) > 300 else rewritten)


def main():
    """Main function"""
    init_session_state()

    render_header()
    render_sidebar()

    st.markdown("## 📥 Choose Input Method")
    input_method = st.radio(
        "Select input type:",
        ["🎤 Voice/Audio", "📝 Text", "📸 Camera/Pose"],
        horizontal=True
    )

    st.markdown("---")

    if input_method == "🎤 Voice/Audio":
        render_voice_input()
    elif input_method == "📝 Text":
        render_text_input()
        if st.session_state.transcript.strip():
            render_results()
            render_rewrite()
    elif input_method == "📸 Camera/Pose":
        render_camera_input()

    st.markdown("---")

    try:
        history = client.history(limit=5)
        if history.get("sessions"):
            st.subheader("📜 Recent Sessions")
            for session in history["sessions"][:3]:
                with st.expander(f"Session #{session['id']} - {session.get('grade', 'N/A')}"):
                    st.write(f"**Score:** {session.get('overall_score', 0)}/100")
                    st.write(f"**Text:** {session.get('original_text', 'N/A')[:100]}...")
    except:
        pass


if __name__ == "__main__":
    main()