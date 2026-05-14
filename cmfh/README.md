# CMFH - Call Me For Help

**AI TEDX Speech Coach & Professional Communication Assistant**

A production-grade MVP for AI-powered communication coaching that transforms users into high-confidence TEDX-style communicators.

## Project Goal

Build a lightweight AI-powered communication coaching application that runs efficiently on low-end hardware (Intel i3, 8GB RAM, CPU-only).

## Features

- **Real-time Microphone Input** - Capture and process audio in chunks
- **Speech-to-Text** - Whisper Tiny for efficient CPU inference
- **NLP Analysis Engine** - Grammar, filler words, confidence, vocabulary
- **Professional Speech Rewrite** - Phi-3 Mini via Ollama
- **TEDX Reference System** - Style analysis and suggestions
- **Feedback Engine** - Comprehensive scoring and coaching
- **User Progress Tracking** - SQLite-based session history

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Speech-to-Text**: faster-whisper (Whisper Tiny)
- **NLP**: spaCy, regex, LanguageTool
- **LLM**: Phi-3 Mini via Ollama
- **Database**: SQLite

## Project Structure

```
cmfh/
├── app/
│   ├── audio/           # Audio recording
│   ├── stt/             # Whisper STT engine
│   ├── nlp/             # NLP analysis modules
│   ├── ai/              # LLM rewrite engine
│   ├── tedx/            # TEDX reference system
│   ├── feedback/        # Scoring & feedback
│   ├── database/        # SQLite manager
│   ├── api/             # FastAPI routes
│   └── utils/           # Utilities
├── frontend/            # Streamlit dashboard
├── data/                # Data directory
├── models/              # Model storage
├── main.py              # FastAPI entry point
└── requirements.txt     # Dependencies
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

3. Install Ollama and download Phi-3:
```bash
ollama pull phi3
```

4. Run the backend:
```bash
python main.py
```

5. In a new terminal, run the frontend:
```bash
streamlit run frontend/app.py
```

## API Endpoints

- `POST /api/transcribe` - Transcribe audio to text
- `POST /api/analyze` - Analyze text for NLP metrics
- `POST /api/rewrite` - Rewrite in professional style
- `POST /api/feedback` - Generate comprehensive feedback
- `GET /api/history` - Get session history
- `GET /api/health` - Health check

## Hardware Optimization

- Whisper Tiny model for low memory usage
- Chunk-based audio processing (10-15 seconds)
- Quantized LLM models
- Async processing
- Rule-based NLP before LLM calls
- Target: <6GB RAM usage on Intel i3

## Usage

1. Enter or speak your speech text
2. Click "Analyze" to get NLP metrics
3. Click "Rewrite" for professional TEDX-style rewrite
4. Click "Feedback" for coaching tips
5. Track progress over time

## License

MIT