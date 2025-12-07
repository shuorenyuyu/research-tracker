#!/bin/bash
#
# Research Tracker - Remote Deploy Script
# Deploys the project to a remote Linux VM via SSH
#

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║      Research Tracker - Remote Deployment to Linux VM           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
read -p "Remote host (e.g., user@your-server.com): " REMOTE_HOST
read -p "Remote directory (default: ~/research-tracker): " REMOTE_DIR
REMOTE_DIR=${REMOTE_DIR:-~/research-tracker}

echo ""
echo "Deploying to: $REMOTE_HOST:$REMOTE_DIR"
echo ""

# Check SSH connection
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing SSH connection..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ssh -o ConnectTimeout=5 "$REMOTE_HOST" "echo 'SSH connection successful'"; then
    echo -e "${GREEN}✓ SSH connection successful${NC}"
else
    echo -e "${RED}✗ SSH connection failed${NC}"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Creating remote directory"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh "$REMOTE_HOST" "mkdir -p $REMOTE_DIR"
echo -e "${GREEN}✓ Remote directory created${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Syncing project files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Sync files (exclude venv, data, logs)
rsync -avz --progress \
    --exclude 'venv/' \
    --exclude 'data/' \
    --exclude '.git/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.DS_Store' \
    --exclude '.env' \
    ./ "$REMOTE_HOST:$REMOTE_DIR/"

echo -e "${GREEN}✓ Files synced${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Running remote setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ssh "$REMOTE_HOST" "cd $REMOTE_DIR && chmod +x scripts/*.sh && ./scripts/setup.sh"
echo -e "${GREEN}✓ Remote setup complete${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Transferring .env file"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ".env" ]; then
    read -p "Transfer local .env file to remote? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        scp .env "$REMOTE_HOST:$REMOTE_DIR/.env"
        echo -e "${GREEN}✓ .env file transferred${NC}"
    else
        echo -e "${YELLOW}⚠ You'll need to configure .env on remote manually${NC}"
        echo "  ssh $REMOTE_HOST"
        echo "  cd $REMOTE_DIR"
        echo "  nano .env"
    fi
else
    echo -e "${YELLOW}⚠ No local .env file found${NC}"
    echo "You'll need to create .env on remote server"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Deploying scheduler"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

read -p "Deploy scheduler now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ssh "$REMOTE_HOST" "cd $REMOTE_DIR && ./scripts/deploy.sh"
    echo -e "${GREEN}✓ Scheduler deployed${NC}"
else
    echo -e "${YELLOW}⚠ Skipped scheduler deployment${NC}"
    echo "To deploy later: ssh $REMOTE_HOST 'cd $REMOTE_DIR && ./scripts/deploy.sh'"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║              Remote Deployment Complete! ✅                      ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Remote server: $REMOTE_HOST"
echo "Project directory: $REMOTE_DIR"
echo ""
echo "To manage remotely:"
echo "  SSH: ssh $REMOTE_HOST"
echo "  View logs: ssh $REMOTE_HOST 'tail -f $REMOTE_DIR/data/logs/*.log'"
echo "  Run manually: ssh $REMOTE_HOST 'cd $REMOTE_DIR && source venv/bin/activate && python3 src/scheduler/daily_scheduler.py --run-once'"
echo ""
