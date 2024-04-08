#define LLMs
from langchain_openai import ChatOpenAI
import os 

def load_llm():
    llm = ChatOpenAI(model_name="gpt-4-0125-preview", openai_api_key=os.environ["OPENAI_API_KEY"])
    return llm
#from langchain_groq import ChatGroq
#llm = ChatGroq(temperature=0, groq_api_key=os.environ["GROQ_API_KEY"], model_name="mixtral-8x7b-32768")