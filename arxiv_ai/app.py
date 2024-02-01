from typing import List

import streamlit as st
from phi.assistant import Assistant
from phi.tools.streamlit.components import (
    get_openai_key_sidebar,
    get_username_sidebar,
    reload_button_sidebar,
)

from arxiv_ai.assistant import get_arxiv_assistant
from utils.log import logger


st.set_page_config(
    page_title="Arxiv AI",
    page_icon=":orange_heart:",
)
st.title("Chat with Arxiv Papers")
st.markdown("##### :orange_heart: built using [phidata](https://github.com/phidatahq/phidata)")


def restart_assistant():
    st.session_state["arxiv_assistant"] = None
    st.session_state["arxiv_assistant_run_id"] = None
    st.rerun()


def main() -> None:
    # Get OpenAI key from environment variable or user input
    get_openai_key_sidebar()

    # Get username
    username = get_username_sidebar()
    if username:
        st.sidebar.info(f":technologist: User: {username}")
    else:
        st.markdown("---")
        st.markdown("#### :technologist: Enter a username and ask me about Arxiv papers")
        return

    # Get the assistant
    arxiv_assistant: Assistant
    if "arxiv_assistant" not in st.session_state or st.session_state["arxiv_assistant"] is None:
        logger.info("---*--- Creating Arxiv Assistant ---*---")
        arxiv_assistant = get_arxiv_assistant(
            user_id=username,
            debug_mode=True,
        )
        st.session_state["arxiv_assistant"] = arxiv_assistant
    else:
        arxiv_assistant = st.session_state["arxiv_assistant"]

    # Create assistant run (i.e. log to database) and save run_id in session state
    st.session_state["arxiv_assistant_run_id"] = arxiv_assistant.create_run()

    # Load messages for existing assistant
    assistant_chat_history = arxiv_assistant.memory.get_chat_history()
    if len(assistant_chat_history) > 0:
        logger.debug("Loading chat history")
        st.session_state["messages"] = assistant_chat_history
    else:
        logger.debug("No chat history found")
        st.session_state["messages"] = [{"role": "assistant", "content": "Ask me questions from the Arxiv"}]

    # Prompt for user input
    if prompt := st.chat_input():
        st.session_state["messages"].append({"role": "user", "content": prompt})

    # Display existing chat messages
    for message in st.session_state["messages"]:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is from a user, generate a new response
    last_message = st.session_state["messages"][-1]
    if last_message.get("role") == "user":
        question = last_message["content"]
        with st.chat_message("assistant"):
            with st.spinner("Working..."):
                response = ""
                resp_container = st.empty()
                for delta in arxiv_assistant.run(question):
                    response += delta  # type: ignore
                    resp_container.markdown(response)

                st.session_state["messages"].append({"role": "assistant", "content": response})

    # Select a specic paper
    # if arxiv_assistant.knowledge_base:
    #     available_docs = get_available_docs(arxiv_assistant.knowledge_base)
    #     selected_paper = st.sidebar.selectbox(
    #         "Select Paper",
    #         options=available_docs.keys(),
    #         format_func=lambda x: available_docs[x].title,
    #     )
    #     if selected_paper is not None:
    #        # Refresh the assistant to update the instructions and document names
    #        arxiv_assistant = get_arxiv_assistant(
    #            user_id=username,
    #            run_id=st.session_state["arxiv_assistant_run_id"],
    #            document_name=selected_paper,
    #            debug_mode=True,
    #        )
    #        st.session_state["arxiv_assistant"] = arxiv_assistant

    st.sidebar.markdown("---")

    if st.sidebar.button("New Run"):
        restart_assistant()

    if st.sidebar.button("Auto Rename"):
        arxiv_assistant.auto_rename_run()

    if arxiv_assistant.storage:
        arxiv_assistant_run_ids: List[str] = arxiv_assistant.storage.get_all_run_ids(user_id=username)
        new_arxiv_assistant_run_id = st.sidebar.selectbox("Run ID", options=arxiv_assistant_run_ids)
        if st.session_state["arxiv_assistant_run_id"] != new_arxiv_assistant_run_id:
            logger.debug(f"Loading run {new_arxiv_assistant_run_id}")
            logger.info("---*--- Loading ArXiv Assistant ---*---")
            st.session_state["arxiv_assistant"] = get_arxiv_assistant(
                user_id=username,
                run_id=new_arxiv_assistant_run_id,
                debug_mode=True,
            )
            st.rerun()

    arxiv_assistant_run_name = arxiv_assistant.run_name
    if arxiv_assistant_run_name:
        st.sidebar.write(f":thread: {arxiv_assistant_run_name}")

    # Show reload button
    reload_button_sidebar()


main()
