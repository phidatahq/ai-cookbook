from arxiv_ai.assistant import get_arxiv_assistant

arxiv_assistant = get_arxiv_assistant(user_id="ab", debug_mode=True)

# arxiv_assistant.print_response("Who are you?")
arxiv_assistant.print_response("What is FlashAttention?")
# arxiv_assistant.print_response("summarize this")
# arxiv_assistant.print_response("What the capital of India?")
