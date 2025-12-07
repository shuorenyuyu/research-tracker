#!/bin/bash
#
# Research Tracker - Deploy Script for Linux VM
# Sets up systemd service and cron job for daily execution
#

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║         Research Tracker - Deployment Script (Linux)            ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get absolute path to project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_DIR/venv"
PYTHON_BIN="$VENV_PATH/bin/python3"

echo "Project directory: $PROJECT_DIR"
echo ""

# Check if running on Linux
if [[ ! "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${RED}✗ This script is for Linux only${NC}"
    echo "For macOS, use: ./deployment/manage_scheduler.sh"
    exit 1
fi

# Check if venv exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}✗ Virtual environment not found${NC}"
    echo "Run ./scripts/setup.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo "Copy .env.example to .env and configure Azure credentials"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Deployment Method Selection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Choose deployment method:"
echo "  1) Cron job (recommended for simple setup)"
echo "  2) Systemd service + timer (recommended for production)"
echo ""
read -p "Enter choice [1-2]: " -n 1 -r
echo ""

if [[ $REPLY == "1" ]]; then
    METHOD="cron"
elif [[ $REPLY == "2" ]]; then
    METHOD="systemd"
else
    echo -e "${RED}✗ Invalid choice${NC}"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Deploying with: $METHOD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$METHOD" == "cron" ]; then
    # Cron deployment
    CRON_SCRIPT="$PROJECT_DIR/scripts/run_daily.sh"
    
    # Create run script
    cat > "$CRON_SCRIPT" << 'EOFSCRIPT'
#!/bin/bash
# Research Tracker Daily Job
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run Phase 1: Fetch papers
python3 src/scheduler/daily_scheduler.py --run-once >> data/logs/cron.log 2>&1

# Run Phase 2: Summarize papers
python3 src/scheduler/process_papers.py --one >> data/logs/cron.log 2>&1

# Optional: Run Phase 3 (uncomment when ready)
# python3 src/scheduler/publish_papers.py --one >> data/logs/cron.log 2>&1

echo "$(date): Daily job completed" >> data/logs/cron.log
EOFSCRIPT
    
    chmod +x "$CRON_SCRIPT"
    echo -e "${GREEN}✓ Created run script: $CRON_SCRIPT${NC}"
    
    # Add to crontab (0 UTC = varies by local timezone)
    CRON_ENTRY="0 0 * * * $CRON_SCRIPT"
    
    # Check if entry already exists
    if crontab -l 2>/dev/null | grep -q "$CRON_SCRIPT"; then
        echo -e "${YELLOW}⚠ Cron job already exists${NC}"
    else
        (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
        echo -e "${GREEN}✓ Cron job added (runs daily at midnight UTC)${NC}"
    fi
    
    echo ""
    echo "Cron job installed!"
    echo "  Script: $CRON_SCRIPT"
    echo "  Schedule: Daily at 00:00 UTC"
    echo "  Logs: $PROJECT_DIR/data/logs/cron.log"
    echo ""
    echo "To test: $CRON_SCRIPT"
    echo "To remove: crontab -e (delete the line)"
    
elif [ "$METHOD" == "systemd" ]; then
    # Systemd deployment
    SERVICE_NAME="research-tracker"
    SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
    TIMER_FILE="/etc/systemd/system/$SERVICE_NAME.timer"
    
    # Create systemd service
    echo -e "${YELLOW}Creating systemd service...${NC}"
    sudo bash -c "cat > $SERVICE_FILE" << EOFSERVICE
[Unit]
Description=Research Tracker - AI Paper Fetcher & Summarizer
After=network.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_PATH/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PYTHON_BIN $PROJECT_DIR/src/scheduler/daily_scheduler.py --run-once
ExecStart=$PYTHON_BIN $PROJECT_DIR/src/scheduler/process_papers.py --one
StandardOutput=append:$PROJECT_DIR/data/logs/systemd.log
StandardError=append:$PROJECT_DIR/data/logs/systemd.log

[Install]
WantedBy=multi-user.target
EOFSERVICE
    
    echo -e "${GREEN}✓ Created service: $SERVICE_FILE${NC}"
    
    # Create systemd timer
    echo -e "${YELLOW}Creating systemd timer...${NC}"
    sudo bash -c "cat > $TIMER_FILE" << EOFTIMER
[Unit]
Description=Research Tracker Daily Timer
Requires=$SERVICE_NAME.service

[Timer]
OnCalendar=daily
# Run at midnight UTC (adjusts for local timezone)
OnCalendar=*-*-* 00:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOFTIMER
    
    echo -e "${GREEN}✓ Created timer: $TIMER_FILE${NC}"
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable and start timer
    sudo systemctl enable $SERVICE_NAME.timer
    sudo systemctl start $SERVICE_NAME.timer
    
    echo -e "${GREEN}✓ Timer enabled and started${NC}"
    
    echo ""
    echo "Systemd service installed!"
    echo "  Service: $SERVICE_NAME.service"
    echo "  Timer: $SERVICE_NAME.timer"
    echo "  Schedule: Daily at 00:00 UTC"
    echo "  Logs: $PROJECT_DIR/data/logs/systemd.log"
    echo ""
    echo "Commands:"
    echo "  Status: sudo systemctl status $SERVICE_NAME.timer"
    echo "  Run now: sudo systemctl start $SERVICE_NAME.service"
    echo "  View logs: journalctl -u $SERVICE_NAME.service -f"
    echo "  Stop: sudo systemctl stop $SERVICE_NAME.timer"
    echo "  Disable: sudo systemctl disable $SERVICE_NAME.timer"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test run
echo "Running test fetch..."
cd "$PROJECT_DIR"
source venv/bin/activate
python3 src/scheduler/daily_scheduler.py --run-once

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Test run successful${NC}"
else
    echo -e "${RED}✗ Test run failed${NC}"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                  Deployment Complete! ✅                         ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Your research tracker is now running!"
echo "Papers will be fetched and summarized daily at 00:00 UTC"
echo ""
