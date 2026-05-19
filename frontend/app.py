"""Streamlit Dashboard for CMFH
AI TEDX Speech Coach - Voice, Text, and Camera Input
"""

import streamlit as st
import requests
import json
import time
import base64
import os
from datetime import datetime

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

    def transcribe_audio(self, audio_file):
        """Transcribe audio file"""
        try:
            files = {"audio_file": (audio_file.name, audio_file.getvalue(), audio_file.type)}
            response = requests.post(f"{self.base_url}/transcribe", files=files, timeout=120)
            return response.json()
        except requests.exceptions.Timeout:
            return {"text": "", "success": False, "error": "Timeout - audio too long"}
        except requests.exceptions.ConnectionError:
            return {"text": "", "success": False, "error": "Backend not connected"}
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

    def analyze_pose(self, file):
        """Analyze pose from image"""
        try:
            files = {"file": (file.name, file.getvalue(), file.type)}
            return requests.post(f"{self.base_url}/vision/analyze/pose", files=files, timeout=30).json()
        except Exception as e:
            return {"detected": False, "message": str(e)}

    def history(self, limit: int = 10):
        """Get history"""
        try:
            return requests.get(f"{self.base_url}/history?limit={limit}", timeout=10).json()
        except:
            return {"sessions": [], "statistics": {"total_sessions": 0}}

    def health(self):
        """Health check"""
        try:
            return requests.get(f"{self.base_url}/health", timeout=5).json()
        except:
            return {"status": "error"}


client = CMFHClient()


def init_session_state():
    """Initialize session state"""
    if "transcript" not in st.session_state:
        st.session_state.transcript = ""
    if "analysis" not in st.session_state:
        st.session_state.analysis = None
    if "rewritten" not in st.session_state:
        st.session_state.rewritten = None
    if "audio_transcribed" not in st.session_state:
        st.session_state.audio_transcribed = False


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
        with st.sidebar.expander("📈 Session Stats", expanded=False):
            st.metric("Total Sessions", stats.get("total_sessions", 0))
            st.metric("Average Score", stats.get("average_score", 0))
    except:
        pass

    with st.sidebar.expander("ℹ️ System Status"):
        try:
            health = client.health()
            if health.get("status") == "healthy":
                st.success(f"✅ Backend Connected")
                st.info(f"Whisper: {health.get('whisper_model', 'unknown')}")
                st.info(f"Ollama: {'✅' if health.get('ollama_available') else '❌'}")
            else:
                st.error("❌ Backend not responding")
        except:
            st.error("❌ Cannot connect to backend")


def render_voice_input():
    """Render voice input section"""
    st.subheader("🎙️ Voice/Audio Input")

    tab1, tab2 = st.tabs(["📁 Upload Audio File", "ℹ️ How to Use"])

    with tab1:
        st.markdown("**Upload an audio file to transcribe**")
        
        audio_file = st.file_uploader(
            "Choose audio file",
            type=["mp3", "wav", "m4a", "ogg", "webm", "flac", "wma", "aac"]
        )

        if audio_file:
            st.info(f"📄 File: {audio_file.name} ({audio_file.size/1024:.1f} KB)")
            
            if st.button("🔄 Transcribe Audio", type="primary", use_container_width=True):
                with st.spinner("⏳ Transcribing audio... (this may take a moment)"):
                    try:
                        result = client.transcribe_audio(audio_file)
                        
                        if result.get("success") and result.get("text"):
                            st.session_state.transcript = result["text"]
                            st.session_state.audio_transcribed = True
                            st.success(f"✅ Transcribed successfully!")
                            st.info(f"**Transcript:** {result['text'][:500]}...")
                            if len(result['text']) > 500:
                                st.info(f"... (total {len(result['text'])} characters)")
                        else:
                            error_msg = result.get("error", "Unknown error")
                            st.error(f"❌ Transcription failed: {error_msg}")
                            
                            if "ffmpeg" in error_msg.lower():
                                st.info("💡 Tip: Install ffmpeg to support more audio formats")
                            elif "model" in error_msg.lower():
                                st.info("💡 Tip: Check if faster-whisper is properly installed")
                                
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    with tab2:
        st.markdown("""
        **🎤 How to use voice input:**
        
        1. **Record your voice** using your phone or computer's voice recorder
        
        2. **Save as audio file** - Supported formats:
           - MP3 (most common)
           - WAV (best quality)
           - M4A (iPhone)
           - OGG, WebM, FLAC
        
        3. **Upload** the file above
        
        4. **Click Transcribe** to convert speech to text
        
        5. **Then analyze** your speech for improvements!
        
        ---
        
        **📝 Note:** For best results:
        - Speak clearly and at normal pace
        - Avoid background noise
        - Use MP3 or WAV format
        - Keep recordings under 5 minutes
        """)


def render_text_input():
    """Render text input section"""
    st.subheader("📝 Text Input")

    text_input = st.text_area(
        "Enter or paste your speech:",
        value=st.session_state.transcript if not st.session_state.get("audio_transcribed") else st.session_state.transcript,
        height=150,
        placeholder="Type your speech here to analyze and rewrite as a professional TEDX speaker..."
    )

    if text_input != st.session_state.transcript:
        st.session_state.transcript = text_input
        st.session_state.audio_transcribed = False

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
        st.session_state.audio_transcribed = False
        st.rerun()


def render_camera_input():
    """Render camera/pose input section"""
    st.subheader("📸 Camera / Pose Analysis")

    tab1, tab2 = st.tabs(["📁 Upload Image/Video", "ℹ️ About Pose Analysis"])

    with tab1:
        st.markdown("**Upload image or video to analyze your body language**")
        pose_file = st.file_uploader("Choose file", type=["jpg", "jpeg", "png", "mp4", "avi", "mov"])

        if pose_file:
            if st.button("🔄 Analyze Pose", type="primary"):
                with st.spinner("Analyzing pose..."):
                    try:
                        result = client.analyze_pose(pose_file)
                        if result.get("detected"):
                            display_pose_results(result)
                        else:
                            st.warning(result.get("message", "No person detected"))
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    with tab2:
        st.markdown("""
        **📸 What we analyze:**
        
        - **Posture** - Are you standing/sitting straight?
        - **Hand Gestures** - Are your hand movements natural?
        - **Arm Position** - Are your arms open or crossed?
        - **Shoulder Balance** - Are shoulders level?
        - **Confidence Level** - High, medium, or low?
        
        ---
        
        **💡 Tips for best results:**
        - Use good lighting
        - Show your upper body in the frame
        - Take a photo while practicing speaking
        - Upload a video clip of your presentation practice
        """)


def display_pose_results(result: dict):
    """Display pose analysis results"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Posture", f"{result.get('posture_score', 0)}%")

    with col2:
        st.metric("Shoulder Balance", f"{result.get('shoulder_balance', 0)}%")

    with col3:
        st.metric("Hand Gesture", result.get('hand_gesture', 'N/A').replace('_', ' ').title())

    with col4:
        st.metric("Confidence", result.get('confidence_level', 'N/A').upper())

    st.markdown("**💡 Suggestions:**")
    for suggestion in result.get("suggestions", []):
        st.write(f"- {suggestion}")


def analyze_speech():
    """Analyze speech"""
    with st.spinner("Analyzing..."):
        try:
            result = client.analyze(st.session_state.transcript)
            st.session_state.analysis = result
        except Exception as e:
            st.error(f"Error: {str(e)}")


def rewrite_speech():
    """Rewrite speech"""
    with st.spinner("Generating TEDX-style rewrite..."):
        try:
            result = client.rewrite(st.session_state.transcript, "tedx")
            st.session_state.rewritten = result
        except Exception as e:
            st.error(f"Error: {str(e)}")


def complete_analysis():
    """Complete analysis"""
    with st.spinner("Performing complete analysis..."):
        try:
            result = client.complete_analysis(st.session_state.transcript)
            st.session_state.analysis = result
            st.session_state.rewritten = {"rewritten": result.get("rewritten", ""), "source": "llm"}
        except Exception as e:
            st.error(f"Error: {str(e)}")


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


def render_nlp_results(analysis: dict):
    """Render NLP results"""
    st.subheader("📊 Analysis Results")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Overall", f"{analysis.get('overall_score', 0)}/100")

    with col2:
        grammar = analysis.get("grammar", {})
        st.metric("Grammar Errors", grammar.get("error_count", 0))

    with col3:
        filler = analysis.get("filler", {})
        st.metric("Filler %", f"{filler.get('effective_filler_ratio', filler.get('filler_ratio', 0))}%")

    with col4:
        conf = analysis.get("confidence", {})
        st.metric("Confidence", f"{conf.get('confidence_score', 0):.0f}/100")

    with col5:
        vocab = analysis.get("vocabulary", {})
        st.metric("Vocabulary", f"{vocab.get('vocabulary_score', 0):.0f}/100")


def render_complete_results(result: dict):
    """Render complete results"""
    st.subheader("📊 Complete Analysis Results")

    scores = result.get("scores", {})
    nlp = result.get("nlp_analysis", {})
    tedx = result.get("tedx_analysis", {})

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Overall", f"{scores.get('overall_score', 0):.1f}/100", scores.get('grade', 'N/A'))

    with col2:
        filler = nlp.get('filler', {})
        ratio = filler.get('effective_filler_ratio', filler.get('filler_ratio', 0))
        count = filler.get('effective_filler_count', filler.get('filler_count', 0))
        st.metric("Fillers", f"{ratio}%", f"{count} words")

    with col3:
        conf = nlp.get('confidence', {})
        st.metric("Confidence", f"{conf.get('confidence_score', 0):.0f}/100")

    with col4:
        st.metric("TEDX", f"{tedx.get('score', 0):.1f}/100")

    with col5:
        vocab = nlp.get('vocabulary', {})
        st.metric("Vocabulary", f"{vocab.get('vocabulary_score', 0):.0f}/100")

    with st.expander("📋 Full Details"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**NLP Analysis:**")
            filler = nlp.get('filler', {})
            st.write(f"- Filler words: {filler.get('filler_types', {})}")
            
            conf = nlp.get('confidence', {})
            st.write(f"- Confidence: {conf.get('assessment', 'N/A')}")
            
            vocab = nlp.get('vocabulary', {})
            st.write(f"- Vocabulary quality: {vocab.get('quality', 'N/A')}")

        with col2:
            st.markdown("**TEDX Analysis:**")
            st.write(f"- Story: {tedx.get('story_score', 0):.1f}")
            st.write(f"- Persuasion: {tedx.get('persuasion_score', 0):.1f}")
            st.write(f"- Rhythm: {tedx.get('rhythm_score', 0):.1f}")
            st.write(f"- Structure: {tedx.get('structure_score', 0):.1f}")


def render_rewrite():
    """Render rewrite"""
    if not st.session_state.rewritten:
        return

    st.subheader("✍️ Professional TEDX Rewrite")

    rewritten = st.session_state.rewritten.get("rewritten", "")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Your Original Speech:**")
        orig = st.session_state.transcript
        st.info(orig[:300] + "..." if len(orig) > 300 else orig)

    with col2:
        st.markdown("**TEDX-Style Rewrite:**")
        st.success(rewritten[:300] + "..." if len(rewritten) > 300 else rewritten)


def main():
    init_session_state()
    render_header()
    render_sidebar()

    st.markdown("## 📥 Choose Input Method")
    input_method = st.radio(
        "Select:",
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


if __name__ == "__main__":
    main()