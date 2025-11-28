# Speech Processing Backend

Python FastAPI backend for speech-to-text processing with transcription, diarization, and translation capabilities.

## Features

- **Speech-to-Text**: Using faster-whisper (optimized Whisper implementation)
- **Speaker Diarization**: Using pyannote.audio (optional, requires HuggingFace token)
- **Translation**: Using NLLB-200 (optional)
- **Async Processing**: Job queue system for handling long-running tasks
- **RESTful API**: FastAPI with automatic OpenAPI documentation

## Requirements

- Python 3.10+
- uv (Python package manager)
- ffmpeg (for audio processing)
- CUDA/ROCM (optional, for GPU acceleration)

## Installation

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### 2. Install Dependencies

```bash
cd backend

# Install core dependencies (automatically creates venv)
uv sync

# Or install with optional features
uv sync --extra dev                    # Development tools (pytest, black, mypy, etc.)
uv sync --extra diarization           # Speaker diarization (pyannote.audio)
uv sync --extra translation           # Translation support (transformers, NLLB)
uv sync --all-extras                  # Install everything
```

**Note**: We're using **faster-whisper** (optimized CTranslate2 implementation) which is ~4x faster than the original OpenAI Whisper while maintaining the same accuracy.

#### Why faster-whisper over WhisperX?

**Current Implementation: faster-whisper**
- ✅ Simpler setup (no additional dependencies)
- ✅ ~4x faster than original Whisper
- ✅ Same accuracy as OpenAI Whisper
- ✅ Lower memory usage
- ✅ Word-level timestamps supported
- ✅ Production-ready and stable

**WhisperX Alternative** (not currently implemented)
- More accurate word-level timestamps
- Integrated speaker diarization
- Better alignment for certain languages
- Requires additional models and more complex setup

**Recommendation**: Start with faster-whisper (current implementation). If you need more precise word-level timestamps or integrated diarization, WhisperX can be added later as an alternative transcription backend.

### 3. Install ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env and configure settings
```

### 5. Initialize Database

```bash
uv run python scripts/setup_db.py
```

### 6. Download Whisper Models (Optional)

```bash
# Download specific model
uv run python scripts/download_models.py --models base

# Download multiple models
uv run python scripts/download_models.py --models tiny base small

# Download all models
uv run python scripts/download_models.py --models all
```

Models will be downloaded automatically on first use if not pre-downloaded.

## Usage

### Start Development Server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or using the main module:

```bash
uv run python -m app.main
```

### API Documentation

Once the server is running, access:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

### Example API Usage

**Upload and transcribe a file:**

```bash
curl -X POST "http://localhost:8000/api/v1/transcribe/file" \
  -F "file=@audio.mp3" \
  -F "language=en" \
  -F "model_size=base"
```

**Check job status:**

```bash
curl "http://localhost:8000/api/v1/transcribe/job/{job_id}"
```

## Configuration

Key environment variables in `.env`:

```env
# Model Settings
WHISPER_MODEL_SIZE=base        # tiny, base, small, medium, large
WHISPER_DEVICE=cpu             # cpu, cuda, mps (Apple Silicon)
WHISPER_COMPUTE_TYPE=int8      # int8 (CPU), float16 (GPU)

# Storage
UPLOAD_DIR=./storage/uploads
MAX_UPLOAD_SIZE=500            # MB

# Features
ENABLE_DIARIZATION=false       # Requires PYANNOTE_HF_TOKEN
ENABLE_TRANSLATION=false       # Requires translation models
```

## Model Sizes

| Model | Parameters | RAM Required | Speed (CPU) |
|-------|------------|--------------|-------------|
| tiny  | 39M        | ~1 GB        | Very Fast   |
| base  | 74M        | ~1 GB        | Fast        |
| small | 244M       | ~2 GB        | Medium      |
| medium| 769M       | ~5 GB        | Slow        |
| large | 1550M      | ~10 GB       | Very Slow   |

Recommendations:
- **Development**: `tiny` or `base` for fast iteration
- **Production (CPU)**: `base` or `small` for balanced performance
- **Production (GPU)**: `medium` or `large` for best accuracy

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Type checking
mypy app/

# Linting
pylint app/
```

### Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Core utilities (config, logging, errors)
│   ├── models/          # Pydantic models
│   ├── schemas/         # Database schemas
│   ├── services/        # Business logic
│   └── utils/           # Helper functions
├── models/              # Downloaded ML models
├── storage/             # File storage
├── scripts/             # Utility scripts
└── tests/               # Unit tests
```

## Troubleshooting

### GPU Not Detected

```bash
# Check PyTorch CUDA support
python -c "import torch; print(torch.cuda.is_available())"

# For Apple Silicon
python -c "import torch; print(torch.backends.mps.is_available())"
```

If False, reinstall PyTorch with GPU support from https://pytorch.org/

### Out of Memory

- Use a smaller model (`tiny` or `base`)
- Reduce `MAX_CONCURRENT_JOBS` in `.env`
- Use `int8` compute type for CPU
- Process shorter audio files

### Audio Format Not Supported

Ensure ffmpeg is installed and accessible in PATH:

```bash
ffmpeg -version
```

## License

[Your License Here]
