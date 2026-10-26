#!/usr/bin/env bash
# ============================================================
# SteadyVox — Localhost Demo Launcher
# Usage: bash start-localhost.sh
# ============================================================
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_LOG="/tmp/steadyvox_backend.log"
FRONTEND_LOG="/tmp/steadyvox_frontend.log"

echo ""
echo "┌─────────────────────────────────────────────┐"
echo "│         SteadyVox — Localhost Demo          │"
echo "│   AI-Powered Voice Analysis for PD Research │"
echo "└─────────────────────────────────────────────┘"
echo ""

# Kill any existing instances
pkill -f "uvicorn backend.app.main" 2>/dev/null || true
pkill -f "vite --host" 2>/dev/null || true
sleep 1

# ── 1. Start Backend ──────────────────────────────
echo "▶  Starting backend (FastAPI + SQLite)..."
cd "$PROJECT_DIR"
source backend/.venv/bin/activate
PYTHONPATH="$PROJECT_DIR" nohup python -m uvicorn backend.app.main:app \
    --host 0.0.0.0 --port 8000 \
    > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo -n "   Waiting for backend..."
for i in {1..20}; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo " ✓ Ready"
        break
    fi
    echo -n "."
    sleep 1
done

# ── 2. Start Frontend ─────────────────────────────
echo "▶  Starting frontend (React + Vite)..."
cd "$PROJECT_DIR/frontend"
nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# Wait for frontend to be ready
echo -n "   Waiting for frontend..."
for i in {1..20}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo " ✓ Ready"
        break
    fi
    echo -n "."
    sleep 1
done

# ── 3. Summary ────────────────────────────────────
echo ""
echo "┌─────────────────────────────────────────────┐"
echo "│               ✅ READY!                     │"
echo "│                                             │"
echo "│  🌐 Open in browser:                        │"
echo "│     http://localhost:5173                   │"
echo "│                                             │"
echo "│  📡 Backend API docs:                       │"
echo "│     http://localhost:8000/docs              │"
echo "│                                             │"
echo "│  📝 Logs:                                   │"
echo "│     Backend: $BACKEND_LOG"
echo "│     Frontend: $FRONTEND_LOG"
echo "│                                             │"
echo "│  ⚠️  Research tool only — not a diagnosis   │"
echo "└─────────────────────────────────────────────┘"
echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

# Keep script running and show logs
trap "echo ''; echo 'Stopping SteadyVox...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
