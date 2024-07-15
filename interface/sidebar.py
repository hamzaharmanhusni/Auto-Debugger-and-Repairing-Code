import streamlit as st
from PIL import Image
from interface.faq import faq
from dotenv import load_dotenv
import os

load_dotenv()


def sidebar():
    with st.sidebar:
        st.markdown(
            "## How to use\n"
            "1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) below🔑\n"  # noqa: E501
            "2. Upload path file or type the code📄\n"
            "3. Ask requirement to application💬\n"
        )
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="Paste your OpenAI API key here (sk-...)",
            help="You can get your API key from https://platform.openai.com/account/api-keys.",  # noqa: E501
            value=os.environ.get("OPENAI_API_KEY", None)
            or st.session_state.get("OPENAI_API_KEY", "")
        )

        st.session_state["OPENAI_API_KEY"] = api_key_input
        # st.markdown("**Flow Autocode Debugger**")
        # image = Image.open('.\\core\\graph_image.png')
        # st.image(image, caption="Flowchart autocode debugger")
        st.markdown("\n\n---")
        st.markdown("# About")
        st.markdown(
            "📖Auto Debugger allows you to ask questions about your identify "
            "your code and the the error detected also refined code "
        )
        st.markdown(
            "This tool is a work in progress. "
        )
        st.markdown("---")

        # faq()
