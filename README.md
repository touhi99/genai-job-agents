## GenAI-job-agent

### Description

This is a simple Langgraph/Langchain based AI agent as a learning experiment of how LLM-based agent will work. Motivation is to automate better seaching in API (in this case Linkedin job), find suitable matching given user resume and write a cover letter for the most matching job. There are different usecases can be extended on top of the current design. 

- Langgraph example inspired from [Notebook](https://github.com/langchain-ai/langgraph/blob/main/examples/multi_agent/agent_supervisor.ipynb?ref=blog.langchain.dev)
- Warning: Linkedin *Unofficial* API. Using it might violate LinkedIn's Terms of Service. Use it at your own risk. [Github](https://github.com/tomquirk/linkedin-api)

### Installation

```pip install -r requirements.txt```

### Usage

These environment variables are required:
``OPENAI_API_KEY=<OPENAI_API_KEY>
LINKEDIN_EMAIL=<LINKEDIN_EMAIL>
LINKEDIN_PASS=<LINKEDIN_PASS>``
LANGCHAIN_API_KEY=<LANGSMITH_KEY>
LANGCHAIN_TRACING_V2=true
LLM_NAME=<LLM_NAME> groq/openai

Then run on terminal

```streamlit run app.py```

### Agents

````
                                          +-----------+                                          
                                          | __start__ |                                          
                                          +-----------+                                          
                                                *                                                
                                                *                                                
                                                *                                                
                                         +------------+                                          
                                      ***| supervisor |****                                      
                               *******   +------------+*   *******                               
                        *******          ***            ***       *******                        
                 *******                *                  ***           *******                 
          *******                     **                      ***               *******          
      ****              +----------------------+                 **                    ****      
      *                 | supervisor_condition |**                *                       *      
      *                 +----------------------+* **********      *                       *      
      *            *****            *            *****      **********                    *      
      *       *****                 *                 *****       *   **********          *      
      *    ***                      *                      ***    *             *****     *      
+-----------+                 +---------+                  +-----------+            +----------+ 
| Extractor |                 | __end__ |                  | Generator |            | Searcher | 
+-----------+                 +---------+                  +-----------+            +----------+ 
````
### TODO
- enrich linkedin search with more params
- fix streamlit callback handler
- bug fixes