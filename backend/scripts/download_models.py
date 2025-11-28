#!/usr/bin/env python3
"""Script to download Whisper models."""
import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from faster_whisper import WhisperModel

AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]


def download_model(model_size: str, device: str = "cpu") -> None:
    """Download a Whisper model.

    Args:
        model_size: Model size to download
        device: Device type (cpu, cuda, auto)
    """
    print(f"\n{'='*60}")
    print(f"Downloading Whisper model: {model_size}")
    print(f"{'='*60}\n")

    try:
        # Initialize model (downloads if not present)
        model = WhisperModel(
            model_size,
            device=device,
            compute_type="int8" if device == "cpu" else "float16",
            download_root="./models",
        )

        print(f"✓ Successfully downloaded/verified {model_size} model")
        return model

    except Exception as e:
        print(f"✗ Failed to download {model_size}: {str(e)}")
        raise


def main() -> None:
    """Main function to download models."""
    parser = argparse.ArgumentParser(
        description="Download Whisper models for speech-to-text"
    )
    parser.add_argument(
        "--models",
        nargs="+",
        choices=AVAILABLE_MODELS + ["all"],
        default=["base"],
        help="Model sizes to download (default: base)",
    )
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda", "auto"],
        default="cpu",
        help="Device type for model optimization (default: cpu)",
    )

    args = parser.parse_args()

    # Determine which models to download
    if "all" in args.models:
        models_to_download = AVAILABLE_MODELS
    else:
        models_to_download = args.models

    print("\n" + "="*60)
    print("Whisper Model Downloader")
    print("="*60)
    print(f"\nModels to download: {', '.join(models_to_download)}")
    print(f"Device: {args.device}")
    print(f"Download location: ./models")

    # Create models directory
    models_dir = Path("./models")
    models_dir.mkdir(exist_ok=True)

    # Download each model
    successful = []
    failed = []

    for model_size in models_to_download:
        try:
            download_model(model_size, args.device)
            successful.append(model_size)
        except Exception:
            failed.append(model_size)

    # Summary
    print("\n" + "="*60)
    print("Download Summary")
    print("="*60)
    print(f"\nSuccessful: {len(successful)}")
    for model in successful:
        print(f"  ✓ {model}")

    if failed:
        print(f"\nFailed: {len(failed)}")
        for model in failed:
            print(f"  ✗ {model}")

    print("\n" + "="*60)
    print("\nNote: Models are cached by faster-whisper.")
    print("Subsequent loads will be much faster.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
