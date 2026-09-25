from datetime import datetime

import streamlit as st

from auth.database import (
    approve_user,
    create_adviser,
    get_advisers,
    get_farmers,
    get_help_requests,
    get_pending_farmers,
    reply_to_help_request,
)
from auth.session import is_admin, logout_user


if not is_admin():
    st.error("Admin access is required to view this page.")
    st.stop()

farmers = get_farmers()
pending = get_pending_farmers()
advisers = get_advisers()
requests = get_help_requests()

current_month = datetime.now().strftime("%Y-%m")
new_farmers = [farmer for farmer in farmers if str(farmer["created_at"]).startswith(current_month)]
new_advisers = [adviser for adviser in advisers if str(adviser["created_at"]).startswith(current_month)]

st.markdown(
    """
    <style>
    .stApp { background: #f1faf6; }
    .block-container { max-width: 1180px; padding: 0 0 3rem; }
    .admin-topbar { background: white; border-bottom: 1px solid #d9e5de; margin: 0 -2rem 30px; padding: 16px 2rem; }
    .admin-brand { color: #111827; font-size: 20px; font-weight: 750; }
    .admin-brand span { color: #16a34a; font-size: 30px; vertical-align: middle; margin-right: 9px; }
    [data-testid="stTabs"] { margin-top: 28px; }
    [data-baseweb="tab-list"] { background: #e4efe7; border-radius: 10px; padding: 4px; gap: 4px; }
    [data-baseweb="tab"] { flex: 1; justify-content: center; color: #65806b; border-radius: 8px; }
    [aria-selected="true"][data-baseweb="tab"] { background: white; color: #173c23; }
    [data-testid="stDataFrame"] { border: 1px solid #d8e4dc; border-radius: 10px; overflow: hidden; }
    .stat-card { border-radius: 12px; padding: 18px 16px; min-height: 90px; }
    .stat-card p { margin: 0; font-size: 16px; }
    .stat-card strong { display: block; margin-top: 8px; font-size: 25px; }
    .stat-green { background: #effcf3; color: #047857; }
    .stat-blue { background: #eef5ff; color: #2453c2; }
    .stat-purple { background: #faf2ff; color: #7e22ce; }
    .stat-orange { background: #fff6eb; color: #c2410c; }
    @media (max-width: 800px) {
        .block-container { padding: 0 .7rem 2rem; }
        .admin-topbar { margin: 0 -.7rem 18px; padding: 14px .7rem; }
        [data-baseweb="tab"] { font-size: 11px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

topbar_left, topbar_right = st.columns([4, 1])
with topbar_left:
    st.markdown('<div class="admin-brand"><span>◉</span>Farm Admin Panel</div>', unsafe_allow_html=True)
with topbar_right:
    if st.button("⇥  Logout", key="admin_dashboard_logout", use_container_width=True):
        logout_user()
        st.rerun()

with st.container(border=True):
    st.subheader("♧ Dashboard Overview")
    stat_columns = st.columns(4)
    stat_values = [
        ("Total Farmers", len(farmers), "stat-green"),
        ("Total Workers", len(advisers), "stat-blue"),
        ("This Month (Farmers)", len(new_farmers), "stat-purple"),
        ("This Month (Workers)", len(new_advisers), "stat-orange"),
    ]
    for column, (label, value, class_name) in zip(stat_columns, stat_values):
        with column:
            st.markdown(f'<div class="stat-card {class_name}"><p>{label}</p><strong>{value}</strong></div>', unsafe_allow_html=True)
new_tab, farmers_tab, advisers_tab, expert_tab = st.tabs(
    ["♧  New Registrations", "♧  Farmers", "▣  Workers / Advisers", "♧  Ask Expert"]
)

with new_tab:
    st.subheader("Pending Farmer Registrations")
    if not pending:
        st.info("No pending registrations.")
    else:
        for farmer in pending:
            with st.container(border=True):
                details, action = st.columns([4, 1])
                with details:
                    st.write(f"**{farmer['full_name']}**")
                    st.caption(f"{farmer['mobile']} · {farmer['email']} · OTP verified: {'Yes' if farmer['is_verified'] else 'No'}")
                with action:
                    if st.button("Approve", key=f"admin_approve_{farmer['id']}", type="primary", use_container_width=True):
                        approve_user(farmer["id"])
                        st.success("Member approved.")
                        st.rerun()

with farmers_tab:
    st.subheader("Farmers Management")
    if farmers:
        st.dataframe(
            [
                {
                    "ID": farmer["id"],
                    "Name": farmer["full_name"],
                    "Phone": farmer["mobile"],
                    "Email": farmer["email"],
                    "Registered Date": str(farmer["created_at"])[:10],
                    "Status": "Approved" if farmer["is_approved"] else "Pending",
                }
                for farmer in farmers
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No farmers registered yet.")

with advisers_tab:
    st.subheader("Adviser Management")
    with st.form("admin_adviser_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            adviser_name = st.text_input("Name")
            phone = st.text_input("Phone")
            location = st.text_input("Location")
        with right:
            specialization = st.text_input("Specialization")
            crops = st.text_input("Crops", placeholder="Rice, Tomato, Corn")
            diseases = st.text_input("Diseases", placeholder="Rust, Blight, Smut")
        submitted = st.form_submit_button("+ Add Adviser", type="primary", use_container_width=True)
        if submitted:
            values = [adviser_name, specialization, phone, location, crops, diseases]
            if not all(value.strip() for value in values):
                st.error("Complete every adviser field.")
            else:
                create_adviser(*[value.strip() for value in values])
                st.success("Adviser added.")
                st.rerun()

    if advisers:
        st.dataframe(
            [
                {
                    "Name": adviser["full_name"],
                    "Phone": adviser["phone"],
                    "Specialization": adviser["specialization"],
                    "Crops": adviser["crops"],
                    "Diseases": adviser["diseases"],
                    "Location": adviser["location"],
                }
                for adviser in advisers
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No advisers have been added yet.")

with expert_tab:
    st.subheader("Ask Expert Queries")
    if not requests:
        st.info("No farmer questions yet.")
    else:
        for request in requests:
            with st.container(border=True):
                status, farmer = st.columns([1, 4])
                with status:
                    st.write(f"**{request['status']}**")
                with farmer:
                    st.write(f"**{request['full_name']}** · {request['subject']}")
                    st.caption(f"{request['mobile']} · {request['created_at'][:16].replace('T', ' ')}")
                st.write(request["message"])
                answer = st.text_area("Answer", value=request["reply"] or "", key=f"admin_answer_{request['id']}", height=100)
                if st.button("Update reply", key=f"admin_update_{request['id']}", type="primary", use_container_width=True):
                    if answer.strip():
                        reply_to_help_request(request["id"], answer)
                        st.success("Answer sent to member.")
                        st.rerun()
                    else:
                        st.error("Write an answer first.")

