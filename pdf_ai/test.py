from pdf_ai.assistant import get_pdf_assistant

pdf_assistant = get_pdf_assistant(user_id="ab", debug_mode=True)

pdf_assistant.print_response("Who is the agreement between?")
pdf_assistant.print_response("Who is the heyday agreement with?")
# pdf_assistant.print_response("summarize this")
# pdf_assistant.print_response("What the capital of India?")

# "If you are able to identify the document and the user asks a specific question, use the `search_document` tool to search the contents of the document for context.",
# "If you are able to identify the document and needs you to summarize it, use the `get_document_contents` tool to get the contents of the document.",
# "If the user asks a specific question but the document name is not clear, use the `search_latest_document` tool to search the latest document for context.",
# "If the user asks to summarize a document but the document name is not clear, use the `get_latest_document_contents` tool to get the contents of the latest document.",
