#!/bin/bash

# Quick restart script - doesn't reinstall dependencies
# Usage: ./scripts/restart.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

print_header "Quick Restart - Speech Processing Application"

# Kill existing services
print_info "Stopping existing services..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "tauri dev" 2>/dev/null || true
pkill -f "npm run tauri:dev" 2>/dev/null || true

# Wait for processes to stop
sleep 2

# Kill any lingering port users
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:1420 | xargs kill -9 2>/dev/null || true

print_success "Services stopped"

# Start backend
print_info "Starting backend server..."
cd backend
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

print_success "Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
print_info "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start"
        exit 1
    fi
    sleep 1
done

# Start frontend
print_info "Starting frontend..."
cd frontend
npm run tauri:dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

print_success "Frontend started (PID: $FRONTEND_PID)"

print_header "Restart Complete!"
echo ""
echo -e "${GREEN}Application is running:${NC}"
echo -e "  Backend API: ${BLUE}http://localhost:8000${NC}"
echo -e "  API Docs:    ${BLUE}http://localhost:8000/docs${NC}"
echo -e "  Frontend:    ${BLUE}Tauri app window${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for interrupt
trap 'print_info "Shutting down..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

# Keep script running
wait
