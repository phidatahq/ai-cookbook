def handle_message(message):
    p_message = message.lower()

    if p_message == "hello" or p_message == "hi":
        return "Hello! Please use `/discuss` or `/summarize` to interact with me."


def handle_discussion(paper):
    return f"Thanks for providing me with {paper}. You can now discuss the paper with me."
