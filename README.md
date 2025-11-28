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

### Prerequisites

- **Backend**: Python 3.10+, ffmpeg
- **Frontend**: Node.js 18+, Rust 1.70+

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env if needed

# Initialize database
python scripts/setup_db.py

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at http://localhost:8000

### Frontend Setup

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
pytest tests/ -v

# Code formatting
black app/
isort app/

# Type checking
mypy app/

# Run development server with auto-reload
uvicorn app.main:app --reload
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

The backend can be run directly with Python or containerized with Docker:

```bash
cd backend

# Option 1: Direct execution
python -m app.main

# Option 2: Docker
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
- [ ] Speaker diarization (identify different speakers)
- [ ] Translation between languages
- [ ] Mobile apps (iOS/Android)
- [ ] Cloud deployment options
- [ ] Custom vocabulary and domain-specific models
- [ ] Batch processing multiple files
- [ ] Audio enhancement (noise reduction)

## Technologies Used

### Backend
- **FastAPI**: Modern async web framework
- **faster-whisper**: Optimized Whisper implementation using CTranslate2
- **SQLite**: Database for job tracking
- **pydub**: Audio format conversion
- **PyTorch**: ML model inference

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