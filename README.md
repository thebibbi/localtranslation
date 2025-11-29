# Speech Processing Application

A universal speech-to-text application with speaker diarization and translation capabilities, designed to work across desktop platforms (macOS, Linux, Windows).

## Features

- **Speech-to-Text**: Transcribe audio in 100+ languages with high accuracy using OpenAI Whisper
- **Multi-format Support**: WAV, MP3, M4A, FLAC, OGG, MP4, MOV, and more
- **Multiple Model Sizes**: Choose between speed and accuracy (tiny to large)
- **Desktop Native**: Built with Tauri for a lightweight, native experience
- **User-Friendly Interface**: Simple drag-and-drop file upload
- **Export Options**: Export transcriptions as TXT, JSON, or SRT subtitle format
- **Real-time Progress**: Live updates during transcription

## Architecture

```
┌─────────────────────────────────┐
│  Desktop Client (Tauri + React) │
│  - File upload                   │
│  - Results display               │
│  - Settings management           │
└────────────┬────────────────────┘
             │ HTTP REST API
             │
┌────────────▼────────────────────┐
│  Backend Server (Python/FastAPI)│
│  - Speech-to-Text (Whisper)     │
│  - Job queue management         │
│  - Audio processing             │
└─────────────────────────────────┘
```

## Quick Start

### One-Step Setup (Recommended)

The easiest way to get started is using the automated setup script:

```bash
# Clone the repository (if you haven't already)
git clone <repository-url>
cd localtranslation

# Run the setup script
./scripts/setup.sh
```

This script will:
- Check and install prerequisites (uv, if missing)
- Set up the backend (Python dependencies, database, directories)
- Set up the frontend (npm dependencies, icons)
- Create configuration files from examples

After setup, start both services:

```bash
# Option 1: Start both services together
./scripts/start.sh

# Option 2: Start services separately (in different terminals)
# Terminal 1 - Backend:
cd backend && uv run uvicorn app.main:app --reload

# Terminal 2 - Frontend:
cd frontend && npm run tauri:dev
```

### Prerequisites

Before running the setup script, ensure you have:

- **Python 3.10+**: `python3 --version`
- **Node.js 18+**: `node --version`
- **Rust 1.70+**: `rustc --version`
- **ffmpeg**: `ffmpeg -version`

#### Installing Prerequisites

**macOS (with Homebrew):**
```bash
brew install python@3.12 node ffmpeg
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip nodejs npm ffmpeg
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

**Windows:**
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/
- Rust: https://rustup.rs/
- ffmpeg: https://ffmpeg.org/download.html

### Manual Setup

If you prefer manual setup:

#### Backend Setup

```bash
cd backend

# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies with uv (automatically creates venv)
uv sync

# Or install with optional features
uv sync --extra dev                    # Include development tools
uv sync --extra diarization           # Include speaker diarization
uv sync --extra translation           # Include translation support
uv sync --all-extras                  # Include everything

# Configure environment
cp .env.example .env
# Edit .env if needed

# Create storage directories
mkdir -p storage/uploads storage/processed storage/cache models

# Initialize database
uv run python scripts/setup_db.py

# Start server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at http://localhost:8000

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if needed (default backend URL: http://localhost:8000)

# Start development app
npm run tauri:dev
```

## Usage

1. **Start the backend server** (see Backend Setup above)
2. **Launch the desktop app** (see Frontend Setup above)
3. **Upload an audio file** by dragging and dropping or clicking to browse
4. **Select options**:
   - Model size (tiny, base, small, medium, large)
   - Language (optional, auto-detects if not specified)
5. **Click "Transcribe Audio"**
6. **Wait for processing** - progress is shown in real-time
7. **View and export results** - available in TXT, JSON, or SRT format

## Model Sizes

| Model  | Speed    | Accuracy | RAM Required | Best For                |
|--------|----------|----------|--------------|-------------------------|
| tiny   | Fastest  | Low      | ~1 GB        | Quick drafts            |
| base   | Fast     | Good     | ~1 GB        | General use (default)   |
| small  | Medium   | Better   | ~2 GB        | Balanced quality/speed  |
| medium | Slow     | High     | ~5 GB        | High accuracy (GPU rec.)|
| large  | Slowest  | Best     | ~10 GB       | Best quality (GPU req.) |

## Project Structure

```
speech-processing-app/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Config, logging, errors
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   ├── schemas/        # Database schemas
│   │   └── utils/          # Helper functions
│   ├── models/             # Downloaded ML models
│   ├── storage/            # File storage
│   ├── scripts/            # Utility scripts
│   └── tests/              # Unit tests
│
├── frontend/               # Tauri + React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API clients
│   │   ├── stores/         # State management
│   │   ├── types/          # TypeScript types
│   │   └── styles/         # CSS styles
│   └── src-tauri/          # Rust/Tauri code
│
├── docs/                   # Documentation
└── README.md               # This file
```

## Development

### Backend Development

```bash
cd backend

# Run tests
uv run pytest tests/ -v

# Code formatting
uv run black app/
uv run isort app/

# Type checking
uv run mypy app/

# Run development server with auto-reload
uv run uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Run in development mode (hot reload)
npm run tauri:dev

# Lint code
npm run lint

# Format code
npm run format

# Build for production
npm run tauri:build
```

## Building for Production

### Backend

The backend can be run directly with uv or containerized with Docker:

```bash
cd backend

# Option 1: Direct execution with uv
uv run python -m app.main

# Option 2: Production server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Option 3: Docker
docker build -t speech-processing-backend .
docker run -p 8000:8000 speech-processing-backend
```

### Frontend

Build native applications for your platform:

```bash
cd frontend

# macOS
npm run tauri:build -- --target universal-apple-darwin

# Windows
npm run tauri:build -- --target x86_64-pc-windows-msvc

# Linux
npm run tauri:build -- --target x86_64-unknown-linux-gnu
```

Built applications will be in `frontend/src-tauri/target/release/bundle/`

## API Documentation

Once the backend is running, visit:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## Troubleshooting

### Backend Issues

**GPU not detected**:
```bash
# Check PyTorch CUDA support
python -c "import torch; print(torch.cuda.is_available())"
```

**Out of memory**:
- Use a smaller model size (`tiny` or `base`)
- Reduce `MAX_CONCURRENT_JOBS` in `.env`

**ffmpeg not found**:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows: Download from https://ffmpeg.org
```

### Frontend Issues

**Backend connection failed**:
- Ensure backend is running at http://localhost:8000
- Check firewall settings
- Verify CORS settings in backend `.env`

**Build fails**:
- Ensure Rust is installed: `rustup --version`
- Update Rust: `rustup update`
- Check Node.js version: `node --version` (requires 18+)

## Future Enhancements

- [ ] Real-time audio recording and live transcription
- [ ] Speaker diarization (identify different speakers) ✅ **Implemented**
- [ ] Translation between languages
- [ ] Mobile apps (iOS/Android)
- [ ] Cloud deployment options
- [ ] Custom vocabulary and domain-specific models
- [ ] Batch processing multiple files
- [ ] Audio enhancement (noise reduction)

## Technologies Used

### Backend
- **FastAPI**: Modern async web framework
- **faster-whisper**: Optimized Whisper implementation using CTranslate2 (~4x faster than original)
- **uv**: Fast Python package and project manager (replaces pip/pip-tools/virtualenv)
- **SQLite**: Database for job tracking
- **pydub**: Audio format conversion
- **PyTorch**: ML model inference

**Note on faster-whisper**: We chose faster-whisper over WhisperX for the MVP because it's simpler to set up, has the same accuracy as OpenAI Whisper, uses less memory, and is production-ready. WhisperX can be added later if you need more precise word-level timestamps or integrated diarization.

### Performance Optimization

#### Apple Silicon (M1/M2/M3) Acceleration

The app automatically uses **Metal Performance Shaders (MPS)** on Apple Silicon for GPU acceleration:

```bash
# Configuration in .env
WHISPER_DEVICE=mps          # Use Apple Metal GPU
WHISPER_COMPUTE_TYPE=float16 # Better GPU performance
```

**Performance benefits:**
- ~2-3x faster transcription on M1/M2/M3
- Lower power consumption than CPU
- Automatic fallback to CPU if MPS unavailable

#### Model Size Performance

| Model | Speed | Accuracy | Memory | Recommended For |
|-------|-------|----------|--------|------------------|
| tiny  | ⚡ Fast | Good | ~1GB | Quick drafts, real-time |
| base  | 🚀 Fast | Better | ~1GB | Daily use (default) |
| small | 📖 Medium | Good | ~2GB | Better accuracy |
| medium| 🐢 Slow | Very Good | ~5GB | Professional use |
| large | 🐢🐢 Slowest | Best | ~10GB | Highest quality |

### Frontend
- **Tauri**: Lightweight desktop framework (Rust + WebView)
- **React**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Zustand**: Lightweight state management
- **Axios**: HTTP client

## License

[Specify your license here]

## Credits

- **OpenAI Whisper**: Speech recognition model
- **faster-whisper**: Optimized Whisper implementation
- **Tauri**: Cross-platform desktop framework

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review existing issues
- Create a new issue with detailed information

---

**Version**: 0.1.0 (MVP)
**Status**: Development