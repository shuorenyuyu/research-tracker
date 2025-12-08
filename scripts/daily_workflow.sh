#!/bin/bash
# Daily Research Tracker Workflow
# Runs: Fetch → Summarize → Generate Article
# Usage: bash scripts/daily_workflow.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "🚀 Starting Daily Research Tracker Workflow"
echo "Time: $(date)"
echo "========================================"

# Step 1: Fetch one high-quality paper
echo ""
echo "📥 Step 1: Fetching today's paper..."
python3 src/scheduler/daily_scheduler.py --run-once
FETCH_STATUS=$?

if [ $FETCH_STATUS -ne 0 ]; then
    echo "❌ Paper fetch failed!"
    exit 1
fi

echo "✅ Paper fetch complete"

# Step 2: Process unprocessed papers (generate summaries)
echo ""
echo "🤖 Step 2: Generating AI summaries..."
python3 src/scheduler/process_papers.py --one
PROCESS_STATUS=$?

if [ $PROCESS_STATUS -ne 0 ]; then
    echo "⚠️  Summary generation failed (may be no unprocessed papers)"
fi

echo "✅ Summary generation complete"

# Step 3: Generate WeChat article
echo ""
echo "📝 Step 3: Generating WeChat article..."
python3 scripts/generate_wechat_article.py
ARTICLE_STATUS=$?

if [ $ARTICLE_STATUS -ne 0 ]; then
    echo "⚠️  Article generation failed"
else
    echo "✅ Article generation complete"
fi

# Summary
echo ""
echo "========================================"
echo "✅ Daily workflow completed!"
echo "Time: $(date)"
echo ""
echo "📊 Summary:"
python3 -c "
import sqlite3
conn = sqlite3.connect('data/papers.db')
c = conn.cursor()
total = c.execute('SELECT COUNT(*) FROM papers').fetchone()[0]
processed = c.execute('SELECT COUNT(*) FROM papers WHERE processed = 1').fetchone()[0]
print(f'  Total papers: {total}')
print(f'  Processed: {processed}')
print(f'  Pending: {total - processed}')
conn.close()
"
