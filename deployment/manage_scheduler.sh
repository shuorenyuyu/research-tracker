#!/bin/bash

# Research Tracker Scheduler Control Script
# Manages the background scheduler service on macOS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PLIST_FILE="$SCRIPT_DIR/com.researchtracker.scheduler.plist"
LAUNCHAGENTS_DIR="$HOME/Library/LaunchAgents"
LAUNCHAGENTS_PLIST="$LAUNCHAGENTS_DIR/com.researchtracker.scheduler.plist"

case "$1" in
    install)
        echo "Installing Research Tracker scheduler..."
        
        # Create logs directory
        mkdir -p "$PROJECT_DIR/logs"
        
        # Copy plist to LaunchAgents
        cp "$PLIST_FILE" "$LAUNCHAGENTS_PLIST"
        
        # Load the service
        launchctl load "$LAUNCHAGENTS_PLIST"
        
        echo "✓ Scheduler installed and started"
        echo "  - Runs daily at 00:00 UTC"
        echo "  - Logs: $PROJECT_DIR/logs/scheduler.log"
        echo "  - To stop: ./manage_scheduler.sh stop"
        ;;
    
    uninstall)
        echo "Uninstalling Research Tracker scheduler..."
        
        # Unload the service
        launchctl unload "$LAUNCHAGENTS_PLIST" 2>/dev/null
        
        # Remove plist
        rm -f "$LAUNCHAGENTS_PLIST"
        
        echo "✓ Scheduler uninstalled"
        ;;
    
    start)
        echo "Starting scheduler..."
        launchctl load "$LAUNCHAGENTS_PLIST"
        echo "✓ Scheduler started"
        ;;
    
    stop)
        echo "Stopping scheduler..."
        launchctl unload "$LAUNCHAGENTS_PLIST"
        echo "✓ Scheduler stopped"
        ;;
    
    restart)
        echo "Restarting scheduler..."
        launchctl unload "$LAUNCHAGENTS_PLIST" 2>/dev/null
        launchctl load "$LAUNCHAGENTS_PLIST"
        echo "✓ Scheduler restarted"
        ;;
    
    status)
        echo "Checking scheduler status..."
        if launchctl list | grep -q "com.researchtracker.scheduler"; then
            echo "✓ Scheduler is RUNNING"
            
            # Show recent logs
            if [ -f "$PROJECT_DIR/logs/scheduler.log" ]; then
                echo ""
                echo "Recent logs (last 20 lines):"
                tail -20 "$PROJECT_DIR/logs/scheduler.log"
            fi
        else
            echo "✗ Scheduler is NOT running"
        fi
        ;;
    
    logs)
        echo "Showing scheduler logs..."
        if [ -f "$PROJECT_DIR/logs/scheduler.log" ]; then
            tail -f "$PROJECT_DIR/logs/scheduler.log"
        else
            echo "No logs found"
        fi
        ;;
    
    run-once)
        echo "Running one-time fetch..."
        cd "$PROJECT_DIR"
        source venv/bin/activate
        python3 src/scheduler/daily_scheduler.py --run-once
        ;;
    
    *)
        echo "Research Tracker Scheduler Control"
        echo ""
        echo "Usage: $0 {install|uninstall|start|stop|restart|status|logs|run-once}"
        echo ""
        echo "Commands:"
        echo "  install    - Install and start the scheduler service"
        echo "  uninstall  - Stop and remove the scheduler service"
        echo "  start      - Start the scheduler"
        echo "  stop       - Stop the scheduler"
        echo "  restart    - Restart the scheduler"
        echo "  status     - Check if scheduler is running"
        echo "  logs       - Show real-time logs"
        echo "  run-once   - Run fetch once without scheduling"
        exit 1
        ;;
esac

exit 0
