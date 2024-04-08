from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
import operator
from typing import Annotated, Sequence, TypedDict
import functools
from langgraph.graph import StateGraph, END
from langchain_community.callbacks import StreamlitCallbackHandler
from tools import *

def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
    # Each worker node will be given a name and some tools.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor

def agent_node(state, agent, name, callbacks):
    result = agent.invoke(state, callbacks=callbacks)
    return {"messages": [HumanMessage(content=result["output"], name=name)]} #["output"]

def define_graph(llm, st_callback):
    members = ["Analyzer", "Generator", "Searcher"]
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        " following workers:  {members}. User has uploaded a document and sent a query. Given the uploaded document and following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status." 
        #" Task will include, extracting cv content, searching jobs given user query, write modified cv according to best matched jobs."
        " When finished, respond with FINISH."
    )

    # Our team supervisor is an LLM node. It just picks the next agent to process
    # and decides when the work is completed
    options = ["FINISH"] + members
    # Using openai function calling can make output parsing easier for us
    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    "title": "Next",
                    "anyOf": [
                        {"enum": options},
                    ],
                }
            },
            "required": ["next"],
        },
    }

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next?"
                " Or should we FINISH? Select one of: {options}",
            ),]).partial(options=str(options), members=", ".join(members))

    supervisor_chain = (
        prompt
        | llm.bind_functions(functions=[function_def], function_call="route") 
        | JsonOutputFunctionsParser()
    )

    search_agent = create_agent(llm, [job_pipeline], "Given user job related queries of searching a role with necessary parameters, show the most relevant jobs with title, company url, job location and detailed job description")
    search_node = functools.partial(agent_node, agent=search_agent, name="Searcher", callbacks=st_callback)

    analyzer_agent = create_agent(llm, [extract_cv], "Analyzer extracts the user uploaded document, then reviews the content and relevant job listings from the Searcher. It extracts information from the resume to find the best matching job.")
    analyzer_node = functools.partial(agent_node, agent=analyzer_agent, name="Analyzer", callbacks=st_callback)

    generator_agent = create_agent(llm, [generate_letter_for_specific_job], "Given the extracted CV and highest matching job from the Analyzer, write a cover letter motivated with the job.")
    generator_node = functools.partial(agent_node, agent=generator_agent, name="Generator", callbacks=st_callback)

    workflow = StateGraph(AgentState)
    workflow.add_node("Analyzer", analyzer_node)
    workflow.add_node("Searcher", search_node)
    workflow.add_node("Generator", generator_node)
    workflow.add_node("supervisor", supervisor_chain)

    for member in members:
        # We want our workers to ALWAYS "report back" to the supervisor when done
        workflow.add_edge(member, "supervisor")
    # The supervisor populates the "next" field in the graph state
    # which routes to a node or finishes
    conditional_map = {k: k for k in members}
    conditional_map["FINISH"] = END
    workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
    # Finally, add entrypoint
    workflow.set_entry_point("supervisor")

    graph = workflow.compile()
    return graph

# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always be added to the current states
    input: str
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str
    #callbacks: StreamlitCallbackHandler
