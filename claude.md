# Speech Processing Application - Project Specification

## Project Overview

A universal speech-to-text application with speaker diarization and translation capabilities, designed to work across desktop platforms (macOS, Linux, Windows) with future mobile support. The application uses a client-server architecture where heavy ML processing occurs on a backend server while lightweight clients handle UI and audio capture.

### Core Capabilities
1. **Speech-to-Text (STT)**: Transcribe audio in 100+ languages with high accuracy
2. **Speaker Diarization**: Identify and label different speakers in audio
3. **Translation**: Translate transcribed text between languages
4. **Multi-platform**: Desktop (Mac/Linux/Windows) initially, mobile (iOS/Android) later
5. **Flexible Input**: Real-time audio capture or file upload processing
6. **Local Server**: Process audio files on a local server for privacy and performance

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│            Desktop Client (Tauri)                │
│  ┌──────────────────────────────────────────┐  │
│  │   UI Layer (React/Svelte + TypeScript)   │  │
│  │  - Audio capture/file selection          │  │
│  │  - Results display                        │  │
│  │  - Settings management                    │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │   Native Layer (Rust/Tauri)              │  │
│  │  - System integration                     │  │
│  │  - File dialogs                           │  │
│  │  - Audio device access                    │  │
│  └──────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────┘
                  │ HTTP/WebSocket (REST API)
                  │
┌─────────────────▼───────────────────────────────┐
│         Backend Server (Python/FastAPI)         │
│  ┌──────────────────────────────────────────┐  │
│  │   API Layer                               │  │
│  │  - REST endpoints                         │  │
│  │  - WebSocket streaming                    │  │
│  │  - Job queue management                   │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │   Processing Services                     │  │
│  │  - STT (faster-whisper/WhisperX)         │  │
│  │  - Diarization (pyannote.audio)          │  │
│  │  - Translation (NLLB/SeamlessM4T)        │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │   Storage Layer                           │  │
│  │  - File storage (local/MinIO)            │  │
│  │  - Job metadata (SQLite/PostgreSQL)      │  │
│  │  - Results cache                          │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Design Decisions

**Why Tauri over Electron:**
- 600KB vs 100MB+ bundle size
- Native OS webviews (WebKit on macOS, WebView2 on Windows, WebKitGTK on Linux)
- Better performance and lower memory footprint
- Rust-based with excellent security model
- Still uses standard web technologies for UI (React, Svelte, Vue)

**Why Python Backend:**
- Best ecosystem for ML/AI libraries
- faster-whisper, pyannote.audio, NLLB all Python-native
- FastAPI provides excellent async performance
- Easy to iterate and modify models
- Can run locally or on remote server without code changes

**Why Client-Server Architecture:**
- Heavy ML processing centralized
- Clients stay lightweight and responsive
- Easy to scale horizontally if needed
- Same backend serves desktop and future mobile clients
- Enables offline capability with local server

---

## Technology Stack

### Backend (Python 3.10+)

**Core Framework:**
- **FastAPI** (0.104+): Modern async web framework
- **Uvicorn** (0.24+): ASGI server
- **Pydantic** (2.5+): Data validation

**ML/AI Libraries:**
- **faster-whisper** (1.0+): Optimized Whisper implementation using CTranslate2
  - Alternative: **WhisperX** if word-level timestamps + integrated diarization needed
- **pyannote.audio** (3.1+): State-of-the-art speaker diarization
- **torch** (2.1+): PyTorch for model inference
- **transformers** (4.35+): HuggingFace transformers for translation models
- **NLLB** or **SeamlessM4T**: Translation (via transformers)

**Supporting Libraries:**
- **librosa** or **soundfile**: Audio file handling
- **pydub**: Audio format conversion
- **python-multipart**: File upload handling
- **websockets**: WebSocket support for streaming
- **celery** (optional): Async job queue for batch processing
- **redis** (optional): Job queue backend

**Storage:**
- **SQLite** (built-in): Job metadata and results (start simple)
- **PostgreSQL** (optional): Production database
- **MinIO** (optional): S3-compatible object storage for audio files

### Frontend (Tauri + Web)

**Framework:**
- **Tauri** (1.5+): Native desktop framework
- **Rust** (1.70+): Tauri backend (minimal custom code needed)

**UI Layer:**
- **React** (18+) with TypeScript OR **Svelte** (4+) with TypeScript
  - Recommendation: React for larger ecosystem, Svelte for smaller bundle
- **TypeScript** (5.0+): Type safety
- **Vite** (5.0+): Build tool and dev server

**UI Libraries (Optional):**
- **TailwindCSS** (3.3+): Utility-first CSS
- **shadcn/ui** or **DaisyUI**: Component library
- **Lucide React** or **Heroicons**: Icon library

**Audio Handling:**
- **Web Audio API**: Browser-native audio capture
- **MediaRecorder API**: Audio recording
- **Tauri File System API**: File operations

**State Management:**
- **Zustand** or **Jotai**: Lightweight state management
- **TanStack Query**: Server state management

**HTTP Client:**
- **axios** or **fetch API**: HTTP requests

---

## Project Structure

```
speech-processing-app/
├── README.md
├── claude.md                          # This file
├── .gitignore
├── docker-compose.yml                 # Optional: for containerized deployment
│
├── backend/                           # Python FastAPI backend
│   ├── README.md
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pyproject.toml                # Optional: for poetry
│   ├── .env.example
│   ├── .env
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry point
│   │   ├── config.py                 # Configuration management
│   │   ├── dependencies.py           # Dependency injection
│   │   │
│   │   ├── api/                      # API routes
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── transcription.py  # STT endpoints
│   │   │   │   ├── diarization.py    # Diarization endpoints
│   │   │   │   ├── translation.py    # Translation endpoints
│   │   │   │   ├── jobs.py           # Job management endpoints
│   │   │   │   └── websocket.py      # WebSocket endpoints
│   │   │   └── router.py
│   │   │
│   │   ├── services/                 # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── transcription.py      # Whisper service
│   │   │   ├── diarization.py        # Pyannote service
│   │   │   ├── translation.py        # NLLB service
│   │   │   ├── audio_processor.py    # Audio preprocessing
│   │   │   └── job_manager.py        # Job queue management
│   │   │
│   │   ├── models/                   # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── transcription.py      # STT request/response models
│   │   │   ├── diarization.py        # Diarization models
│   │   │   ├── translation.py        # Translation models
│   │   │   └── job.py                # Job models
│   │   │
│   │   ├── schemas/                  # Database schemas
│   │   │   ├── __init__.py
│   │   │   └── job.py
│   │   │
│   │   ├── core/                     # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── logging.py
│   │   │   ├── errors.py             # Custom exceptions
│   │   │   └── ml_models.py          # Model loading/management
│   │   │
│   │   └── utils/                    # Helper functions
│   │       ├── __init__.py
│   │       ├── audio.py              # Audio utilities
│   │       ├── file_handler.py       # File operations
│   │       └── validators.py         # Input validation
│   │
│   ├── models/                       # Downloaded ML models
│   │   ├── .gitkeep
│   │   └── README.md                 # Instructions for downloading models
│   │
│   ├── storage/                      # Local file storage
│   │   ├── uploads/
│   │   ├── processed/
│   │   └── cache/
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_transcription.py
│   │   ├── test_diarization.py
│   │   └── test_api.py
│   │
│   └── scripts/
│       ├── download_models.py        # Script to download ML models
│       ├── setup_db.py               # Database initialization
│       └── dev_server.py             # Development server script
│
├── frontend/                         # Tauri desktop application
│   ├── README.md
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── .env.example
│   ├── .env
│   │
│   ├── src-tauri/                    # Rust/Tauri backend
│   │   ├── Cargo.toml
│   │   ├── Cargo.lock
│   │   ├── tauri.conf.json          # Tauri configuration
│   │   ├── build.rs
│   │   ├── icons/                    # App icons
│   │   │   ├── icon.icns            # macOS
│   │   │   ├── icon.ico             # Windows
│   │   │   └── icon.png             # Linux
│   │   └── src/
│   │       ├── main.rs               # Tauri entry point
│   │       ├── commands.rs           # Tauri commands
│   │       └── audio.rs              # Audio capture (if native)
│   │
│   ├── src/                          # Web UI source
│   │   ├── main.tsx                  # Entry point
│   │   ├── App.tsx                   # Root component
│   │   ├── vite-env.d.ts
│   │   │
│   │   ├── components/               # React/Svelte components
│   │   │   ├── AudioRecorder.tsx
│   │   │   ├── FileUploader.tsx
│   │   │   ├── TranscriptionView.tsx
│   │   │   ├── DiarizationView.tsx
│   │   │   ├── TranslationPanel.tsx
│   │   │   ├── JobQueue.tsx
│   │   │   └── Settings.tsx
│   │   │
│   │   ├── services/                 # API clients
│   │   │   ├── api.ts                # API base client
│   │   │   ├── transcription.ts      # STT API calls
│   │   │   ├── diarization.ts        # Diarization API calls
│   │   │   ├── translation.ts        # Translation API calls
│   │   │   └── websocket.ts          # WebSocket client
│   │   │
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── useAudioRecorder.ts
│   │   │   ├── useTranscription.ts
│   │   │   └── useWebSocket.ts
│   │   │
│   │   ├── stores/                   # State management
│   │   │   ├── audio.ts
│   │   │   ├── transcription.ts
│   │   │   └── settings.ts
│   │   │
│   │   ├── types/                    # TypeScript types
│   │   │   ├── api.ts
│   │   │   ├── audio.ts
│   │   │   └── transcription.ts
│   │   │
│   │   ├── utils/                    # Utility functions
│   │   │   ├── audio.ts
│   │   │   ├── format.ts
│   │   │   └── validation.ts
│   │   │
│   │   ├── styles/                   # Global styles
│   │   │   └── globals.css
│   │   │
│   │   └── assets/                   # Static assets
│   │       └── logo.svg
│   │
│   └── public/                       # Public assets
│       └── favicon.ico
│
├── docs/                             # Documentation
│   ├── API.md                        # API documentation
│   ├── ARCHITECTURE.md               # Architecture details
│   ├── DEPLOYMENT.md                 # Deployment guide
│   └── DEVELOPMENT.md                # Development guide
│
└── scripts/                          # Project-level scripts
    ├── setup.sh                      # Initial project setup
    └── build-all.sh                  # Build script for all platforms
```

---

## Core Components Specification

### Backend Components

#### 1. FastAPI Application (`backend/app/main.py`)

```python
# Key features:
# - CORS middleware for frontend communication
# - File upload handling
# - WebSocket support for streaming
# - Error handling middleware
# - API versioning (/api/v1/)
# - Health check endpoint
# - OpenAPI documentation at /docs

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Speech Processing API",
    description="STT, Diarization, and Translation services",
    version="1.0.0"
)

# CORS configuration - allow Tauri app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "http://localhost:1420"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. Transcription Service (`backend/app/services/transcription.py`)

**Responsibilities:**
- Load and manage Whisper models
- Handle audio file transcription
- Stream real-time transcription
- Return timestamps and confidence scores
- Support multiple languages
- Handle model switching (tiny, base, small, medium, large)

**Key Methods:**
```python
class TranscriptionService:
    def __init__(self, model_size: str = "base"):
        """Initialize with faster-whisper model"""
        
    async def transcribe_file(
        self, 
        audio_path: str, 
        language: Optional[str] = None
    ) -> TranscriptionResult:
        """Transcribe audio file"""
        
    async def transcribe_stream(
        self, 
        audio_chunk: bytes
    ) -> AsyncGenerator[TranscriptionSegment, None]:
        """Stream transcription for real-time audio"""
        
    def get_supported_languages(self) -> List[str]:
        """Return list of supported languages"""
```

**Implementation Notes:**
- Use `faster-whisper` for optimal performance
- Support compute_type: int8, float16, float32 (int8 for CPU, float16 for GPU)
- Enable VAD filter to remove silence
- Return word-level timestamps when available
- Handle long audio files with chunking
- Support both file paths and audio buffers

#### 3. Diarization Service (`backend/app/services/diarization.py`)

**Responsibilities:**
- Load pyannote.audio pipeline
- Identify speaker segments
- Label speakers (Speaker 1, Speaker 2, etc.)
- Merge with transcription timestamps
- Handle speaker overlap

**Key Methods:**
```python
class DiarizationService:
    def __init__(self, hf_token: str):
        """Initialize with HuggingFace token for pyannote"""
        
    async def diarize(
        self, 
        audio_path: str,
        num_speakers: Optional[int] = None
    ) -> DiarizationResult:
        """Perform speaker diarization"""
        
    async def merge_with_transcription(
        self,
        transcription: TranscriptionResult,
        diarization: DiarizationResult
    ) -> DiarizedTranscription:
        """Merge speaker labels with transcription"""
```

**Implementation Notes:**
- Requires HuggingFace token (set in .env)
- Use pyannote/speaker-diarization-3.1 pipeline
- Support min_speakers and max_speakers parameters
- Return start_time, end_time, speaker_id for each segment
- Handle speaker overlap by splitting segments

#### 4. Translation Service (`backend/app/services/translation.py`)

**Responsibilities:**
- Load translation models (NLLB or SeamlessM4T)
- Translate transcribed text
- Support multiple language pairs
- Batch translation for efficiency

**Key Methods:**
```python
class TranslationService:
    def __init__(self, model_name: str = "facebook/nllb-200-distilled-600M"):
        """Initialize translation model"""
        
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """Translate text"""
        
    async def batch_translate(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str
    ) -> List[TranslationResult]:
        """Batch translate multiple texts"""
        
    def get_supported_language_pairs(self) -> List[Tuple[str, str]]:
        """Return supported language pairs"""
```

**Implementation Notes:**
- NLLB supports 200+ languages
- Use batch processing for efficiency
- Cache model in memory after first load
- Support automatic language detection for source
- Handle special characters and formatting

#### 5. Audio Processor (`backend/app/services/audio_processor.py`)

**Responsibilities:**
- Audio format conversion
- Resampling to 16kHz (Whisper requirement)
- Audio validation
- Silence removal
- Audio chunking for streaming

**Key Methods:**
```python
class AudioProcessor:
    @staticmethod
    async def convert_to_wav(input_path: str) -> str:
        """Convert audio to WAV format"""
        
    @staticmethod
    async def resample(audio_path: str, target_sr: int = 16000) -> str:
        """Resample audio to target sample rate"""
        
    @staticmethod
    async def validate_audio(audio_path: str) -> bool:
        """Validate audio file"""
        
    @staticmethod
    async def chunk_audio(
        audio_path: str, 
        chunk_duration: float = 30.0
    ) -> List[str]:
        """Split audio into chunks"""
```

### Frontend Components

#### 1. Audio Recorder Component (`frontend/src/components/AudioRecorder.tsx`)

**Features:**
- Start/stop recording
- Real-time audio visualization (waveform or level meter)
- Recording timer
- Audio format selection
- Device selection (if multiple microphones)

**State:**
```typescript
interface AudioRecorderState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
  audioLevel: number;
  selectedDevice: string;
}
```

**Key Functions:**
```typescript
const startRecording = async () => { /* ... */ };
const stopRecording = async () => { /* ... */ };
const pauseRecording = () => { /* ... */ };
const resumeRecording = () => { /* ... */ };
```

#### 2. File Uploader Component (`frontend/src/components/FileUploader.tsx`)

**Features:**
- Drag-and-drop file upload
- File browser selection
- Multiple file upload support
- File validation (type, size)
- Upload progress indicator
- File preview/info

**Supported Formats:**
- WAV, MP3, M4A, FLAC, OGG, AAC, WMA
- Video formats with audio: MP4, MOV, AVI, MKV

#### 3. Transcription View Component (`frontend/src/components/TranscriptionView.tsx`)

**Features:**
- Display transcription results
- Word-level highlighting
- Timestamp display
- Confidence score visualization
- Edit transcription (optional)
- Export results (TXT, SRT, VTT, JSON)
- Search within transcription

**Data Structure:**
```typescript
interface TranscriptionSegment {
  id: string;
  text: string;
  startTime: number;
  endTime: number;
  confidence: number;
  speaker?: string;
  words?: Word[];
}

interface Word {
  text: string;
  startTime: number;
  endTime: number;
  confidence: number;
}
```

#### 4. Diarization View Component (`frontend/src/components/DiarizationView.tsx`)

**Features:**
- Speaker timeline visualization
- Speaker color coding
- Speaker renaming (Speaker 1 → John Doe)
- Filter by speaker
- Speaker statistics (speaking time, word count)

#### 5. Settings Component (`frontend/src/components/Settings.tsx`)

**Settings to Include:**
- Backend server URL
- Whisper model size (tiny, base, small, medium, large)
- Default language
- Enable/disable diarization
- Number of speakers (auto or manual)
- Translation language pairs
- Audio quality settings
- Output format preferences
- Theme (light/dark)

---

## API Specification

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Transcription Endpoints

**POST /transcribe/file**
```json
Request:
- Content-Type: multipart/form-data
- Body:
  - file: audio file
  - language: string (optional, auto-detect if not provided)
  - model_size: string (optional, default: "base")
  - enable_diarization: boolean (optional, default: false)
  - num_speakers: integer (optional, for diarization)

Response: 200 OK
{
  "job_id": "uuid",
  "status": "processing",
  "message": "Transcription started"
}
```

**GET /transcribe/job/{job_id}**
```json
Response: 200 OK
{
  "job_id": "uuid",
  "status": "completed|processing|failed",
  "progress": 0-100,
  "result": {
    "text": "Full transcription text",
    "segments": [
      {
        "id": 0,
        "text": "Segment text",
        "start": 0.0,
        "end": 2.5,
        "confidence": 0.95,
        "speaker": "Speaker 1" (if diarization enabled),
        "words": [
          {
            "word": "Hello",
            "start": 0.0,
            "end": 0.5,
            "confidence": 0.98
          }
        ]
      }
    ],
    "language": "en",
    "duration": 120.5
  },
  "error": null
}
```

**WebSocket /ws/transcribe**
```json
Client → Server:
{
  "type": "start",
  "language": "en",
  "model_size": "base"
}

{
  "type": "audio_chunk",
  "data": "base64_encoded_audio"
}

{
  "type": "stop"
}

Server → Client:
{
  "type": "transcription",
  "text": "Partial transcription",
  "is_final": false,
  "timestamp": 1.5
}

{
  "type": "complete",
  "text": "Complete transcription"
}
```

#### 2. Diarization Endpoints

**POST /diarize**
```json
Request:
- Content-Type: multipart/form-data
- Body:
  - file: audio file
  - num_speakers: integer (optional)
  - min_speakers: integer (optional)
  - max_speakers: integer (optional)

Response: 200 OK
{
  "job_id": "uuid",
  "status": "processing"
}
```

**GET /diarize/job/{job_id}**
```json
Response: 200 OK
{
  "job_id": "uuid",
  "status": "completed",
  "result": {
    "speakers": [
      {
        "speaker_id": "Speaker 1",
        "segments": [
          {
            "start": 0.0,
            "end": 2.5
          }
        ],
        "total_speaking_time": 45.2
      }
    ],
    "num_speakers": 2
  }
}
```

#### 3. Translation Endpoints

**POST /translate**
```json
Request:
{
  "text": "Text to translate",
  "source_lang": "en",
  "target_lang": "es",
  "transcription_id": "uuid" (optional, for caching)
}

Response: 200 OK
{
  "translated_text": "Texto traducido",
  "source_lang": "en",
  "target_lang": "es",
  "confidence": 0.92
}
```

**POST /translate/batch**
```json
Request:
{
  "texts": ["Text 1", "Text 2", "Text 3"],
  "source_lang": "en",
  "target_lang": "es"
}

Response: 200 OK
{
  "translations": [
    {
      "original": "Text 1",
      "translated": "Texto 1",
      "confidence": 0.95
    }
  ]
}
```

#### 4. Utility Endpoints

**GET /health**
```json
Response: 200 OK
{
  "status": "healthy",
  "services": {
    "transcription": "ready",
    "diarization": "ready",
    "translation": "ready"
  },
  "version": "1.0.0"
}
```

**GET /models**
```json
Response: 200 OK
{
  "whisper_models": ["tiny", "base", "small", "medium", "large"],
  "current_model": "base",
  "supported_languages": ["en", "es", "fr", ...],
  "translation_models": ["nllb-200-distilled-600M"]
}
```

**GET /jobs**
```json
Query Parameters:
- status: completed|processing|failed
- limit: integer (default: 50)
- offset: integer (default: 0)

Response: 200 OK
{
  "jobs": [
    {
      "job_id": "uuid",
      "type": "transcription|diarization|translation",
      "status": "completed",
      "created_at": "2024-01-01T00:00:00Z",
      "completed_at": "2024-01-01T00:05:00Z"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

**DELETE /jobs/{job_id}**
```json
Response: 200 OK
{
  "message": "Job deleted successfully"
}
```

---

## Data Models

### Backend (Pydantic Models)

```python
# backend/app/models/transcription.py

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ModelSize(str, Enum):
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class Word(BaseModel):
    word: str
    start: float
    end: float
    confidence: float

class TranscriptionSegment(BaseModel):
    id: int
    text: str
    start: float
    end: float
    confidence: float
    speaker: Optional[str] = None
    words: Optional[List[Word]] = None

class TranscriptionRequest(BaseModel):
    language: Optional[str] = None
    model_size: ModelSize = ModelSize.BASE
    enable_diarization: bool = False
    num_speakers: Optional[int] = None

class TranscriptionResult(BaseModel):
    text: str
    segments: List[TranscriptionSegment]
    language: str
    duration: float

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = Field(ge=0, le=100)
    result: Optional[TranscriptionResult] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
```

### Frontend (TypeScript Types)

```typescript
// frontend/src/types/api.ts

export enum ModelSize {
  TINY = 'tiny',
  BASE = 'base',
  SMALL = 'small',
  MEDIUM = 'medium',
  LARGE = 'large',
}

export enum JobStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface Word {
  word: string;
  start: number;
  end: number;
  confidence: number;
}

export interface TranscriptionSegment {
  id: number;
  text: string;
  start: number;
  end: number;
  confidence: number;
  speaker?: string;
  words?: Word[];
}

export interface TranscriptionResult {
  text: string;
  segments: TranscriptionSegment[];
  language: string;
  duration: number;
}

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  result?: TranscriptionResult;
  error?: string;
  created_at: string;
  completed_at?: string;
}

export interface TranscriptionRequest {
  language?: string;
  model_size?: ModelSize;
  enable_diarization?: boolean;
  num_speakers?: number;
}
```

---

## Development Workflow

### Initial Setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/download_models.py  # Download Whisper and pyannote models
cp .env.example .env
# Edit .env and add HuggingFace token for pyannote
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env and set backend URL (default: http://localhost:8000)
```

### Running Development Servers

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run tauri dev  # Opens native app window with hot reload
```

### Testing

**Backend Tests:**
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

**Frontend Tests:**
```bash
cd frontend
npm run test
npm run test:coverage
```

### Building

**Backend (if containerizing):**
```bash
cd backend
docker build -t speech-processing-backend .
```

**Frontend:**
```bash
cd frontend

# macOS
npm run tauri build -- --target universal-apple-darwin

# Windows
npm run tauri build -- --target x86_64-pc-windows-msvc

# Linux
npm run tauri build -- --target x86_64-unknown-linux-gnu
```

---

## Configuration

### Backend Configuration (`backend/.env`)

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=info

# ML Models
WHISPER_MODEL_SIZE=base
WHISPER_DEVICE=cuda  # cuda, cpu, mps (Apple Silicon)
WHISPER_COMPUTE_TYPE=float16  # float16, int8, float32
PYANNOTE_HF_TOKEN=your_huggingface_token_here

# Storage
UPLOAD_DIR=./storage/uploads
PROCESSED_DIR=./storage/processed
CACHE_DIR=./storage/cache
MAX_UPLOAD_SIZE=500  # MB

# Database
DATABASE_URL=sqlite:///./storage/jobs.db
# For PostgreSQL: postgresql://user:password@localhost/dbname

# Job Queue (optional)
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

# API
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["tauri://localhost", "http://localhost:1420"]

# Features
ENABLE_TRANSLATION=true
ENABLE_DIARIZATION=true
MAX_CONCURRENT_JOBS=3
```

### Frontend Configuration (`frontend/.env`)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_MAX_FILE_SIZE=500
VITE_SUPPORTED_FORMATS=.wav,.mp3,.m4a,.flac,.ogg,.mp4,.mov
VITE_DEFAULT_MODEL_SIZE=base
VITE_ENABLE_DEV_TOOLS=true
```

### Tauri Configuration (`frontend/src-tauri/tauri.conf.json`)

```json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devPath": "http://localhost:1420",
    "distDir": "../dist"
  },
  "package": {
    "productName": "Speech Processing",
    "version": "0.1.0"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "fs": {
        "all": false,
        "readFile": true,
        "writeFile": true,
        "readDir": true,
        "createDir": true,
        "scope": ["$APPDATA/*", "$DOWNLOAD/*", "$DOCUMENT/*"]
      },
      "dialog": {
        "all": true,
        "open": true,
        "save": true
      },
      "http": {
        "all": true,
        "request": true,
        "scope": ["http://localhost:8000/*"]
      },
      "shell": {
        "all": false
      }
    },
    "bundle": {
      "active": true,
      "identifier": "com.speechprocessing.app",
      "targets": "all",
      "icon": [
        "icons/icon.icns",
        "icons/icon.ico",
        "icons/icon.png"
      ]
    },
    "security": {
      "csp": null
    },
    "windows": [
      {
        "fullscreen": false,
        "resizable": true,
        "title": "Speech Processing",
        "width": 1200,
        "height": 800,
        "minWidth": 800,
        "minHeight": 600
      }
    ]
  }
}
```

---

## Model Management

### Downloading Models

**Whisper Models:**
```python
# backend/scripts/download_models.py
from faster_whisper import WhisperModel

models = ["tiny", "base", "small", "medium", "large-v2"]
for model_size in models:
    print(f"Downloading {model_size}...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    print(f"✓ {model_size} downloaded")
```

**Pyannote Models:**
Requires HuggingFace token with access to pyannote models:
1. Create account at https://huggingface.co
2. Accept pyannote user agreement: https://huggingface.co/pyannote/speaker-diarization-3.1
3. Generate access token: https://huggingface.co/settings/tokens
4. Add to `.env`: `PYANNOTE_HF_TOKEN=your_token_here`

**Translation Models:**
```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "facebook/nllb-200-distilled-600M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
```

### Model Size Comparison

| Model | Parameters | English-only | Multilingual | Required VRAM | Relative Speed |
|-------|------------|--------------|--------------|---------------|----------------|
| tiny | 39M | ✓ | ✓ | ~1 GB | ~32x |
| base | 74M | ✓ | ✓ | ~1 GB | ~16x |
| small | 244M | ✓ | ✓ | ~2 GB | ~6x |
| medium | 769M | ✓ | ✓ | ~5 GB | ~2x |
| large | 1550M | - | ✓ | ~10 GB | 1x |

**Recommendations:**
- **Development**: tiny or base (fast iteration)
- **Production (CPU)**: base or small (good balance)
- **Production (GPU)**: medium or large (best quality)
- **Mobile/Edge**: tiny (if on-device processing)

---

## Performance Optimization

### Backend Optimizations

1. **Model Caching**: Load models once at startup, keep in memory
2. **Batch Processing**: Process multiple short audio files together
3. **Async Processing**: Use FastAPI async endpoints for I/O operations
4. **GPU Acceleration**: Use CUDA/Metal when available
5. **Audio Preprocessing**: Resample and convert formats before processing
6. **Result Caching**: Cache results for identical audio files

### Frontend Optimizations

1. **Audio Compression**: Compress audio before upload (if acceptable quality loss)
2. **Chunked Upload**: Upload large files in chunks with progress
3. **WebSocket for Streaming**: Use WebSocket for real-time transcription
4. **Virtual Scrolling**: For large transcription lists
5. **Lazy Loading**: Load job history on demand
6. **State Management**: Use efficient state management (Zustand/Jotai)

### Network Optimizations

1. **HTTP/2**: Enable HTTP/2 on FastAPI
2. **Compression**: Enable gzip compression for API responses
3. **WebSocket**: Use WebSocket for bidirectional streaming
4. **Polling**: Use exponential backoff for job status polling

---

## Error Handling

### Backend Error Handling

**Custom Exceptions:**
```python
# backend/app/core/errors.py

class SpeechProcessingException(Exception):
    """Base exception for all custom errors"""
    pass

class AudioProcessingError(SpeechProcessingException):
    """Audio file processing errors"""
    pass

class ModelLoadError(SpeechProcessingException):
    """Model loading errors"""
    pass

class TranscriptionError(SpeechProcessingException):
    """Transcription errors"""
    pass

class DiarizationError(SpeechProcessingException):
    """Diarization errors"""
    pass
```

**Error Response Format:**
```json
{
  "error": {
    "code": "TRANSCRIPTION_FAILED",
    "message": "Failed to transcribe audio",
    "details": "Audio file is corrupted or unsupported format",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Frontend Error Handling

**Error Boundary Component:**
```typescript
// Catch and display errors gracefully
<ErrorBoundary fallback={<ErrorView />}>
  <App />
</ErrorBoundary>
```

**User-Friendly Error Messages:**
- Network errors: "Unable to connect to server. Please check your connection."
- Upload errors: "File upload failed. Please try again."
- Processing errors: "Transcription failed. The audio file may be corrupted."

---

## Security Considerations

### Backend Security

1. **File Upload Validation**:
   - Validate file types (whitelist)
   - Validate file size (max 500MB default)
   - Scan for malicious content
   - Generate unique filenames (prevent path traversal)

2. **API Rate Limiting**:
   ```python
   from slowapi import Limiter
   
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/transcribe/file")
   @limiter.limit("10/minute")
   async def transcribe_file(...):
       pass
   ```

3. **CORS**: Restrict to Tauri app origins only

4. **Input Sanitization**: Validate all user inputs

5. **Secrets Management**: Use environment variables for sensitive data

### Frontend Security

1. **Tauri Security**:
   - Minimal allowlist (only needed APIs)
   - CSP (Content Security Policy)
   - Scope file system access

2. **API Communication**:
   - HTTPS in production
   - Validate server responses
   - Handle sensitive data securely

3. **User Data**:
   - Don't store sensitive audio files unnecessarily
   - Clear temporary files
   - Respect user privacy

---

## Testing Strategy

### Backend Testing

**Unit Tests:**
```python
# tests/test_transcription.py

import pytest
from app.services.transcription import TranscriptionService

@pytest.fixture
def transcription_service():
    return TranscriptionService(model_size="tiny")

def test_transcribe_file(transcription_service):
    result = transcription_service.transcribe_file("test_audio.wav")
    assert result.text != ""
    assert len(result.segments) > 0
    assert result.language == "en"

@pytest.mark.asyncio
async def test_transcribe_stream(transcription_service):
    async for segment in transcription_service.transcribe_stream(audio_chunk):
        assert segment.text != ""
```

**Integration Tests:**
```python
# tests/test_api.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_transcribe_endpoint():
    with open("test_audio.wav", "rb") as f:
        response = client.post(
            "/api/v1/transcribe/file",
            files={"file": f}
        )
    assert response.status_code == 200
    assert "job_id" in response.json()
```

### Frontend Testing

**Component Tests:**
```typescript
// tests/AudioRecorder.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import AudioRecorder from '../components/AudioRecorder';

test('starts recording when button clicked', () => {
  render(<AudioRecorder />);
  const button = screen.getByText('Start Recording');
  fireEvent.click(button);
  expect(screen.getByText('Stop Recording')).toBeInTheDocument();
});
```

**API Client Tests:**
```typescript
// tests/api.test.ts

import { transcribeFile } from '../services/transcription';

test('transcribeFile returns job ID', async () => {
  const file = new File(['audio'], 'test.wav', { type: 'audio/wav' });
  const result = await transcribeFile(file);
  expect(result.job_id).toBeDefined();
});
```

---

## Deployment

### Local Server Deployment

**Option 1: Direct Python**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Option 2: Docker**
```dockerfile
# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option 3: Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/storage:/app/storage
      - ./backend/models:/app/models
    environment:
      - WHISPER_DEVICE=cuda
      - PYANNOTE_HF_TOKEN=${PYANNOTE_HF_TOKEN}
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Desktop App Distribution

**macOS:**
```bash
cd frontend
npm run tauri build -- --target universal-apple-darwin
# Output: frontend/src-tauri/target/release/bundle/macos/
# Distribute: .app bundle or .dmg
```

**Windows:**
```bash
npm run tauri build -- --target x86_64-pc-windows-msvc
# Output: frontend/src-tauri/target/release/bundle/msi/
# Distribute: .msi installer
```

**Linux:**
```bash
npm run tauri build -- --target x86_64-unknown-linux-gnu
# Output: frontend/src-tauri/target/release/bundle/
# Distribute: .deb, .AppImage, or .rpm
```

---

## Future Enhancements

### Phase 2: Mobile Apps

**Architecture:**
```
Mobile App (Flutter/React Native)
↓ HTTP/WebSocket
Backend Server (same as desktop)
```

**Key Considerations:**
- Smaller model sizes for on-device processing (whisper.cpp)
- Optimize for mobile bandwidth (audio compression)
- Background processing support
- Offline mode with sync

### Phase 3: Advanced Features

1. **Real-time Collaboration**:
   - Multiple users editing same transcription
   - WebSocket-based live updates
   - Conflict resolution

2. **Speaker Recognition**:
   - Train on known speakers
   - Automatic speaker labeling

3. **Custom Vocabulary**:
   - Add domain-specific terms
   - Improve accuracy for specialized content

4. **Audio Enhancement**:
   - Noise reduction
   - Audio normalization
   - Echo cancellation

5. **Advanced Analytics**:
   - Speaking pace analysis
   - Filler word detection
   - Sentiment analysis

6. **Export Formats**:
   - SRT, VTT, TTML subtitles
   - Word documents with speaker labels
   - Video subtitling

7. **Cloud Backup**:
   - S3/Cloud storage integration
   - Automatic backup of transcriptions

---

## Code Style and Conventions

### Python (Backend)

**Style Guide**: PEP 8
**Tools**:
- black (code formatting)
- isort (import sorting)
- pylint (linting)
- mypy (type checking)

**Example:**
```python
from typing import Optional, List
from pydantic import BaseModel

async def transcribe_audio(
    audio_path: str,
    language: Optional[str] = None,
    model_size: str = "base"
) -> TranscriptionResult:
    """
    Transcribe audio file to text.
    
    Args:
        audio_path: Path to audio file
        language: Source language code (auto-detect if None)
        model_size: Whisper model size to use
        
    Returns:
        TranscriptionResult with text and segments
        
    Raises:
        AudioProcessingError: If audio file is invalid
        TranscriptionError: If transcription fails
    """
    # Implementation
    pass
```

### TypeScript (Frontend)

**Style Guide**: Airbnb TypeScript Style Guide
**Tools**:
- eslint (linting)
- prettier (formatting)

**Example:**
```typescript
interface TranscriptionOptions {
  language?: string;
  modelSize?: ModelSize;
  enableDiarization?: boolean;
}

/**
 * Transcribe audio file using backend API
 * @param file - Audio file to transcribe
 * @param options - Transcription options
 * @returns Job response with job ID
 */
export async function transcribeFile(
  file: File,
  options: TranscriptionOptions = {}
): Promise<JobResponse> {
  // Implementation
}
```

### Git Workflow

**Branch Naming**:
- `feature/feature-name`
- `bugfix/bug-description`
- `refactor/component-name`

**Commit Messages**:
```
type(scope): subject

body

footer
```

Types: feat, fix, docs, style, refactor, test, chore

**Example:**
```
feat(transcription): add real-time streaming support

- Implement WebSocket endpoint for audio streaming
- Add client-side audio chunking
- Update UI to show partial results

Closes #123
```

---

## Dependencies

### Backend (requirements.txt)

```txt
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
websockets==12.0

# ML/AI
faster-whisper==1.0.0
pyannote.audio==3.1.0
torch==2.1.0
torchaudio==2.1.0
transformers==4.35.0

# Audio Processing
librosa==0.10.1
soundfile==0.12.1
pydub==0.25.1

# Utilities
pydantic==2.5.0
python-dotenv==1.0.0
aiofiles==23.2.1

# Storage
sqlalchemy==2.0.23
alembic==1.13.0
redis==5.0.1

# Job Queue (optional)
celery==5.3.4

# Monitoring
prometheus-client==0.19.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2

# Code Quality
black==23.12.0
isort==5.13.0
pylint==3.0.3
mypy==1.7.1
```

### Frontend (package.json)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tauri-apps/api": "^1.5.1",
    "axios": "^1.6.2",
    "zustand": "^4.4.7",
    "@tanstack/react-query": "^5.8.4"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^1.5.6",
    "@types/react": "^18.2.42",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.5",
    "eslint": "^8.55.0",
    "prettier": "^3.1.0",
    "tailwindcss": "^3.3.6"
  }
}
```

---

## Troubleshooting

### Common Issues

**1. Pyannote fails to load**
- Ensure HuggingFace token is set in .env
- Accept user agreement on HuggingFace website
- Check token has proper permissions

**2. GPU not detected**
- Install CUDA toolkit (NVIDIA) or use MPS (Apple Silicon)
- Check `torch.cuda.is_available()` or `torch.backends.mps.is_available()`
- Set `WHISPER_DEVICE=cpu` if GPU unavailable

**3. Audio format not supported**
- Install ffmpeg: `brew install ffmpeg` (macOS)
- Ensure pydub can access ffmpeg
- Convert to WAV before processing

**4. Out of memory errors**
- Use smaller model size (tiny, base, small)
- Reduce batch size
- Process audio in chunks
- Use int8 compute type for CPU

**5. Tauri build fails**
- Ensure Rust is installed: `rustup update`
- Install platform-specific dependencies
- Check tauri.conf.json for errors

---

## Performance Benchmarks (Expected)

### Transcription Speed (RTF = Real-Time Factor)

| Model | Device | RTF | Notes |
|-------|--------|-----|-------|
| tiny | CPU (M1) | 0.1 | 10x faster than real-time |
| base | CPU (M1) | 0.3 | 3x faster than real-time |
| small | CPU (M1) | 0.8 | Slightly faster |
| medium | GPU (RTX 3090) | 0.2 | 5x faster |
| large | GPU (RTX 3090) | 0.5 | 2x faster |

### Memory Requirements

| Component | RAM | VRAM (GPU) |
|-----------|-----|------------|
| tiny model | 1 GB | 1 GB |
| base model | 1 GB | 1 GB |
| small model | 2 GB | 2 GB |
| medium model | 5 GB | 5 GB |
| large model | 10 GB | 10 GB |
| pyannote | 2 GB | 2 GB |
| NLLB-200 | 4 GB | 4 GB |

---

## Contact and Support

**Project Repository**: [Add GitHub URL]
**Documentation**: [Add docs URL]
**Issue Tracker**: [Add issues URL]

---

## License

[Choose appropriate license - MIT, Apache 2.0, etc.]

---

## Acknowledgments

- **OpenAI Whisper**: Speech recognition model
- **pyannote.audio**: Speaker diarization
- **Meta NLLB**: Neural machine translation
- **faster-whisper**: Optimized Whisper implementation
- **Tauri**: Cross-platform desktop framework

---

## Version History

### v0.1.0 (Current)
- Initial project specification
- Basic transcription, diarization, translation
- Desktop support (Mac/Linux/Windows)
- File upload and real-time recording

### Planned
- v0.2.0: Mobile apps (iOS/Android)
- v0.3.0: Advanced features (speaker recognition, custom vocabulary)
- v0.4.0: Cloud integration and collaboration

---

## Development Roadmap

### Phase 1: MVP (Weeks 1-4)
- [ ] Backend API skeleton
- [ ] Transcription service (faster-whisper)
- [ ] Basic Tauri app with file upload
- [ ] Results display
- [ ] Job management

### Phase 2: Core Features (Weeks 5-8)
- [ ] Real-time recording
- [ ] Speaker diarization
- [ ] Translation service
- [ ] WebSocket streaming
- [ ] Settings management

### Phase 3: Polish (Weeks 9-12)
- [ ] UI/UX improvements
- [ ] Error handling
- [ ] Performance optimization
- [ ] Documentation
- [ ] Testing
- [ ] Multi-platform builds

### Phase 4: Mobile (Weeks 13-16)
- [ ] Mobile app (Flutter/React Native)
- [ ] Mobile-optimized UI
- [ ] Offline support
- [ ] App store deployment

---

**End of Specification**

This document should be updated as the project evolves. All contributors should familiarize themselves with this specification before making changes.
