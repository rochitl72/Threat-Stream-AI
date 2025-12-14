#!/bin/bash
# Real-time log monitoring for dashboard services

cd /Users/rochitlen/Downloads/animus

echo "🔍 Monitoring Dashboard Logs (Press Ctrl+C to stop)"
echo "=================================================="
echo ""

# Function to show logs
show_logs() {
    echo "📊 Current Status:"
    echo "------------------"
    
    # Check if processes are running
    if pgrep -f "threat_consumer" > /dev/null; then
        echo "✅ Threat Consumer: Running"
    else
        echo "❌ Threat Consumer: Stopped"
    fi
    
    if pgrep -f "dashboard.api.server" > /dev/null; then
        echo "✅ Backend API: Running"
    else
        echo "❌ Backend API: Stopped"
    fi
    
    if pgrep -f "next dev" > /dev/null; then
        echo "✅ Frontend: Running"
    else
        echo "❌ Frontend: Stopped"
    fi
    
    echo ""
    echo "📝 Recent Backend Errors:"
    echo "-------------------------"
    tail -20 logs/dashboard_backend.log | grep -i "error\|exception\|traceback\|failed" || echo "No errors found"
    
    echo ""
    echo "📝 Recent Frontend Errors:"
    echo "--------------------------"
    tail -20 logs/dashboard_frontend.log | grep -i "error\|exception\|failed" || echo "No errors found"
    
    echo ""
    echo "📝 Recent Threat Consumer Errors:"
    echo "----------------------------------"
    tail -20 logs/threat_consumer.log | grep -i "error\|exception\|failed" || echo "No errors found"
}

# Show initial status
show_logs

echo ""
echo "🔄 Monitoring... (Refreshing every 5 seconds)"
echo ""

# Monitor in a loop
while true; do
    sleep 5
    clear
    show_logs
    echo ""
    echo "Last updated: $(date '+%H:%M:%S')"
    echo "Press Ctrl+C to stop monitoring"
done

