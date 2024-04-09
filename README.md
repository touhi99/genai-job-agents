## GenAI-job-agent

### Description


- Example inspired from https://github.com/langchain-ai/langgraph/blob/main/examples/multi_agent/agent_supervisor.ipynb?ref=blog.langchain.dev
- Linkedin *Unofficial* API

### Installation

```pip install -r requirements.txt```

### Usage

These environment variables are required:
OPENAI_API_KEY=<OPENAI_API_KEY>
LINKEDIN_EMAIL=<LINKEDIN_EMAIL>
LINKEDIN_PASS=<LINKEDIN_PASS>

Then run on terminal

```streamlit run app.py```

### TODO
- test conversation flow (add input suggestion)
- enrich linkedin search with more params
- write cover letter to a word doc and download to modify
- fix streamlit callback handler
- bug fixes