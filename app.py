import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
from search import *
from agents import define_graph
from streamlit_chat import message
from llms import load_llm 
from langchain_core.messages import BaseMessage, HumanMessage

st.title("GenAI Job Agent - 🦜")
uploaded_file = st.sidebar.file_uploader("Upload File", type="pdf")


# Handle file upload
if uploaded_file is not None:
    temp_dir = "tmp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    bytes_data = uploaded_file.getvalue()
    predefined_name = "cv.pdf"
    
    # To save the file, we use the 'with' statement to open a file and write the contents
    # The file will be saved with the predefined name in the /temp folder
    file_path = os.path.join(temp_dir, predefined_name)
    with open(file_path, "wb") as f:
        f.write(bytes_data)

    llm = load_llm()
    graph = define_graph(llm)

    def conversational_chat(query, graph):
        #Find data science job for me in Germany maximum 5 relevant one. \
        # Then analyze my CV and write me a cover letter according to the best matching job.
        results = []
        for s in graph.stream(
            {"messages": [HumanMessage(content=query)]},
            {"recursion_limit": 100},):
            if "__end__" not in s:
                result = list(s.values())[0]
                results.append(result)
                #print(s)
                #print("----")
                st.write(results)

        #result = agent_executor.invoke({"input": query, "chat_history": st.session_state['history']})
        #print(result)
        st.session_state['history'].append((query, results))
        return results

    # Initialize chat history
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    # Initialize messages
    if 'generated' not in st.session_state:
        st.session_state['generated'] = ["Hello ! Ask your Job agent " + uploaded_file.name + " 🤗"]

    if 'past' not in st.session_state:
        st.session_state['past'] = ["Hey ! 👋"]

    # Create containers for chat history and user input
    response_container = st.container()
    container = st.container()

    # User input form
    with container:
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_input("Query:", placeholder="Write your query 👉 (:", key='input')
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            output = conversational_chat(user_input, graph)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output["agent_outcome"].return_values["output"])

    # Display chat history
    if st.session_state['generated']:
        with response_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="big-smile")
                message(st.session_state["generated"][i], key=str(i), avatar_style="thumbs")