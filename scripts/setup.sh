#!/bin/bash
#
# Speech Processing Application - One-Step Setup Script
# This script sets up both backend and frontend for development
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_header() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

print_header "Speech Processing Application Setup"

echo "Project root: $PROJECT_ROOT"
echo ""

# ============================================================
# Check Prerequisites
# ============================================================
print_header "Checking Prerequisites"

MISSING_DEPS=()

# Check for Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
else
    MISSING_DEPS+=("python3")
    print_error "Python 3 not found"
fi

# Check for uv
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>&1 | head -n1)
    print_success "uv found: $UV_VERSION"
else
    print_warning "uv not found - will attempt to install"
fi

# Check for Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
else
    MISSING_DEPS+=("node")
    print_error "Node.js not found"
fi

# Check for npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION found"
else
    MISSING_DEPS+=("npm")
    print_error "npm not found"
fi

# Check for Rust (prefer ~/.cargo/bin version from rustup)
if [ -f "$HOME/.cargo/bin/rustc" ]; then
    export PATH="$HOME/.cargo/bin:$PATH"
    RUST_VERSION=$("$HOME/.cargo/bin/rustc" --version | cut -d' ' -f2)
    print_success "Rust $RUST_VERSION found (rustup)"
elif command -v rustc &> /dev/null; then
    RUST_VERSION=$(rustc --version | cut -d' ' -f2)
    # Check if version is too old (< 1.85 for edition2024 support)
    RUST_MAJOR=$(echo "$RUST_VERSION" | cut -d'.' -f1)
    RUST_MINOR=$(echo "$RUST_VERSION" | cut -d'.' -f2)
    if [ "$RUST_MAJOR" -eq 1 ] && [ "$RUST_MINOR" -lt 85 ]; then
        print_warning "Rust $RUST_VERSION found but may be too old"
        print_warning "Run 'rustup update' to get the latest version"
    else
        print_success "Rust $RUST_VERSION found"
    fi
else
    MISSING_DEPS+=("rust")
    print_error "Rust not found"
fi

# Check for ffmpeg
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1 | cut -d' ' -f3)
    print_success "ffmpeg $FFMPEG_VERSION found"
else
    MISSING_DEPS+=("ffmpeg")
    print_error "ffmpeg not found"
fi

# Exit if critical dependencies are missing
if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo ""
    print_error "Missing required dependencies: ${MISSING_DEPS[*]}"
    echo ""
    echo "Please install the missing dependencies:"
    echo ""
    
    if [[ " ${MISSING_DEPS[*]} " =~ " python3 " ]]; then
        echo "  Python 3.10+:"
        echo "    macOS: brew install python@3.12"
        echo "    Ubuntu: sudo apt install python3"
    fi
    
    if [[ " ${MISSING_DEPS[*]} " =~ " node " ]] || [[ " ${MISSING_DEPS[*]} " =~ " npm " ]]; then
        echo "  Node.js 18+:"
        echo "    macOS: brew install node"
        echo "    Ubuntu: sudo apt install nodejs npm"
        echo "    Or use nvm: https://github.com/nvm-sh/nvm"
    fi
    
    if [[ " ${MISSING_DEPS[*]} " =~ " rust " ]]; then
        echo "  Rust 1.70+:"
        echo "    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    fi
    
    if [[ " ${MISSING_DEPS[*]} " =~ " ffmpeg " ]]; then
        echo "  ffmpeg:"
        echo "    macOS: brew install ffmpeg"
        echo "    Ubuntu: sudo apt install ffmpeg"
    fi
    
    echo ""
    exit 1
fi

# ============================================================
# Install uv if not present
# ============================================================
if ! command -v uv &> /dev/null; then
    print_header "Installing uv (Python package manager)"
    
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # Add to current session
        export PATH="$HOME/.cargo/bin:$PATH"
    else
        print_error "Please install uv manually: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
    
    if command -v uv &> /dev/null; then
        print_success "uv installed successfully"
    else
        print_error "Failed to install uv"
        exit 1
    fi
fi

# ============================================================
# Backend Setup
# ============================================================
print_header "Setting Up Backend"

cd "$PROJECT_ROOT/backend"

# Create storage directories
print_info "Creating storage directories..."
mkdir -p storage/uploads storage/processed storage/cache models
print_success "Storage directories created"

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        print_success "Created .env from .env.example"
        print_warning "Please review backend/.env and update settings as needed"
    else
        print_error ".env.example not found"
    fi
else
    print_info ".env already exists, skipping"
fi

# Install Python dependencies
print_info "Installing Python dependencies with uv..."
# Check if diarization was previously installed
if uv run python -c "import pyannote.audio" 2>/dev/null; then
    print_info "Diarization already installed, preserving with --all-extras"
    uv sync --all-extras
else
    # Check if .env has PYANNOTE_AUTH_TOKEN to decide if we should install diarization
    if grep -q "PYANNOTE_AUTH_TOKEN=.*[^[:space:]]" .env 2>/dev/null; then
        print_info "PYANNOTE_AUTH_TOKEN found, installing with diarization support"
        uv sync --extra diarization
    else
        print_info "Installing base dependencies only"
        uv sync
    fi
fi
print_success "Python dependencies installed"

# Install dev dependencies
print_info "Installing development dependencies..."
uv sync --group dev
print_success "Development dependencies installed"

# Initialize database
print_info "Initializing database..."
uv run python scripts/setup_db.py
print_success "Database initialized"

# Verify backend installation
print_info "Verifying backend installation..."
if uv run python -c "import torch; import faster_whisper; import fastapi; print('Backend OK')" 2>/dev/null; then
    print_success "Backend dependencies verified"
else
    print_warning "Some backend dependencies may have issues"
fi

# ============================================================
# Frontend Setup
# ============================================================
print_header "Setting Up Frontend"

cd "$PROJECT_ROOT/frontend"

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        print_success "Created .env from .env.example"
    else
        print_error ".env.example not found"
    fi
else
    print_info ".env already exists, skipping"
fi

# Create icons directory if it doesn't exist
if [ ! -d src-tauri/icons ]; then
    print_info "Creating icons directory..."
    mkdir -p src-tauri/icons
    
    # Create placeholder icons (simple colored squares)
    # In production, replace these with actual app icons
    print_info "Creating placeholder icons..."
    
    # Check if we have ImageMagick or can create icons
    if command -v convert &> /dev/null; then
        convert -size 32x32 xc:#3B82F6 src-tauri/icons/32x32.png
        convert -size 128x128 xc:#3B82F6 src-tauri/icons/128x128.png
        convert -size 256x256 xc:#3B82F6 src-tauri/icons/128x128@2x.png
        convert -size 512x512 xc:#3B82F6 src-tauri/icons/icon.png
        print_success "Placeholder icons created"
    else
        print_warning "ImageMagick not found - creating minimal placeholder icons"
        # Create minimal valid PNG files (1x1 blue pixel)
        # These are base64 encoded minimal PNG files
        echo "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAFklEQVR42mNkYPhfz0AFMIqBUQwMPAYAE7wBhWYxPLAAAAAASUVORK5CYII=" | base64 -d > src-tauri/icons/32x32.png 2>/dev/null || touch src-tauri/icons/32x32.png
        cp src-tauri/icons/32x32.png src-tauri/icons/128x128.png
        cp src-tauri/icons/32x32.png src-tauri/icons/128x128@2x.png
        cp src-tauri/icons/32x32.png src-tauri/icons/icon.png
        print_warning "Created minimal placeholder icons - replace with real icons for production"
    fi
    
    # Create .icns for macOS (placeholder)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [ -f src-tauri/icons/icon.png ]; then
            # Try to create icns from png
            if command -v iconutil &> /dev/null; then
                mkdir -p src-tauri/icons/icon.iconset
                cp src-tauri/icons/32x32.png src-tauri/icons/icon.iconset/icon_32x32.png
                cp src-tauri/icons/128x128.png src-tauri/icons/icon.iconset/icon_128x128.png
                iconutil -c icns src-tauri/icons/icon.iconset -o src-tauri/icons/icon.icns 2>/dev/null || touch src-tauri/icons/icon.icns
                rm -rf src-tauri/icons/icon.iconset
            else
                touch src-tauri/icons/icon.icns
            fi
        fi
    else
        touch src-tauri/icons/icon.icns
    fi
    
    # Create .ico for Windows (placeholder)
    touch src-tauri/icons/icon.ico
    
    print_success "Icons directory created"
else
    print_info "Icons directory already exists"
fi

# Install npm dependencies
print_info "Installing npm dependencies..."
npm install
print_success "npm dependencies installed"

# Verify frontend installation
print_info "Verifying frontend installation..."
if npm run build 2>/dev/null; then
    print_success "Frontend build verified"
else
    print_warning "Frontend build had issues - this may be normal for first run"
fi

# ============================================================
# Summary
# ============================================================
print_header "Setup Complete!"

echo "Your Speech Processing Application is ready for development."
echo ""
echo "Next steps:"
echo ""
echo "  1. Start the backend server:"
echo "     ${BLUE}cd backend && uv run uvicorn app.main:app --reload${NC}"
echo ""
echo "  2. In a new terminal, start the frontend:"
echo "     ${BLUE}cd frontend && npm run tauri:dev${NC}"
echo ""
echo "  3. (Optional) Download Whisper models:"
echo "     ${BLUE}cd backend && uv run python scripts/download_models.py --models base${NC}"
echo ""
echo "Configuration files:"
echo "  - Backend: ${YELLOW}backend/.env${NC}"
echo "  - Frontend: ${YELLOW}frontend/.env${NC}"
echo ""
echo "API Documentation (when backend is running):"
echo "  - Swagger UI: ${BLUE}http://localhost:8000/docs${NC}"
echo "  - ReDoc: ${BLUE}http://localhost:8000/redoc${NC}"
echo ""
print_success "Happy coding!"
echo ""
