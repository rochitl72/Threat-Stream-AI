#!/bin/bash
# Start all ThreatStream AI services

cd /Users/rochitlen/Downloads/animus

echo "🚀 Starting ThreatStream AI Services..."
echo ""

# Kill existing processes
pkill -f "uvicorn\|dashboard\|next\|threat_consumer" 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
sleep 2

# Activate virtual environment
source venv/bin/activate

# Start Threat Consumer
echo "📡 Starting Threat Consumer..."
python -m src.consumers.threat_consumer > logs/threat_consumer.log 2>&1 &
THREAT_PID=$!
echo "  ✅ Threat Consumer (PID: $THREAT_PID)"
sleep 2

# Start Backend API
echo "🔧 Starting Backend API..."
python -m uvicorn src.dashboard.api.server:app --host 127.0.0.1 --port 8000 > logs/dashboard_backend.log 2>&1 &
BACKEND_PID=$!
echo "  ✅ Backend API (PID: $BACKEND_PID)"
sleep 5

# Start Frontend
echo "🎨 Starting Frontend..."
cd dashboard
npm run dev > ../logs/dashboard_frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "  ✅ Frontend (PID: $FRONTEND_PID)"
sleep 5

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ All services started!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🌐 Access URLs:"
echo "  Dashboard:    http://localhost:3000"
echo "  Backend API:  http://localhost:8000"
echo "  Health Check: http://localhost:8000/api/health"
echo ""
echo "📝 Log Files:"
echo "  Backend:   logs/dashboard_backend.log"
echo "  Frontend:  logs/dashboard_frontend.log"
echo "  Consumer:  logs/threat_consumer.log"
echo ""
echo "🛑 To stop all services:"
echo "  pkill -f 'uvicorn|next|threat_consumer'"
echo ""
echo "⏳ Waiting 10 seconds for services to fully start..."
sleep 10

echo ""
echo "🔍 Final Status Check:"
echo "──────────────────────"
lsof -i:8000 2>/dev/null | grep LISTEN && echo "✅ Backend listening on port 8000" || echo "⚠️  Backend may still be starting..."
lsof -i:3000 2>/dev/null | grep LISTEN && echo "✅ Frontend listening on port 3000" || echo "⚠️  Frontend may still be starting..."

echo ""
echo "🧪 Testing Backend:"
curl -s -m 3 http://localhost:8000/api/health 2>&1 | head -3 && echo "✅ Backend is responding!" || echo "⚠️  Backend not responding yet (may need a few more seconds)"

echo ""
echo "✅ Ready for testing!"
echo ""
echo "💡 If backend doesn't respond, check: tail -f logs/dashboard_backend.log"

