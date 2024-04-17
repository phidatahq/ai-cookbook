import json
from typing import List, Optional

import streamlit as st
from phi.tools.streamlit.components import get_username_sidebar

from medical_ai.assistants import (
    SearchTerms,
    SearchResults,
    search_term_generator,
    arxiv_search_assistant,
    research_editor,
    arxiv_toolkit,
)
from medical_ai.search import exa_search


st.set_page_config(
    page_title="Medical Research AI",
    page_icon=":orange_heart:",
    layout="wide",
)
st.title("Medical Research AI")
st.markdown("##### :orange_heart: built using [phidata](https://github.com/phidatahq/phidata)")

disclaimer = """\
This application is not intended to replace professional medical advice, diagnosis, or treatment. The information provided by our AI technology is based on data input and should not be used as the sole basis for making medical decisions. While we strive to offer accurate and up-to-date medical information, the outputs provided by the AI are predictions and may be subject to inaccuracies.

Please consult with a qualified healthcare provider for any questions concerning your medical condition or treatment. Reliance on any information provided by this application is solely at your own risk. The developers and distributors of this app are not liable for any damages or health complications that may result from users interpreting and using the AI-generated medical information.

Use of this application does not establish a doctor-patient relationship. Remember to always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

By using this app, you agree to the terms outlined in this disclaimer.\
"""
with st.expander(":rainbow[:point_down: Disclaimer]"):
    st.markdown(disclaimer)


def main() -> None:
    # Get username
    # username = get_username_sidebar()
    # if username:
    #     st.sidebar.info(f":female-doctor: User: {username}")
    # else:
    #     st.markdown("---")
    #     st.markdown("#### :female-doctor: Please enter a username")
    #     return

    # Get topic for report
    input_topic = st.text_input(
        ":female-doctor: Enter a topic to generate a report",
        value="AI in Healthcare",
    )
    # Button to generate report
    generate_report = st.button("Generate Report")
    if generate_report:
        st.session_state["topic"] = input_topic

    # Checkboxes for search
    st.sidebar.markdown("## Search Options")
    search_arxiv = st.sidebar.checkbox("Search ArXiv", value=True)
    search_web = st.sidebar.checkbox("Search Web", value=True)
    search_pubmed = st.sidebar.checkbox("Search PubMed", disabled=True)
    search_google_scholar = st.sidebar.checkbox("Search Google Scholar", disabled=True)
    use_cache = st.sidebar.toggle("Use Cache", value=True)
    num_search_terms = st.sidebar.number_input(
        "Number of Search Terms", value=1, min_value=1, max_value=3, help="This will increase latency."
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Trending Topics")
    if st.sidebar.button("AI in Healthcare"):
        st.session_state["topic"] = "AI in Healthcare"

    if "topic" in st.session_state:
        report_topic = st.session_state["topic"]

        search_terms: Optional[SearchTerms] = None
        with st.status("Generating Search Terms", expanded=True) as status:
            with st.container():
                search_terms_container = st.empty()
                search_generator_input = {"topic": report_topic, "num_terms": num_search_terms}
                search_terms = search_term_generator.run(json.dumps(search_generator_input))
                if search_terms:
                    search_terms_container.json(search_terms.model_dump())
            status.update(label="Search Terms Generated", state="complete", expanded=False)

        if not search_terms:
            st.write("Sorry report generation failed. Please try again.")
            return

        arxiv_content: Optional[str] = None
        web_content: Optional[str] = None
        if search_arxiv:
            arxiv_search_results: List[SearchResults] = []
            with st.status("Searching ArXiv (this takes a while)", expanded=True) as status:
                with st.container():
                    search_results_container = st.empty()
                    for search_term in search_terms.terms:
                        search_results = arxiv_search_assistant.run(search_term)
                        if search_results:
                            arxiv_search_results.append(search_results)

                    if len(arxiv_search_results) > 0:
                        search_results_container.json(
                            [result.model_dump() for result in arxiv_search_results]
                        )
                status.update(label="ArXiv Search Complete", state="complete", expanded=False)

            if len(arxiv_search_results) > 0:
                arxiv_paper_ids = []
                for search_result in arxiv_search_results:
                    arxiv_paper_ids.extend([result.id for result in search_result.results])

                if len(arxiv_paper_ids) > 0:
                    with st.status("Reading ArXiv Papers", expanded=True) as status:
                        with st.container():
                            arxiv_paper_ids_container = st.empty()
                            arxiv_content = arxiv_toolkit.read_arxiv_papers(arxiv_paper_ids, pages_to_read=2)
                            arxiv_paper_ids_container.json(arxiv_paper_ids)
                        status.update(label="Reading ArXiv Papers Complete", state="complete", expanded=False)

        if search_web:
            _content = {}
            for search_term in search_terms.terms:
                _content[search_term] = exa_search(search_term)
            web_content = json.dumps(_content, indent=4)

        report_input = ""
        report_input += f"# Topic: {report_topic}\n\n"
        report_input += f"## Search Terms\n\n"
        report_input += f"{search_terms}\n\n"
        if arxiv_content:
            report_input += f"## ArXiv Papers\n\n"
            report_input += "<arxiv_papers>\n\n"
            report_input += f"{arxiv_content}\n\n"
            report_input += "</arxiv_papers>\n\n"
        if web_content:
            report_input += f"## Web Content\n\n"
            report_input += "<web_content>\n\n"
            report_input += f"{web_content}\n\n"
            report_input += "</web_content>\n\n"

        with st.spinner("Generating Report"):
            final_report = ""
            final_report_container = st.empty()
            for delta in research_editor.run(report_input):
                final_report += delta  # type: ignore
                final_report_container.markdown(final_report)

    st.sidebar.markdown("---")
    if st.sidebar.button("Restart"):
        st.rerun()


main()
