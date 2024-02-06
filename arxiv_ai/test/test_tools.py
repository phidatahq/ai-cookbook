from phi.utils.log import set_log_level_to_debug

from arxiv_ai.tools import ArxivTools

set_log_level_to_debug()
arxiv_tools = ArxivTools(user_id="ab")

# add_to_knowledge_base = arxiv_tools.add_arxiv_results_to_knowledge_base(query="FlashAttention")
# print(add_to_knowledge_base)

flash_attention_docs = arxiv_tools.get_document_summaries(query="FlashAttention")
# print(flash_attention_docs)
