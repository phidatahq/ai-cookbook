from phi.utils.log import set_log_level_to_debug

from pdf_ai.tools import PDFTools

set_log_level_to_debug()
pdf_tools = PDFTools(user_id="ab")

# latest_document = pdf_tools.get_latest_document()
# print(latest_document)

# result = pdf_tools.search_latest_document("agreement between")
# print(result)

# document_names = pdf_tools.get_document_names()
# print(document_names)

# search_document = pdf_tools.search_document("agreement", "Hydy Services Agreement")
# print(search_document)

# document_content = pdf_tools.get_document_contents("Hydy Services Agreement")
# print(document_content)
