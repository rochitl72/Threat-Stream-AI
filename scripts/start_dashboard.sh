#!/bin/bash
# Start Dashboard Services

echo "🚀 Starting ThreatStream AI Dashboard Services..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start dashboard backend
echo "📡 Starting Dashboard Backend (FastAPI)..."
python -m src.dashboard.api.server &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if dashboard directory exists
if [ ! -d "dashboard" ]; then
    echo "❌ Dashboard directory not found!"
    exit 1
fi

# Start dashboard frontend
echo "🎨 Starting Dashboard Frontend (Next.js)..."
cd dashboard

if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ Dashboard services started!"
echo ""
echo "📊 Backend API: http://localhost:8000"
echo "🎨 Frontend Dashboard: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait

