from pdf_ai.tools import PDFTools

pdf_tools = PDFTools(user_id="ab")

latest_document = pdf_tools.get_latest_document()
print(latest_document)
