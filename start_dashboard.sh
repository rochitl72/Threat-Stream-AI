#!/bin/bash

# ThreatStream AI - Complete Dashboard Startup Script
# Runs all services in background

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting ThreatStream AI Dashboard..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# PID file
PID_FILE="$SCRIPT_DIR/.dashboard_pids"

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down all services...${NC}"
    
    if [ -f "$PID_FILE" ]; then
        while read pid; do
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
    
    # Kill any remaining processes
    pkill -f "src.consumers.threat_consumer" 2>/dev/null || true
    pkill -f "src.dashboard.api.server" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true
    
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Trap signals
trap cleanup SIGINT SIGTERM EXIT

# Check virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    pip install -q -r requirements.txt
fi

# Check dashboard directory
if [ ! -d "dashboard" ]; then
    echo -e "${RED}❌ Dashboard directory not found!${NC}"
    exit 1
fi

# Install frontend dependencies if needed
if [ ! -d "dashboard/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    cd dashboard
    npm install --silent
    cd ..
fi

# Clear PID file
> "$PID_FILE"

# Start Threat Consumer
echo -e "${GREEN}📡 Starting Threat Consumer...${NC}"
python -m src.consumers.threat_consumer > logs/threat_consumer.log 2>&1 &
THREAT_PID=$!
echo "$THREAT_PID" >> "$PID_FILE"
echo "  ✅ Threat Consumer (PID: $THREAT_PID)"

# Wait a bit for consumer to initialize
sleep 2

# Start Dashboard Backend
echo -e "${GREEN}🔧 Starting Dashboard Backend (FastAPI)...${NC}"
python -m src.dashboard.api.server > logs/dashboard_backend.log 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" >> "$PID_FILE"
echo "  ✅ Backend API (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 3

# Start Dashboard Frontend
echo -e "${GREEN}🎨 Starting Dashboard Frontend (Next.js)...${NC}"
cd dashboard
npm run dev > ../logs/dashboard_frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "$FRONTEND_PID" >> "$PID_FILE"
echo "  ✅ Frontend Dashboard (PID: $FRONTEND_PID)"

# Wait a bit for frontend to start
sleep 5

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ All services started successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📊 Services:${NC}"
echo "  • Threat Consumer: Running (PID: $THREAT_PID)"
echo "  • Backend API:     http://localhost:8000 (PID: $BACKEND_PID)"
echo "  • Frontend:        http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo "  • Threat Consumer: logs/threat_consumer.log"
echo "  • Backend:          logs/dashboard_backend.log"
echo "  • Frontend:         logs/dashboard_frontend.log"
echo ""
echo -e "${YELLOW}💡 To generate test data, run in another terminal:${NC}"
echo "   python scripts/generate_demo_data.py --all --duration 300"
echo ""
echo -e "${YELLOW}🛑 Press Ctrl+C to stop all services${NC}"
echo ""

# Keep script running and monitor processes
while true; do
    sleep 5
    
    # Check if processes are still running
    if ! kill -0 "$THREAT_PID" 2>/dev/null; then
        echo -e "${RED}⚠️  Threat Consumer stopped!${NC}"
    fi
    
    if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "${RED}⚠️  Backend stopped!${NC}"
    fi
    
    if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "${RED}⚠️  Frontend stopped!${NC}"
    fi
done

