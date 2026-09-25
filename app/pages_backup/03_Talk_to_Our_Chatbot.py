import streamlit as st
from utils.llm_client import run_llm


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="🌿 CropDoctor AI",
    page_icon="🌿",
    layout="wide"
)


# ==========================================================
# TITLE
# ==========================================================

st.title("🌿 CropDoctor AI")

st.write(
    "Ask your agriculture or plant disease questions."
)


# ==========================================================
# CHAT HISTORY
# ==========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


# ==========================================================
# USER INPUT
# ==========================================================

prompt = st.chat_input(
    "Ask your agriculture question..."
)


# ==========================================================
# CHAT RESPONSE
# ==========================================================

if prompt:

    # User message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)


    # AI response
    with st.chat_message("assistant"):

        with st.spinner(
            "🌿 Thinking..."
        ):

            answer = run_llm(prompt)


        st.markdown(answer)


    # Save AI response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )