from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.output_parsers.openai_tools import JsonOutputToolsParser
import operator
from typing import Annotated, Sequence, TypedDict
import functools
from langgraph.graph import StateGraph, END
from tools import *
from prompts import *
import os 

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
    executor = AgentExecutor(agent=agent, tools=tools) # type: ignore
    return executor

def agent_node(state, agent, name):
    print("STATES ARE", state)
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]} 

def debug_output(data):
    print("DEBUG OUTPUT:", data)
    return data

def flatten_output(data):
    if 'args' in data and isinstance(data['args'], dict):
        # Move the contents of 'args' up to the top level
        args_content = data.pop('args')  # Remove 'args' and capture its contents
        data.update(args_content)  # Merge these contents into the top level of the dictionary
    return data

def define_graph(llm, llm_name):
    members = ["Analyzer", "Generator", "Searcher"]
    system_prompt = (get_system_prompt(llm_name))

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

    llm_name=os.environ.get('LLM_NAME')
    prompt = routing_prompt(llm_name, options, members)

    print(llm_name)
    if llm_name=="openai":
        supervisor_chain = (
            prompt
            | llm.bind_functions(functions=[function_def], function_call="route") 
            | JsonOutputFunctionsParser()
        )
    elif llm_name=="groq" or llm_name=="llama3":
        supervisor_chain = (
            prompt
            | llm.bind_tools(tools=[function_def]) 
            | JsonOutputToolsParser(first_tool_only=True)
            | flatten_output
        )
        print("DEBUG1#", supervisor_chain)


    search_agent = create_agent(llm, [job_pipeline], get_search_agent_prompt(llm_name))
    search_node = functools.partial(agent_node, agent=search_agent, name="Searcher")

    analyzer_agent = create_agent(llm, [extract_cv], get_analyzer_agent_prompt(llm_name))
    analyzer_node = functools.partial(agent_node, agent=analyzer_agent, name="Analyzer")

    generator_agent = create_agent(llm, [generate_letter_for_specific_job], get_generator_agent_prompt(llm_name))
    generator_node = functools.partial(agent_node, agent=generator_agent, name="Generator")

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
    next: str
