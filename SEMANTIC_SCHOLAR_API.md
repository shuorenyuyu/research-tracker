# Semantic Scholar API Key Setup

## Why You Need an API Key

The free tier of Semantic Scholar API has **rate limits of 100 requests per 5 minutes**. Without an API key, you may encounter **429 "Too Many Requests" errors**, especially when:
- Running the daily fetch multiple times for testing
- Searching with multiple keywords
- Making frequent requests

## How to Get an API Key (FREE)

1. **Go to the API Key Request Form:**
   https://www.semanticscholar.org/product/api#api-key-form

2. **Fill out the form:**
   - Name: Your name
   - Email: Your email address
   - Project description: "Research paper tracker for investment analysis"
   - Intended use: "Daily automated fetching of AI/ML/Robotics research papers"

3. **Submit and wait for approval** (usually within 1-2 business days)

4. **Add the API key to your `.env` file:**
   ```bash
   SEMANTIC_SCHOLAR_API_KEY=your_api_key_here
   ```

5. **Deploy to production:**
   ```bash
   # Update .env on Azure VM
   ssh research-azure 'nano research-tracker/.env'
   # Add the line: SEMANTIC_SCHOLAR_API_KEY=your_key
   ```

## Benefits of API Key

- **Higher rate limits**: 1 request per second (vs 100 per 5 minutes)
- **More reliable**: No 429 errors during daily automation
- **Better performance**: Can search multiple keywords without timeout

## Current Status

- **Local**: Check `.env` file for `SEMANTIC_SCHOLAR_API_KEY`
- **Production**: SSH to Azure VM and check `.env`
- **Logs**: Check for "using higher rate limits" message in logs

```bash
ssh research-azure 'cd research-tracker && grep SEMANTIC_SCHOLAR .env'
```
