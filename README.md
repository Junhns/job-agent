# Job Application Agent

An AI agent that autonomously researches companies and generates 
tailored cover letters for job applications.

## How It Works
1. Paste a job description
2. Agent searches the web for information about the company
3. Claude synthesizes the research and your resume to write a 
   tailored cover letter and likely interview questions

## Architecture
- Python backend with Claude's tool use API
- Agentic loop — Claude autonomously decides what to search 
  and when it has enough context to stop
- BeautifulSoup for web scraping

## Setup
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:
```
ANTHROPIC_API_KEY=your_key_here
```

Run:
```bash
python agent.py
```

## Notes
Current limitation: Google blocks automated scraping so search 
results are limited. In production I'd replace with Brave Search 
API or SerpAPI for reliable results.
