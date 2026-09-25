import streamlit as st

from auth.database import create_help_request, get_advisers, get_farmer_help_requests
from auth.session import get_current_user, is_farmer


if not is_farmer():
    st.error("This page is available for farmer accounts.")
    st.stop()

user = get_current_user()

st.markdown(
    """
    <style>
    .help-hero {
        background: linear-gradient(135deg, #134e4a, #0f766e 58%, #2dd4bf);
        color: white;
        padding: 30px clamp(20px, 4vw, 42px);
        border-radius: 22px;
        margin-bottom: 22px;
        box-shadow: 0 14px 32px rgba(15, 118, 110, .18);
    }
    .help-hero h1 { margin: 0; font-size: clamp(28px, 4vw, 44px); }
    .help-hero p { margin: 8px 0 0; color: #d9fffa; }
    .help-title { color: #123c3a; font-size: 22px; font-weight: 800; margin: 22px 0 12px; }
    .request-card { background: #fff; border: 1px solid #d7ebe7; border-radius: 16px; padding: 18px; margin-bottom: 12px; }
    .request-status { color: #0f766e; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; }
    .request-reply { background: #f0fdfa; border-left: 4px solid #14b8a6; border-radius: 10px; padding: 12px 14px; margin-top: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="help-hero">
        <h1>💬 Ask an Adviser</h1>
        <p>Send a crop or farming question to the Smart Crop Advisory team.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="help-title">New adviser request</div>', unsafe_allow_html=True)
with st.form("farmer_help_request_form", clear_on_submit=True):
    subject = st.text_input("Subject", placeholder="Example: Rice leaves have brown spots")
    message = st.text_area(
        "Describe your question",
        placeholder="Tell us the crop, symptoms, location, and what you have already tried.",
        height=150,
    )
    submitted = st.form_submit_button("Send to adviser team", type="primary", use_container_width=True)

    if submitted:
        if not subject.strip() or not message.strip():
            st.error("Please complete the subject and message.")
        elif create_help_request(user["id"], subject, message):
            st.success("Your request was sent. The admin team will reply here.")
            st.rerun()

st.markdown('<div class="help-title">Available advisers</div>', unsafe_allow_html=True)
advisers = get_advisers()
if advisers:
    adviser_columns = st.columns(min(3, len(advisers)))
    for index, adviser in enumerate(advisers):
        with adviser_columns[index % len(adviser_columns)]:
            with st.container(border=True):
                st.subheader(adviser["full_name"])
                st.caption(adviser["specialization"])
                st.write(f"📍 {adviser['location']}")
                st.write(f"📞 {adviser['phone']}")
                st.caption(f"Crops: {adviser['crops']}")
                st.caption(f"Diseases: {adviser['diseases']}")
else:
    st.info("Adviser contacts will appear here after an admin adds them.")

st.markdown('<div class="help-title">My requests</div>', unsafe_allow_html=True)
requests = get_farmer_help_requests(user["id"])

if not requests:
    st.info("You have not sent an adviser request yet.")
else:
    for request in requests:
        status = request["status"]
        with st.container(border=True):
            st.caption(status)
            st.subheader(request["subject"])
            st.write(request["message"])
            if request["reply"]:
                st.success(f"Admin reply: {request['reply']}")
