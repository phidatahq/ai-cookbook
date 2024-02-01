from typing import List

import streamlit as st
from phi.assistant import Assistant
from phi.document import Document
from phi.document.reader.pdf import PDFReader
from phi.tools.streamlit.components import (
    get_openai_key_sidebar,
    get_username_sidebar,
    reload_button_sidebar,
)

from arxiv_ai.assistant import get_pdf_assistant
from utils.log import logger


st.set_page_config(
    page_title="Arxiv AI",
    page_icon=":orange_heart:",
)
st.title("Chat with Arxiv Papers")
st.markdown("##### :orange_heart: built using [phidata](https://github.com/phidatahq/phidata)")


def restart_assistant():
    st.session_state["pdf_assistant"] = None
    st.session_state["pdf_assistant_run_id"] = None
    st.session_state["file_uploader_key"] += 1
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
        st.markdown("#### :technologist: Enter a username, upload a PDF and start chatting")
        return

    # Get the assistant
    pdf_assistant: Assistant
    if "pdf_assistant" not in st.session_state or st.session_state["pdf_assistant"] is None:
        logger.info("---*--- Creating PDF Assistant ---*---")
        pdf_assistant = get_pdf_assistant(
            user_id=username,
            debug_mode=True,
        )
        st.session_state["pdf_assistant"] = pdf_assistant
    else:
        pdf_assistant = st.session_state["pdf_assistant"]

    # Create assistant run (i.e. log to database) and save run_id in session state
    st.session_state["pdf_assistant_run_id"] = pdf_assistant.create_run()

    # Load messages for existing assistant
    assistant_chat_history = pdf_assistant.memory.get_chat_history()
    if len(assistant_chat_history) > 0:
        logger.debug("Loading chat history")
        st.session_state["messages"] = assistant_chat_history
    else:
        logger.debug("No chat history found")
        st.session_state["messages"] = [{"role": "assistant", "content": "Ask me questions from the PDF"}]

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
                for delta in pdf_assistant.run(question):
                    response += delta  # type: ignore
                    resp_container.markdown(response)

                st.session_state["messages"].append({"role": "assistant", "content": response})

    # Upload PDF
    if pdf_assistant.knowledge_base:
        if "file_uploader_key" not in st.session_state:
            st.session_state["file_uploader_key"] = 0

        uploaded_file = st.sidebar.file_uploader(
            "Upload a PDF :page_facing_up:",
            type="pdf",
            key=st.session_state["file_uploader_key"],
        )
        if uploaded_file is not None:
            alert = st.sidebar.info("Processing PDF...", icon="ℹ️")
            pdf_name = uploaded_file.name.split(".")[0]
            if f"{pdf_name}_uploaded" not in st.session_state:
                reader = PDFReader()
                pdf_documents: List[Document] = reader.read(uploaded_file)
                if pdf_documents:
                    pdf_assistant.knowledge_base.load_documents(documents=pdf_documents, upsert=True)
                    # Refresh the assistant to update the instructions and document names
                    pdf_assistant = get_pdf_assistant(
                        user_id=username,
                        run_id=st.session_state["pdf_assistant_run_id"],
                        debug_mode=True,
                    )
                    st.session_state["pdf_assistant"] = pdf_assistant
                else:
                    st.sidebar.error("Could not read PDF")
                st.session_state[f"{pdf_name}_uploaded"] = True
            alert.empty()
        st.sidebar.success(":information_source: If the PDF throws an error, try uploading it again")

    st.sidebar.markdown("---")

    if st.sidebar.button("New Run"):
        restart_assistant()

    if st.sidebar.button("Auto Rename"):
        pdf_assistant.auto_rename_run()

    if pdf_assistant.storage:
        pdf_assistant_run_ids: List[str] = pdf_assistant.storage.get_all_run_ids(user_id=username)
        new_pdf_assistant_run_id = st.sidebar.selectbox("Run ID", options=pdf_assistant_run_ids)
        if st.session_state["pdf_assistant_run_id"] != new_pdf_assistant_run_id:
            logger.debug(f"Loading run {new_pdf_assistant_run_id}")
            logger.info("---*--- Loading PDF Assistant ---*---")
            st.session_state["pdf_assistant"] = get_pdf_assistant(
                user_id=username,
                run_id=new_pdf_assistant_run_id,
                debug_mode=True,
            )
            st.rerun()

    pdf_assistant_run_name = pdf_assistant.run_name
    if pdf_assistant_run_name:
        st.sidebar.write(f":thread: {pdf_assistant_run_name}")

    # Show reload button
    reload_button_sidebar()


main()
