import sqlite3
from datetime import datetime
import streamlit as st

from auth.database import (
    get_connection,
    approve_user,
    create_user,
    create_adviser,
    get_advisers,
    get_farmers,
    get_help_requests,
    get_pending_farmers,
    reply_to_help_request,
)
from auth.session import is_admin, logout_user
from auth.authentication import hash_password


if not is_admin():
    st.error("🛡️ Admin access is required to view the Farm Admin Panel.")
    st.stop()


# ==========================================================
# HELPER DB MUTATIONS FOR ADMIN DIALOGS
# ==========================================================

def delete_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def edit_user_by_id(user_id, full_name, mobile, email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET full_name = ?, mobile = ?, email = ? WHERE id = ?",
        (full_name.strip(), mobile.strip(), email.strip(), user_id)
    )
    conn.commit()
    conn.close()

def delete_adviser_by_id(adviser_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM advisers WHERE id = ?", (adviser_id,))
    conn.commit()
    conn.close()

def edit_adviser_by_id(adviser_id, full_name, specialization, phone, location, crops, diseases):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE advisers
        SET full_name = ?, specialization = ?, phone = ?, location = ?, crops = ?, diseases = ?
        WHERE id = ?
        """,
        (full_name.strip(), specialization.strip(), phone.strip(), location.strip(), crops.strip(), diseases.strip(), adviser_id)
    )
    conn.commit()
    conn.close()


# ==========================================================
# ADMIN DIALOG MODALS
# ==========================================================

@st.dialog("➕ Add New Farmer")
def show_add_farmer_modal():
    st.markdown("### Add Farmer Record")
    name = st.text_input("Full Name", key="add_f_name")
    mobile = st.text_input("Mobile Number (10 digits)", max_chars=10, key="add_f_mobile")
    email = st.text_input("Email Address", key="add_f_email")
    password = st.text_input("Temporary Password", type="password", key="add_f_pass")
    
    st.markdown("##### 📷 Profile Photo / Identity Upload Preview")
    uploaded_file = st.file_uploader("Choose a profile photo", type=["jpg", "jpeg", "png"], key="add_f_img")
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Farmer Photo Preview", width=160)
        
    if st.button("Save Farmer Record", type="primary", use_container_width=True):
        if not name or not mobile or not password:
            st.error("Please fill in Name, Mobile Number, and Password.")
        else:
            pwd_hash = hash_password(password)
            success, msg = create_user(name, mobile, email, pwd_hash, role="Farmer")
            if success:
                # Auto-approve admin created farmer
                conn = get_connection()
                c = conn.cursor()
                c.execute("UPDATE users SET is_approved = 1, is_verified = 1 WHERE mobile = ?", (mobile,))
                conn.commit()
                conn.close()
                st.success("🎉 Farmer added and approved successfully.")
                st.rerun()
            else:
                st.error(msg)

@st.dialog("✏️ Edit Farmer Details")
def show_edit_farmer_modal(farmer_id, current_name, current_mobile, current_email):
    st.markdown(f"### Edit Farmer #{farmer_id}")
    name = st.text_input("Full Name", value=current_name, key=f"edit_f_name_{farmer_id}")
    mobile = st.text_input("Mobile Number", value=current_mobile, key=f"edit_f_mobile_{farmer_id}")
    email = st.text_input("Email Address", value=current_email or "", key=f"edit_f_email_{farmer_id}")
    
    if st.button("Update Farmer Record", type="primary", use_container_width=True):
        if not name or not mobile:
            st.error("Name and Mobile Number are required.")
        else:
            edit_user_by_id(farmer_id, name, mobile, email)
            st.success("Farmer details updated.")
            st.rerun()

@st.dialog("➕ Add New Worker / Adviser")
def show_add_worker_modal():
    st.markdown("### Add Agricultural Worker / Adviser")
    c1, c2 = st.columns(2)
    with c1:
        w_name = st.text_input("Full Name", key="add_w_name")
        w_phone = st.text_input("Phone Number", key="add_w_phone")
        w_loc = st.text_input("District / Location", key="add_w_loc")
    with c2:
        w_spec = st.text_input("Specialization", placeholder="e.g. Agronomist, Soil Specialist", key="add_w_spec")
        w_crops = st.text_input("Covered Crops", placeholder="Paddy, Arecanut, Maize", key="add_w_crops")
        w_diseases = st.text_input("Specialized Diseases", placeholder="Rust, Blight, Rot", key="add_w_dis")

    if st.button("Save Worker Record", type="primary", use_container_width=True):
        if not w_name or not w_phone or not w_spec:
            st.error("Name, Phone, and Specialization are required.")
        else:
            create_adviser(w_name, w_spec, w_phone, w_loc, w_crops, w_diseases)
            st.success("Worker / Adviser registered successfully.")
            st.rerun()

@st.dialog("✏️ Edit Worker / Adviser")
def show_edit_worker_modal(adv_id, c_name, c_spec, c_phone, c_loc, c_crops, c_dis):
    st.markdown(f"### Edit Worker #{adv_id}")
    w_name = st.text_input("Full Name", value=c_name, key=f"ew_name_{adv_id}")
    w_spec = st.text_input("Specialization", value=c_spec, key=f"ew_spec_{adv_id}")
    w_phone = st.text_input("Phone Number", value=c_phone, key=f"ew_phone_{adv_id}")
    w_loc = st.text_input("Location", value=c_loc, key=f"ew_loc_{adv_id}")
    w_crops = st.text_input("Crops", value=c_crops, key=f"ew_crops_{adv_id}")
    w_dis = st.text_input("Diseases", value=c_dis, key=f"ew_dis_{adv_id}")
    
    if st.button("Update Worker Record", type="primary", use_container_width=True):
        edit_adviser_by_id(adv_id, w_name, w_spec, w_phone, w_loc, w_crops, w_dis)
        st.success("Worker details updated.")
        st.rerun()


# ==========================================================
# FETCH DATA
# ==========================================================

farmers = get_farmers()
pending = get_pending_farmers()
advisers = get_advisers()
requests = get_help_requests()

current_month = datetime.now().strftime("%Y-%m")
new_farmers = [f for f in farmers if str(f["created_at"]).startswith(current_month)]
new_advisers = [a for a in advisers if str(a["created_at"]).startswith(current_month)]


# ==========================================================
# ADMIN STYLING
# ==========================================================

st.markdown(
    """
    <style>
    .stApp { background: #f4f6f0; }
    .block-container { max-width: 1320px; padding: 1.5rem 1.5rem 3rem; }
    
    /* Top Header Bar */
    .admin-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        border: 1px solid #dce9de;
        border-radius: 18px;
        padding: 16px 26px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(30, 86, 32, 0.06);
    }
    .admin-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 24px;
        font-weight: 800;
        color: #1E5620;
    }
    .admin-shield-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: linear-gradient(135deg, #1E5620, #2D7D32);
        color: #E5A93C;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: 0 6px 16px rgba(30, 86, 32, 0.2);
    }

    /* Metric Cards */
    .stat-card-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .stat-card {
        border-radius: 16px;
        padding: 20px;
        color: white;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        transition: transform 0.2s ease;
    }
    .stat-card:hover { transform: translateY(-2px); }
    .stat-card-title { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.92; }
    .stat-card-value { font-size: 34px; font-weight: 850; margin-top: 8px; }

    .stat-card-green { background: linear-gradient(135deg, #15803D, #22C55E); }
    .stat-card-blue { background: linear-gradient(135deg, #0284C7, #38BDF8); }
    .stat-card-purple { background: linear-gradient(135deg, #7E22CE, #A855F7); }
    .stat-card-orange { background: linear-gradient(135deg, #C2410C, #F97316); }

    /* Tabs Styling */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: #e6efe8;
        border-radius: 12px;
        padding: 6px;
        gap: 8px;
    }
    [data-testid="stTabs"] button {
        border-radius: 9px;
        font-weight: 700;
        color: #4A3525;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        background: #ffffff !important;
        color: #1E5620 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .table-container {
        background: #ffffff;
        border: 1px solid #dce9de;
        border-radius: 16px;
        padding: 20px;
        margin-top: 16px;
    }
    .pending-row {
        background: #f8faf8;
        border: 1px solid #e1ebe3;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .badge-pending-tag { background: #fef3c7; color: #92400e; padding: 4px 10px; border-radius: 10px; font-size: 11px; font-weight: 800; }
    .badge-approved-tag { background: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 10px; font-size: 11px; font-weight: 800; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# TOP NAVIGATION HEADER
# ==========================================================

head_col1, head_col2 = st.columns([3, 1])
with head_col1:
    st.markdown(
        """
        <div class="admin-topbar">
            <div class="admin-brand">
                <div class="admin-shield-icon">🛡️</div>
                <div>
                    <div>Farm Admin Panel</div>
                    <div style="font-size:12px; font-weight:600; color:#6D4C41;">Smart Advisory Platform & Directory Management</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with head_col2:
    if st.button("🚪 Logout Admin", key="admin_top_logout", type="secondary", use_container_width=True):
        logout_user()
        st.rerun()


# ==========================================================
# 4 METRIC OVERVIEW CARDS
# ==========================================================

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f"""
        <div class="stat-card stat-card-green">
            <div class="stat-card-title">👨‍🌾 Total Farmers</div>
            <div class="stat-card-value">{len(farmers)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m2:
    st.markdown(
        f"""
        <div class="stat-card stat-card-blue">
            <div class="stat-card-title">🧑‍🌾 Total Workers</div>
            <div class="stat-card-value">{len(advisers)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m3:
    st.markdown(
        f"""
        <div class="stat-card stat-card-purple">
            <div class="stat-card-title">📅 Monthly Farmers</div>
            <div class="stat-card-value">{len(new_farmers)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m4:
    st.markdown(
        f"""
        <div class="stat-card stat-card-orange">
            <div class="stat-card-title">⚡ Monthly Workers</div>
            <div class="stat-card-value">{len(new_advisers)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================================
# 4 MAIN MANAGEMENT TABS / VIEWS
# ==========================================================

tab_pending, tab_farmers, tab_workers, tab_expert = st.tabs(
    ["⏳ Pending Registrations", "👨‍🌾 Farmers Directory", "🧑‍🌾 Workers Directory", "💬 Ask Expert Q&A Panel"]
)


# ----------------------------------------------------------
# TAB 1: PENDING FARMER REGISTRATIONS TABLE
# ----------------------------------------------------------
with tab_pending:
    st.subheader("📋 Pending Farmer Registrations")
    st.caption("Review new farmer sign-ups requiring admin authorization.")
    
    if not pending:
        st.info("🎉 All clear! There are no pending farmer registrations.")
    else:
        for farmer in pending:
            with st.container(border=True):
                col_info, col_btn1, col_btn2 = st.columns([4, 1.2, 1.2])
                with col_info:
                    st.markdown(f"**👤 {farmer['full_name']}** &nbsp; <span class='badge-pending-tag'>Pending Approval</span>", unsafe_allow_html=True)
                    st.caption(f"📱 Phone: {farmer['mobile']} | ✉️ Email: {farmer['email']} | OTP Verified: {'Yes' if farmer['is_verified'] else 'No'} | Joined: {str(farmer['created_at'])[:10]}")
                
                with col_btn1:
                    if st.button("✅ Approve", key=f"app_btn_{farmer['id']}", type="primary", use_container_width=True):
                        approve_user(farmer["id"])
                        st.success(f"Approved {farmer['full_name']}.")
                        st.rerun()
                        
                with col_btn2:
                    if st.button("🗑️ Delete", key=f"del_pending_{farmer['id']}", use_container_width=True):
                        delete_user_by_id(farmer["id"])
                        st.warning(f"Registration for {farmer['full_name']} removed.")
                        st.rerun()


# ----------------------------------------------------------
# TAB 2: FARMERS DIRECTORY TABLE
# ----------------------------------------------------------
with tab_farmers:
    header_col, action_col = st.columns([4, 1])
    with header_col:
        st.subheader("👨‍🌾 Farmers Directory")
        st.caption("View, search, edit, and manage registered farmers.")
    with action_col:
        if st.button("➕ Add Farmer", key="btn_open_add_farmer", type="primary", use_container_width=True):
            show_add_farmer_modal()

    if farmers:
        for f in farmers:
            with st.container(border=True):
                c_detail, c_edit, c_del = st.columns([4, 1, 1])
                with c_detail:
                    status_badge = "<span class='badge-approved-tag'>Active</span>" if f["is_approved"] else "<span class='badge-pending-tag'>Pending</span>"
                    st.markdown(f"**👤 {f['full_name']}** &nbsp; {status_badge}", unsafe_allow_html=True)
                    st.caption(f"ID: #{f['id']} | 📞 Phone: {f['mobile']} | ✉️ Email: {f['email']} | Joined: {str(f['created_at'])[:10]}")
                with c_edit:
                    if st.button("✏️ Edit", key=f"btn_ef_{f['id']}", use_container_width=True):
                        show_edit_farmer_modal(f['id'], f['full_name'], f['mobile'], f['email'])
                with c_del:
                    if st.button("🗑️ Delete", key=f"btn_df_{f['id']}", use_container_width=True):
                        delete_user_by_id(f['id'])
                        st.warning(f"Farmer record #{f['id']} deleted.")
                        st.rerun()
    else:
        st.info("No farmers registered in the system yet.")


# ----------------------------------------------------------
# TAB 3: WORKERS DIRECTORY TABLE
# ----------------------------------------------------------
with tab_workers:
    header_col, action_col = st.columns([4, 1])
    with header_col:
        st.subheader("🧑‍🌾 Workers & Field Advisers Directory")
        st.caption("Manage agricultural extension officers and specialists.")
    with action_col:
        if st.button("➕ Add Worker", key="btn_open_add_worker", type="primary", use_container_width=True):
            show_add_worker_modal()

    if advisers:
        for adv in advisers:
            with st.container(border=True):
                c_info, c_edit, c_del = st.columns([4, 1, 1])
                with c_info:
                    st.markdown(f"**🧑‍🌾 {adv['full_name']}** &nbsp; <span style='color:#E5A93C; font-weight:700;'>({adv['specialization']})</span>", unsafe_allow_html=True)
                    st.caption(f"📍 Location: {adv['location']} | 📞 Phone: {adv['phone']}")
                    st.caption(f"Crops: {adv['crops']} | Diseases: {adv['diseases']}")
                with c_edit:
                    if st.button("✏️ Edit", key=f"btn_ew_{adv['id']}", use_container_width=True):
                        show_edit_worker_modal(adv['id'], adv['full_name'], adv['specialization'], adv['phone'], adv['location'], adv['crops'], adv['diseases'])
                with c_del:
                    if st.button("🗑️ Delete", key=f"btn_dw_{adv['id']}", use_container_width=True):
                        delete_adviser_by_id(adv['id'])
                        st.warning(f"Worker {adv['full_name']} deleted.")
                        st.rerun()
    else:
        st.info("No advisers/workers registered yet.")


# ----------------------------------------------------------
# TAB 4: ASK EXPERT Q&A PANEL
# ----------------------------------------------------------
with tab_expert:
    st.subheader("💬 Ask Expert Q&A Queue")
    st.caption("Respond to farmer inquiries and update resolution status.")
    
    if not requests:
        st.info("No farmer questions in queue.")
    else:
        for req in requests:
            with st.container(border=True):
                status_color = "#166534" if req["status"] in ["Replied", "Answered"] else "#92400e"
                st.markdown(f"<span style='color:{status_color}; font-weight:800;'>● Status: {req['status']}</span>", unsafe_allow_html=True)
                st.markdown(f"### ❓ {req['subject']}")
                st.caption(f"Submitted by **{req['full_name']}** (📞 {req['mobile']}) on {req['created_at'][:16].replace('T', ' ')}")
                st.write(f"**Farmer Question:** {req['message']}")
                
                reply_input = st.text_area("Answer / Advisory Reply", value=req["reply"] or "", key=f"admin_ans_area_{req['id']}", height=90)
                
                if st.button("Send & Update Status →", key=f"admin_send_ans_{req['id']}", type="primary", use_container_width=True):
                    if reply_input.strip():
                        reply_to_help_request(req["id"], reply_input)
                        st.success("✅ Reply sent and status updated to Replied.")
                        st.rerun()
                    else:
                        st.error("Please type a response before submitting.")
