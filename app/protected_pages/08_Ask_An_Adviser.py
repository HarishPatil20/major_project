import streamlit as st

from auth.database import create_help_request, get_advisers, get_farmer_help_requests
from auth.session import get_current_user, is_farmer
from utils.theme import apply_premium_theme
from utils.live_refresh import live_fragment


if not is_farmer():
    st.error("This page is available for farmer accounts.")
    st.stop()

apply_premium_theme()

user = get_current_user()

st.markdown(
    """
    <style>
    .stApp { background: #f4f6f0; }
    .help-hero {
        background: linear-gradient(135deg, #1E5620 0%, #2D7D32 60%, #E5A93C 100%);
        color: white;
        padding: 32px clamp(20px, 4vw, 42px);
        border-radius: 22px;
        margin-bottom: 22px;
        box-shadow: 0 14px 32px rgba(30, 86, 32, 0.2);
    }
    .help-hero h1 { margin: 0; font-size: clamp(28px, 4vw, 42px); font-weight: 800; }
    .help-hero p { margin: 8px 0 0; color: #F5F5DC; font-size: 15px; }
    .help-title { color: #1E5620; font-size: 22px; font-weight: 800; margin: 24px 0 14px; display: flex; align-items: center; gap: 8px; }
    
    .badge-pending {
        background: #fef3c7;
        color: #92400e;
        border: 1px solid #fcd34d;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-answered {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #86efac;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .adviser-card {
        background: #ffffff;
        border: 1px solid #dce9de;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.04);
        margin-bottom: 14px;
    }
    .adviser-name { color: #1E5620; font-size: 18px; font-weight: 800; margin-bottom: 2px; }
    .adviser-spec { color: #E5A93C; font-weight: 700; font-size: 13px; margin-bottom: 10px; }
    .adviser-tag { background: #f0f7f1; color: #1E5620; border-radius: 8px; padding: 4px 8px; font-size: 11px; font-weight: 600; display: inline-block; margin-right: 4px; margin-top: 4px; }
    
    .reply-box {
        background: #f0f7f1;
        border-left: 4px solid #1E5620;
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 12px;
        color: #1E5620;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="help-hero">
        <h1>💬 Ask an Adviser & Field Support</h1>
        <p>Direct communication channel with agricultural extension specialists & crop doctors.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="help-title">✍️ Submit New Adviser Request</div>', unsafe_allow_html=True)

with st.container(border=True):
    with st.form("farmer_help_request_form", clear_on_submit=True):
        subject = st.text_input("Query Subject", placeholder="Example: Yellow leaf spots on tomato plants")
        message = st.text_area(
            "Detailed Description",
            placeholder="Describe the crop variety, symptoms, location, affected area, and any pesticides applied...",
            height=130,
        )
        submitted = st.form_submit_button("Send Query to Adviser Team →", type="primary", use_container_width=True)

        if submitted:
            if not subject.strip() or not message.strip():
                st.error("Please fill in both the subject and detailed question.")
            elif create_help_request(user["id"], subject, message):
                st.success("🎉 Your question has been submitted to the agricultural adviser team.")
                st.rerun()

st.markdown('<div class="help-title">🧑‍🌾 Available Field Advisers</div>', unsafe_allow_html=True)


@live_fragment("6s")
def _render_advisers():
    # Re-queried fresh on every tick, so an adviser the admin just added or
    # edited shows up here without the farmer needing to reload the page.
    advisers = get_advisers()

    if advisers:
        cols = st.columns(min(3, len(advisers)))
        for idx, adv in enumerate(advisers):
            with cols[idx % len(cols)]:
                st.markdown(
                    f"""
                    <div class="adviser-card">
                        <div class="adviser-name">🧑‍🌾 {adv['full_name']}</div>
                        <div class="adviser-spec">{adv['specialization']}</div>
                        <div style="font-size:13px; color:#4A3525; margin-bottom:6px;">📍 {adv['location']} &nbsp;|&nbsp; 📞 {adv['phone']}</div>
                        <div>
                            <span class="adviser-tag">🌾 Crops: {adv['crops']}</span>
                            <span class="adviser-tag">🦠 Diseases: {adv['diseases']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("No adviser contacts listed yet. Admin can register advisers via the Admin Panel.")


_render_advisers()

st.markdown('<div class="help-title">📋 My Submitted Queries & Answers</div>', unsafe_allow_html=True)
st.caption("🔄 Auto-refreshes every few seconds — an adviser's reply appears here without reloading the page.")


@live_fragment("4s")
def _render_my_queries():
    # Re-queried fresh on every tick, so an adviser's reply appears here
    # within a few seconds of being saved on the Admin side.
    requests = get_farmer_help_requests(user["id"])

    if not requests:
        st.info("You haven't submitted any adviser questions yet. Use the form above to submit your first question.")
        return

    for req in requests:
        is_answered = req["status"] in ["Replied", "Answered"]
        badge_html = '<span class="badge-answered">Answered</span>' if is_answered else '<span class="badge-pending">Pending Review</span>'

        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <h3 style="margin:0; color:#1E5620; font-size:18px;">{req['subject']}</h3>
                    {badge_html}
                </div>
                <div style="font-size:12px; color:#777; margin-bottom:8px;">Submitted on: {req['created_at'][:16].replace('T', ' ')}</div>
                <div style="font-size:14px; color:#333; line-height:1.5;">{req['message']}</div>
                """,
                unsafe_allow_html=True
            )

            if req["reply"]:
                st.markdown(
                    f"""
                    <div class="reply-box">
                        <strong>👨‍🌾 Expert Advisory Response:</strong><br>
                        {req['reply']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


_render_my_queries()
