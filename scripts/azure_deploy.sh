#!/bin/bash
# Azure Deployment Helper Script
# Usage: ./scripts/azure_deploy.sh [command]

set -e

REMOTE="research-azure"
REMOTE_DIR="~/research-tracker"

case "${1:-help}" in
    status)
        echo "📊 Checking server status..."
        ssh $REMOTE "cd $REMOTE_DIR && git status && echo '---' && ps aux | grep -E '(daily_fetch|process_papers)' | grep -v grep || echo 'No processes running'"
        ;;
    
    logs)
        echo "📋 Fetching recent logs..."
        ssh $REMOTE "cd $REMOTE_DIR && tail -50 data/logs/daily_fetch.log 2>/dev/null || echo 'No logs yet'"
        ;;
    
    db)
        echo "🗄️ Checking database..."
        ssh $REMOTE "cd $REMOTE_DIR && python3 scripts/show_papers.py 2>/dev/null || echo 'Error running show_papers.py'"
        ;;
    
    pull)
        echo "⬇️ Pulling latest code from GitHub..."
        ssh $REMOTE "cd $REMOTE_DIR && git pull origin main"
        ;;
    
    deploy)
        echo "🚀 Deploying latest code..."
        ssh $REMOTE "cd $REMOTE_DIR && git pull origin main && source venv/bin/activate && pip install -r requirements.txt -q"
        echo "✅ Deployment complete!"
        ;;
    
    restart)
        echo "🔄 Restarting processes..."
        ssh $REMOTE "pkill -f daily_fetch.py || true"
        echo "Stopped old processes"
        ssh $REMOTE "cd $REMOTE_DIR && nohup bash -c 'source venv/bin/activate && python3 scripts/daily_fetch.py' > /dev/null 2>&1 &"
        echo "✅ Process restarted"
        ;;
    
    stop)
        echo "⏹️ Stopping processes..."
        ssh $REMOTE "pkill -f daily_fetch.py || echo 'No process to stop'"
        ;;
    
    ssh)
        echo "🔌 Connecting to server..."
        ssh $REMOTE
        ;;
    
    help|*)
        echo "Azure Deployment Helper"
        echo ""
        echo "Usage: ./scripts/azure_deploy.sh [command]"
        echo ""
        echo "Commands:"
        echo "  status   - Check git status and running processes"
        echo "  logs     - View recent logs"
        echo "  db       - Check database contents"
        echo "  pull     - Pull latest code from GitHub"
        echo "  deploy   - Pull code and install dependencies"
        echo "  restart  - Restart daily_fetch process"
        echo "  stop     - Stop all processes"
        echo "  ssh      - Connect to server"
        echo "  help     - Show this help message"
        ;;
esac
