# ML Models Directory

This directory will contain downloaded machine learning models.

## Whisper Models

Run the download script to fetch Whisper models:

```bash
python scripts/download_models.py
```

Available model sizes:
- **tiny**: 39M parameters (~1GB RAM)
- **base**: 74M parameters (~1GB RAM)
- **small**: 244M parameters (~2GB RAM)
- **medium**: 769M parameters (~5GB RAM)
- **large**: 1550M parameters (~10GB RAM)

Models will be automatically downloaded by faster-whisper on first use if not present.

## Pyannote Models (Optional)

For speaker diarization, you'll need:
1. HuggingFace account
2. Accept terms at: https://huggingface.co/pyannote/speaker-diarization-3.1
3. Create access token: https://huggingface.co/settings/tokens
4. Add to `.env`: `PYANNOTE_HF_TOKEN=your_token_here`

## Translation Models (Optional)

NLLB models will be downloaded automatically from HuggingFace when first used.
