# Deployment Guide - Linux VM

Quick reference for deploying Research Tracker to a remote Linux server.

## 🌐 Production Server

- **Azure VM**: `20.51.208.13` (East US)
- **DNS URL**: http://alpha-research.eastus.cloudapp.azure.com/
- **SSH Alias**: `research-azure` (configured in `~/code/.ssh-config`)
- **User**: `azureuser`
- **Path**: `/home/azureuser/research-tracker`
- **Paper Selection**: Recent one year (current_year - 1 onwards) to ensure meaningful citation counts

## 📦 Three Ways to Deploy

### 1️⃣ **Quick Deploy (from your Mac)**

From your local machine:

```bash
# One command to deploy everything to remote server
./scripts/remote_deploy.sh
```

This will:
- Ask for SSH credentials
- Sync all code to remote server
- Run setup automatically
- Optionally transfer .env file
- Deploy scheduler (cron or systemd)

---

### 2️⃣ **Manual Deploy (SSH to server)**

If you prefer manual control:

```bash
# 1. SSH to your server
ssh user@your-server.com

# 2. Clone repository
git clone git@github.com:shuorenyuyu/research-tracker.git
cd research-tracker

# 3. Run setup
chmod +x scripts/*.sh
./scripts/setup.sh

# 4. Configure Azure credentials
nano .env
# Add your AZURE_OPENAI_ENDPOINT, API_KEY, etc.

# 5. Deploy scheduler
./scripts/deploy.sh
```

---

### 3️⃣ **Docker Deploy (coming soon)**

```bash
docker build -t research-tracker .
docker run -d --env-file .env research-tracker
```

---

## 🔧 Script Reference

### `setup.sh` - Initial Setup
Prepares environment on fresh server:
- Checks Python 3.8+
- Creates virtual environment
- Installs dependencies
- Creates directory structure
- Initializes database

```bash
./scripts/setup.sh
```

### `deploy.sh` - Scheduler Deployment
Sets up daily automation (runs at 00:00 UTC):

**Option 1: Cron Job** (simple)
- Creates `scripts/run_daily.sh`
- Adds cron entry
- Logs to `data/logs/cron.log`

**Option 2: Systemd** (production)
- Creates systemd service
- Creates systemd timer
- Better logging and monitoring

```bash
./scripts/deploy.sh
```

### `remote_deploy.sh` - Remote Deployment
Deploys from local Mac to remote server:
- Tests SSH connection
- Syncs code via rsync
- Runs remote setup
- Optionally transfers .env
- Deploys scheduler

```bash
./scripts/remote_deploy.sh
```

---

## ⚙️ Scheduler Options Comparison

| Feature | Cron Job | Systemd | macOS LaunchAgent |
|---------|----------|---------|-------------------|
| **Platform** | Linux | Linux | macOS |
| **Complexity** | Simple | Medium | Medium |
| **Logging** | Basic | Excellent | Good |
| **Monitoring** | Manual | `systemctl status` | `launchctl list` |
| **Auto-restart** | No | Yes (if configured) | Yes |
| **Best for** | Quick setup | Production | Development |

---

## 📋 Post-Deployment Checklist

After deployment, verify everything works:

```bash
# 1. Check scheduler status
# For cron:
crontab -l

# For systemd:
sudo systemctl status research-tracker.timer

# 2. View logs
tail -f data/logs/scheduler.log

# 3. Test manual run
source venv/bin/activate
python3 src/scheduler/daily_scheduler.py --run-once
python3 src/scheduler/process_papers.py --one

# 4. View fetched papers
python3 scripts/show_papers.py
```

---

## 🌍 Remote Server Requirements

### Minimum Specs
- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **CPU**: 1 vCPU (single-threaded tasks)
- **RAM**: 512 MB (minimal usage)
- **Disk**: 2 GB (code + venv + database)
- **Network**: Outbound HTTPS (Semantic Scholar API, Azure OpenAI)

### Recommended Specs (for 1-2 year operation)
- **RAM**: 1 GB
- **Disk**: 5 GB (growing database)

### Popular Providers
- **DigitalOcean**: $4/month droplet
- **Linode**: $5/month nanode
- **Vultr**: $3.50/month instance
- **AWS Lightsail**: $3.50/month
- **Azure VM**: B1s ($4.60/month)
- **GCP e2-micro**: Free tier eligible

---

## 🔐 Security Best Practices

### SSH Setup
```bash
# 1. Use SSH keys (not passwords)
ssh-keygen -t ed25519
ssh-copy-id user@your-server.com

# 2. Disable password authentication
# Edit /etc/ssh/sshd_config:
PasswordAuthentication no
```

### Environment Variables
```bash
# Never commit .env to git
# It's already in .gitignore

# Secure permissions on server
chmod 600 .env
```

### Firewall
```bash
# Only allow SSH (22) and outbound HTTPS (443)
sudo ufw allow 22/tcp
sudo ufw enable
```

---

## 🐛 Troubleshooting

### Cron job not running?
```bash
# Check cron logs
grep CRON /var/log/syslog

# Test script manually
./scripts/run_daily.sh

# Verify cron entry
crontab -l
```

### Systemd service failing?
```bash
# Check status
sudo systemctl status research-tracker.service

# View detailed logs
journalctl -u research-tracker.service -f

# Restart service
sudo systemctl restart research-tracker.service
```

### Python import errors?
```bash
# Ensure venv is activated in scripts
# Check scripts/run_daily.sh has:
source venv/bin/activate
```

### Database locked errors?
```bash
# SQLite can have issues with concurrent access
# Ensure only one process runs at a time
# Systemd handles this automatically (Type=oneshot)
```

---

## 📊 Monitoring

### View recent activity
```bash
# Last 50 lines of scheduler log
tail -50 data/logs/scheduler.log

# Real-time log watching
tail -f data/logs/*.log

# Database stats
sqlite3 data/papers.db "SELECT COUNT(*) FROM papers;"
sqlite3 data/papers.db "SELECT COUNT(*) FROM papers WHERE processed=1;"
```

### Check disk usage
```bash
du -sh data/
du -sh venv/
```

---

## 🔄 Updating Code on Remote Server

### Method 1: Git Pull
```bash
ssh user@your-server.com
cd research-tracker
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart research-tracker.service
```

### Method 2: Re-run remote_deploy.sh
```bash
# From your Mac
./scripts/remote_deploy.sh
```

---

## 📅 Schedule Customization

### Change run time (Systemd)
Edit `/etc/systemd/system/research-tracker.timer`:
```ini
[Timer]
# Run at 2 AM UTC instead of midnight
OnCalendar=*-*-* 02:00:00
```

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart research-tracker.timer
```

### Change run time (Cron)
```bash
crontab -e

# Change from:
0 0 * * * /path/to/run_daily.sh

# To (2 AM UTC):
0 2 * * * /path/to/run_daily.sh
```

---

## 💾 Backup Strategy

```bash
# Backup database
cp data/papers.db data/papers.db.backup

# Automated daily backup (add to cron)
0 1 * * * cp ~/research-tracker/data/papers.db ~/backups/papers_$(date +\%Y\%m\%d).db
```

---

**Last Updated**: December 7, 2025  
**For Questions**: Check ARCHITECTURE.md or README.md
