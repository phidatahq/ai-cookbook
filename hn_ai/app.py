from typing import List

import streamlit as st
from phi.assistant import Assistant
from phi.tools.streamlit.components import (
    get_openai_key_sidebar,
    get_username_sidebar,
)

from hn_ai.assistant import get_hn_assistant
from utils.log import logger


st.set_page_config(
    page_title="Hacker News AI",
    page_icon=":orange_heart:",
)
st.title("Hacker News AI")
st.markdown("##### :orange_heart: built using [phidata](https://github.com/phidatahq/phidata)")
with st.expander(":rainbow[:point_down: Example Questions]"):
    st.markdown("- Tell me about the user pg")
    st.markdown("- What's on hackernews about AI?")
    st.markdown("- What's on hackernews about iPhone?")
    st.markdown("- What's trending on hackernews?")
    st.markdown("- What are users showing on hackernews?")
    st.markdown("- What are users asking on hackernews?")
    st.markdown("- Summarize this story: https://news.ycombinator.com/item?id=39156778")


def restart_assistant():
    st.session_state["hn_assistant"] = None
    st.session_state["hn_assistant_run_id"] = None
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
        st.markdown("#### :technologist: Enter a username and start chatting with the Hacker News AI")
        return

    # Get the assistant
    hn_assistant: Assistant
    if "hn_assistant" not in st.session_state or st.session_state["hn_assistant"] is None:
        logger.info("---*--- Creating HackerNews Assistant ---*---")
        hn_assistant = get_hn_assistant(
            user_id=username,
            debug_mode=True,
        )
        st.session_state["hn_assistant"] = hn_assistant
    else:
        hn_assistant = st.session_state["hn_assistant"]

    # Create assistant run (i.e. log to database) and save run_id in session state
    st.session_state["hn_assistant_run_id"] = hn_assistant.create_run()

    # Load messages for existing assistant
    assistant_chat_history = hn_assistant.memory.get_chat_history()
    if len(assistant_chat_history) > 0:
        logger.debug("Loading chat history")
        st.session_state["messages"] = assistant_chat_history
    else:
        logger.debug("No chat history found")
        st.session_state["messages"] = [{"role": "assistant", "content": "Ask me about what's on HackerNews"}]

    # Prompt for user input
    if prompt := st.chat_input():
        st.session_state["messages"].append({"role": "user", "content": prompt})

    if st.sidebar.button("What are my top posts?"):
        _message = "What are my top posts?"
        st.session_state["messages"].append({"role": "user", "content": _message})

    if st.sidebar.button("What's Trending about AI?"):
        _message = "What's Trending about AI?"
        st.session_state["messages"].append({"role": "user", "content": _message})

    if st.sidebar.button("What's Trending about iPhone?"):
        _message = "What's Trending about iPhone?"
        st.session_state["messages"].append({"role": "user", "content": _message})

    if st.sidebar.button("What's Trending?"):
        _message = "What's Trending on hackernews?"
        st.session_state["messages"].append({"role": "user", "content": _message})

    if st.sidebar.button("What's on show?"):
        _message = "What are users showing on hackernews?"
        st.session_state["messages"].append({"role": "user", "content": _message})

    if st.sidebar.button("What's on ask?"):
        _message = "What are users asking on hackernews?"
        st.session_state["messages"].append({"role": "user", "content": _message})

    if st.sidebar.button("What's new on HN?"):
        _message = "What are new stories on hackernews?"
        st.session_state["messages"].append({"role": "user", "content": _message})

    if st.sidebar.button(":orange_heart: You're awesome!"):
        _message = "You're awesome!"
        st.session_state["messages"].append({"role": "user", "content": _message})

    # Tell me about a user
    if "summarize_user" not in st.session_state:
        st.session_state.summarize_user = ""

    def submit_user_for_summary():
        st.session_state.summarize_user = st.session_state.summarize_user_input
        st.session_state.summarize_user_input = ""

    st.sidebar.text_input(
        ":female-technologist: Ask about a user",
        key="summarize_user_input",
        placeholder="pg",
        on_change=submit_user_for_summary,
    )
    if st.session_state.summarize_user != "":
        _message = f"Tell me about this hackernews user: {st.session_state.summarize_user}"
        st.session_state.summarize_user = ""
        st.session_state["messages"].append({"role": "user", "content": _message})

    # Summarize a story
    if "summarize_story" not in st.session_state:
        st.session_state.summarize_story = ""

    def submit_story_for_summary():
        st.session_state.summarize_story = st.session_state.summarize_story_input
        st.session_state.summarize_story_input = ""

    st.sidebar.text_input(
        ":scroll: Summarize a story",
        key="summarize_story_input",
        placeholder="https://news.ycombinator.com/item?id=39165080",
        on_change=submit_story_for_summary,
    )
    if st.session_state.summarize_story != "":
        _message = f"Summarize this story: {st.session_state.summarize_story}"
        st.session_state.summarize_story = ""
        st.session_state["messages"].append({"role": "user", "content": _message})

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
                for delta in hn_assistant.run(question):
                    response += delta  # type: ignore
                    resp_container.markdown(response)

                st.session_state["messages"].append({"role": "assistant", "content": response})

    st.sidebar.markdown("---")

    if st.sidebar.button("New Run"):
        restart_assistant()

    if st.sidebar.button("Auto Rename"):
        hn_assistant.auto_rename_run()

    if hn_assistant.storage:
        hn_assistant_run_ids: List[str] = hn_assistant.storage.get_all_run_ids(user_id=username)
        new_hn_assistant_run_id = st.sidebar.selectbox("Run ID", options=hn_assistant_run_ids)
        if st.session_state["hn_assistant_run_id"] != new_hn_assistant_run_id:
            logger.debug(f"Loading run {new_hn_assistant_run_id}")
            logger.info("---*--- Loading HackerNews Assistant ---*---")
            st.session_state["hn_assistant"] = get_hn_assistant(
                user_id=username,
                run_id=new_hn_assistant_run_id,
                debug_mode=True,
            )
            st.rerun()

    hn_assistant_run_name = hn_assistant.run_name
    if hn_assistant_run_name:
        st.sidebar.write(f":thread: {hn_assistant_run_name}")


main()
