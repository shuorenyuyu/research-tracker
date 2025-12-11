# Automatic API Fallback Mechanism

## Overview
The Research Tracker now has **automatic failover** between research paper APIs to ensure continuous operation even when one API is rate-limited or unavailable.

## Architecture

### Primary Source: Semantic Scholar
- **API**: https://api.semanticscholar.org/
- **Rate Limit**: 1 req/sec with free API key
- **Requires**: API key (free, but requires registration)
- **Advantage**: 214M+ papers, comprehensive citation data

### Fallback Source: OpenAlex  
- **API**: https://api.openalex.org/
- **Rate Limit**: 10 req/sec (NO API KEY REQUIRED!)
- **Requires**: Nothing - completely free and open
- **Advantage**: 200M+ papers, no registration needed, higher rate limits

## How It Works

```
┌─────────────────────────────────────────────┐
│  Daily Scheduler Starts                     │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Try Semantic Scholar First                 │
│  (Primary source - best citation data)      │
└──────────────┬──────────────────────────────┘
               │
               ├──Success (papers found)──────►  Use papers ✓
               │
               └──Failed/Rate Limited (429)
                              │
                              ▼
               ┌─────────────────────────────────┐
               │  Auto-Fallback to OpenAlex      │
               │  (Free, no API key needed)      │
               └──────────────┬──────────────────┘
                              │
                              ├──Success───────►  Use papers ✓
                              │
                              └──Failed
                                         │
                                         ▼
                              ┌─────────────────┐
                              │  Report Error   │
                              └─────────────────┘
```

## Code Implementation

### Scheduler Changes
**File**: `src/scheduler/daily_scheduler.py`

```python
# Initialize both scrapers
self.ss_scraper = SemanticScholarScraper(...)  # Primary
self.openalex_scraper = OpenAlexScraper(...)   # Fallback

def fetch_and_store_papers(self):
    # Try Semantic Scholar first
    try:
        papers = self.ss_scraper.get_recent_papers(...)
        if papers:
            source = "semantic_scholar"
    except:
        papers = []
    
    # Fallback to OpenAlex if needed
    if not papers:
        papers = self.openalex_scraper.get_recent_papers(...)
        source = "openalex"
```

## Testing

### Test OpenAlex Scraper
```bash
python3 scripts/test_openalex.py
```

**Sample Output**:
```
Found 77 quality papers (with abstracts and citations)
Highest cited paper:
  Title: On Assessing ML Model Robustness
  Citations: 4319
  Source: openalex
```

### Test Full Fallback Mechanism
```bash
python3 src/scheduler/daily_scheduler.py --run-once
```

**Expected Behavior**:
1. Try Semantic Scholar → Success (if not rate limited)
2. Try Semantic Scholar → Fail → Auto-switch to OpenAlex (if rate limited)

## Log Examples

### Successful Primary Source
```
[1/3] Attempting to fetch from Semantic Scholar...
✓ Semantic Scholar: Retrieved 100 papers
Using top 100 papers from semantic_scholar
```

### Successful Fallback
```
[1/3] Attempting to fetch from Semantic Scholar...
✗ Semantic Scholar: 429 Rate Limited
[1/3 FALLBACK] Switching to OpenAlex...
✓ OpenAlex: Retrieved 77 papers
Using top 77 papers from openalex
```

### Both Failed (rare)
```
✗ Semantic Scholar failed: 429 Rate Limited
✗ OpenAlex also failed: Network error
ERROR: Both sources failed - cannot fetch papers
```

## Benefits

1. **Zero Downtime**: If one API is blocked, automatically use the other
2. **No Manual Intervention**: Fully automatic failover
3. **No API Key Hassle**: OpenAlex requires no registration
4. **Better Rate Limits**: OpenAlex allows 10 req/sec vs Semantic Scholar's 1 req/sec
5. **Cost**: Both APIs are 100% free

## Database Compatibility

Papers from both sources use the same schema:
- `source` field: `"semantic_scholar"` or `"openalex"`
- `paper_id`: Unique identifier from each source
- `citation_count`: Available from both
- `abstract`, `title`, `authors`: Standardized format

## Monitoring

Check logs to see which source was used:
```bash
tail -f data/logs/scheduler.log | grep "Using top"
```

Output shows source:
- `Using top 100 papers from semantic_scholar` - Primary worked
- `Using top 77 papers from openalex` - Fallback activated

## Future Improvements

1. **Add More Fallbacks**: CrossRef, PubMed, etc.
2. **Smart Source Selection**: Rotate between sources to distribute load
3. **Source Preference**: Configure preferred source per keyword
4. **Metrics**: Track success rate of each source

## Files Modified

- `src/scrapers/openalex_scraper.py` - New OpenAlex scraper implementation
- `src/scheduler/daily_scheduler.py` - Added automatic fallback logic
- `scripts/test_openalex.py` - Test script for OpenAlex

## Conclusion

You no longer need to worry about Semantic Scholar rate limits! The system will automatically use OpenAlex as a free, reliable fallback whenever needed. Both APIs are 100% free and provide high-quality research papers.
