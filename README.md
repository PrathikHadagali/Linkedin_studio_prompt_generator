![Uploading image.png…]()

# Agentic LinkedIn Studio — Groq Edition

Gemini/OpenAI-free Streamlit application for real-time Agentic AI research and LinkedIn content generation.

Uses:
- Groq GPT-OSS
- Groq Browser Search
- arXiv API
- GitHub API
- Pydantic structured output

Pipeline:
1. Groq Browser Search for current web research
2. arXiv + GitHub collection
3. One Groq structured generation call
4. LinkedIn post + hashtags + source audit + ChatGPT image prompt

Setup:
    py -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    copy .env.example .env

Add your Groq key:
    GROQ_API_KEY=YOUR_KEY

Test:
    python test_groq.py
    python test_browser_search.py

Run:
    streamlit run app.py

Create a key at:
https://console.groq.com/keys

Never commit .env.
