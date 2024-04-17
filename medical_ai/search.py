from phi.tools.exa import ExaTools

exa_tools = ExaTools()


def exa_search(query: str) -> str:
    return exa_tools.search_exa_with_contents(query=query)
