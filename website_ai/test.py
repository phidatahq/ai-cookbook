from pdf_ai.assistant import get_pdf_assistant

pdf_assistant = get_pdf_assistant(user_id="yash", debug_mode=True)

# pdf_assistant.print_response("Who is the agreement between?")
pdf_assistant.print_response("describe this pdf")
