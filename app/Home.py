import streamlit as st

from phi.tools.streamlit.components import check_password

st.set_page_config(
    page_title="AI Apps",
    page_icon=":snowman:",
)
st.title(":snowman: AI Apps")
st.markdown('<a href="https://github.com/phidatahq/phidata"><h4>by phidata</h4></a>', unsafe_allow_html=True)


def main() -> None:
    st.markdown("### Select an App:")
    st.markdown("#### 1. PDF Assistant: Chat with PDFs")
    st.markdown("#### 2. Vision Assistant: Chat with images")
    st.markdown("#### 3. Website Assistant: Chat with website contents")

    st.sidebar.success("Select App from above")


if check_password():
    main()
