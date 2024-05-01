from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
llama3_begin_template = "<|begin_of_text|><|start_header_id|>system<|end_header_id|> "
llama3_end_template = " <|eot_id|> <|start_header_id|>assistant<|end_header_id|>"

def routing_prompt(llm_name, options, members):
      system_prompt = get_system_prompt(llm_name)

      if llm_name=='openai':
            prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                  "system",  "Given the conversation above, who should act next?" \
                  " Or is the task complete and should we FINISH?  Select one of: {options}",
            ),]).partial(options=str(options), members=", ".join(members))
      if llm_name=='groq':
            prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                  "system",  llama3_begin_template + "Summarize and asses the conversation. Given the conversation above, who should act next?" \
                  " Or is the task complete and should we FINISH?  Select one of: {options}" + llama3_end_template,
            ),]).partial(options=str(options), members=", ".join(members))
      return prompt

def get_system_prompt(llm_name):
      if llm_name=='openai':
            SYSTEM_PROMPT = "You are a supervisor agent tasked with managing a conversation between the"\
            " following workers:  {members}. User has uploaded a document and sent a query. Given the uploaded document and following user request,"\
            " respond with the worker to act next. Each worker will perform a"\
            " task and respond with their results and status." \
            " only route the tasks based on the router if there is anything to route or task is not complete." \
            " When finished, respond with FINISH."
      elif llm_name=='groq':
            SYSTEM_PROMPT = llama3_begin_template + "You are a supervisor agent tasked with managing a conversation between the"\
            " following workers:  {members}. User has uploaded a CV and sent a query. Given the uploaded CV and following user request,"\
            " respond with the worker to act next. Each worker will perform a"\
            " task and respond with their results and status." \
            " After the result: ask yourself from the original query if the task is satisfied? based on that pass it to next appropriate route. " \
            " When task is finished, respond with FINISH." \
            + llama3_end_template
      
      return SYSTEM_PROMPT


def get_search_agent_prompt(llm_name):
      if llm_name=='openai':
            SEARCH_AGENT = "Search for job listings based on user-specified parameters, DISPLAY job title, company URL, location, and a summary. \
            If unsuccessful, retry with alternative keywords up to three times and provide the results"
      elif llm_name=='groq':
            SEARCH_AGENT = llama3_begin_template + "You are a Searcher Agent. \
            Search for job listings based on user-specified parameters, DISPLAY job title, company URL, location, and a summary. \
            If unsuccessful, retry with alternative keywords up to three times and provide the results" + llama3_end_template
      
      return SEARCH_AGENT

def get_analyzer_agent_prompt(llm_name):
      if llm_name=='openai':
            ANALYZER_AGENT = "Analyze the content of a user-uploaded document and matching job listings to recommend the best job fit, detailing the reasons behind the choice."
      elif llm_name=='groq':
            ANALYZER_AGENT = llama3_begin_template + "You are an Analyzer Agent. \
            Analyze the content of the user-uploaded CV and matching job listings to recommend the best job fit, \
            detailing the reasons behind the choice." \
            + llama3_end_template
      
      return ANALYZER_AGENT

def get_generator_agent_prompt(llm_name):
      if llm_name=='openai':
            GENERATOR_AGENT = "Generate a personalized cover letter based on an uploaded CV and provide the text output."
      elif llm_name=='groq':
            GENERATOR_AGENT = llama3_begin_template + "You are a Generator Agent. \
            Generate a personalized cover letter based on an uploaded CV and provide the text output." \
            + llama3_end_template
      
      return GENERATOR_AGENT

### Example input:
#Find data science job for me in Germany maximum 5 relevant one. \
# Then analyze my CV and write me a cover letter according to the best matching job.