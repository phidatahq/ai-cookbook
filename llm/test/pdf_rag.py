from llm.conversations.pdf_rag import get_pdf_rag_conversation

pdf_rag_conversation = get_pdf_rag_conversation()

LOAD_KNOWLEDGE_BASE = True
if LOAD_KNOWLEDGE_BASE and pdf_rag_conversation.knowledge_base:
    pdf_rag_conversation.knowledge_base.load(recreate=False)

pdf_rag_conversation.print_response("Tell me about food safety?")
# pdf_rag_conversation.print_response("How do I make chicken curry?")
# pdf_rag_conversation.print_response("Summarize our conversation")
