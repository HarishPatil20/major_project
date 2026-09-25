import streamlit as st

from utils.llm_client import run_llm


st.markdown(
    """
    <style>
    .assistant-hero {
        background: linear-gradient(135deg, #172554 0%, #1e3a8a 55%, #2563eb 100%);
        color: white;
        padding: 30px clamp(20px, 4vw, 42px);
        border-radius: 22px;
        margin-bottom: 20px;
        box-shadow: 0 14px 32px rgba(30, 58, 138, 0.2);
    }
    .assistant-hero h1 { margin: 0; font-size: clamp(28px, 4vw, 44px); }
    .assistant-hero p { margin: 9px 0 0; opacity: 0.88; font-size: 15px; }
    .assistant-panel {
        background: #ffffff;
        border: 1px solid #dbeafe;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 7px 22px rgba(15, 23, 42, 0.05);
    }
    .assistant-kicker { color: #2563eb; font-size: 12px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; }
    .assistant-title { color: #0f172a; font-size: 21px; font-weight: 800; margin-top: 5px; }
    .assistant-copy { color: #64748b; font-size: 14px; margin-top: 5px; }
    @media (max-width: 640px) {
        .assistant-hero { border-radius: 16px; padding: 24px 20px; }
        .assistant-panel { padding: 16px; border-radius: 14px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="assistant-hero">
        <h1>🤖 Farmer Assistant</h1>
        <p>Practical guidance for crop health, irrigation, pests, soil, and everyday farm decisions.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "assistant_notice" not in st.session_state:
    st.session_state.assistant_notice = None

intro_col, action_col = st.columns([4, 1])
with intro_col:
    st.markdown(
        """
        <div class="assistant-panel">
            <div class="assistant-kicker">Field support</div>
            <div class="assistant-title">What is happening in your field?</div>
            <div class="assistant-copy">Describe the crop, symptoms, location, and how long the problem has been present.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with action_col:
    if st.button("Clear chat", use_container_width=True, key="clear_assistant_chat"):
        st.session_state.messages = []
        st.session_state.assistant_notice = "Conversation cleared."
        st.rerun()

if st.session_state.assistant_notice:
    st.info(st.session_state.assistant_notice)
    st.session_state.assistant_notice = None

st.markdown('<div class="assistant-kicker">Try a question</div>', unsafe_allow_html=True)
quick_cols = st.columns(3)
quick_prompts = [
    "Why are my crop leaves turning yellow?",
    "How often should I irrigate tomato plants?",
    "How can I control pests naturally?",
]
for index, quick_prompt in enumerate(quick_prompts):
    with quick_cols[index]:
        if st.button(quick_prompt, use_container_width=True, key=f"quick_prompt_{index}"):
            st.session_state.pending_prompt = quick_prompt

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask about your crop or farm...")
prompt = prompt or st.session_state.pop("pending_prompt", None)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Preparing practical advice..."):
            answer = run_llm(prompt)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
