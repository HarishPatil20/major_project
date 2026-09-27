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
from utils.theme import apply_premium_theme
from utils.live_refresh import live_fragment


if not is_admin():
    st.error("🛡️ Admin access is required to view the Farm Admin Panel.")
    st.stop()

apply_premium_theme()


# ==========================================================
# HELPER DB MUTATIONS FOR ADMIN DIALOGS
# ==========================================================

def delete_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def edit_user_by_id(user_id, full_name, mobile, email=""):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET full_name = ?, mobile = ?, email = ? WHERE id = ?",
            (full_name.strip(), mobile.strip(), email.strip(), user_id)
        )
        conn.commit()
        return True, "Farmer updated successfully."
    except sqlite3.IntegrityError:
        return False, "That mobile number or email is already used by another account."
    except sqlite3.OperationalError as e:
        return False, f"Database is busy, please try again ({e})."
    finally:
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
    st.markdown("### Add New Farmer")
    st.caption("Enter the farmer's details to register them in the system.")
    name = st.text_input("Name", key="add_f_name", placeholder="Enter farmer name")
    phone = st.text_input("Phone", key="add_f_mobile", placeholder="+91 XXXXXXXXXX")
    location = st.text_input("Location", key="add_f_location", placeholder="Enter location")
    
    st.markdown("##### Profile Image Upload")
    uploaded_file = st.file_uploader("Choose profile image", type=["jpg", "jpeg", "png"], key="add_f_img")
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Preview", width=120)
        
    if st.button("Add Farmer", type="primary", use_container_width=True):
        if not name or not phone:
            st.error("Please fill in Name and Phone.")
        else:
            pwd_hash = hash_password("Farmer@123")
            success, msg = create_user(name, phone, f"{phone}@farmer.com", pwd_hash, role="Farmer")
            if success:
                conn = get_connection()
                c = conn.cursor()
                c.execute("UPDATE users SET is_approved = 1, is_verified = 1 WHERE mobile = ?", (phone,))
                conn.commit()
                conn.close()
                st.success("Farmer added successfully.")
                st.rerun()
            else:
                st.error(msg)

@st.dialog("✏️ Edit Farmer")
def show_edit_farmer_modal(farmer_id, current_name, current_mobile, current_email):
    st.markdown(f"### Edit Farmer #{farmer_id}")
    name = st.text_input("Name", value=current_name, key=f"edit_f_name_{farmer_id}")
    phone = st.text_input("Phone", value=current_mobile, key=f"edit_f_mobile_{farmer_id}")
    email = st.text_input("Email", value=current_email or "", key=f"edit_f_email_{farmer_id}")

    if st.button("Update Farmer", type="primary", use_container_width=True):
        if not name or not phone:
            st.error("Name and Phone are required.")
        else:
            success, msg = edit_user_by_id(farmer_id, name, phone, email)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

@st.dialog("➕ Add New Worker")
def show_add_worker_modal():
    st.markdown("### Add New Worker")
    st.caption("Enter the worker's details to register them in the system.")
    c1, c2 = st.columns(2)
    with c1:
        w_name = st.text_input("Name", key="add_w_name", placeholder="Enter worker name")
        w_phone = st.text_input("Phone", key="add_w_phone", placeholder="+91 XXXXXXXXXX")
        w_exp = st.text_input("Experience", key="add_w_exp", placeholder="e.g., 5 years")
        w_spec = st.text_input("Specialization", key="add_w_spec", placeholder="e.g., Tractor Operation")
    with c2:
        w_cat = st.text_input("Category", key="add_w_cat", placeholder="e.g., Heavy Machinery")
        w_loc = st.text_input("Location", key="add_w_loc", placeholder="Enter location")
        w_price = st.text_input("Price", key="add_w_price", placeholder="e.g., ₹500/day")
        w_rating = st.number_input("Rating (0-5)", min_value=0.0, max_value=5.0, value=4.5, step=0.1, key="add_w_rating")

    st.markdown("##### Profile Image Upload")
    uploaded_w_file = st.file_uploader("Choose profile image", type=["jpg", "jpeg", "png"], key="add_w_img")
    if uploaded_w_file is not None:
        st.image(uploaded_w_file, caption="Preview", width=120)

    if st.button("Add Worker", type="primary", use_container_width=True):
        if not w_name or not w_phone or not w_spec:
            st.error("Please fill all required fields.")
        else:
            create_adviser(w_name, w_spec, w_phone, w_loc, w_cat, w_exp)
            st.success("Worker added successfully.")
            st.rerun()

@st.dialog("✏️ Edit Worker")
def show_edit_worker_modal(adv_id, c_name, c_spec, c_phone, c_loc, c_crops, c_dis):
    st.markdown(f"### Edit Worker #{adv_id}")
    w_name = st.text_input("Name", value=c_name, key=f"ew_name_{adv_id}")
    w_phone = st.text_input("Phone", value=c_phone, key=f"ew_phone_{adv_id}")
    w_spec = st.text_input("Specialization", value=c_spec, key=f"ew_spec_{adv_id}")
    w_loc = st.text_input("Location", value=c_loc, key=f"ew_loc_{adv_id}")
    w_crops = st.text_input("Category / Crops", value=c_crops, key=f"ew_crops_{adv_id}")
    w_dis = st.text_input("Experience / Notes", value=c_dis, key=f"ew_dis_{adv_id}")
    
    if st.button("Update Worker", type="primary", use_container_width=True):
        edit_adviser_by_id(adv_id, w_name, w_spec, w_phone, w_loc, w_crops, w_dis)
        st.success("Worker updated successfully.")
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
    .stApp { background: linear-gradient(135deg, #f0fdf4 0%, #eff6ff 100%); }
    .block-container { max-width: 1320px; padding: 1rem 1.5rem 3rem; }
    
    /* Header Bar */
    .admin-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        border-bottom: 1px solid #e5e7eb;
        padding: 16px 24px;
        margin: -1rem -1.5rem 2rem -1.5rem;
    }
    .admin-title-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .admin-title-wrap h1 {
        font-size: 20px;
        font-weight: 700;
        color: #111827;
        margin: 0;
    }
    
    /* Overview Stats Cards */
    .stat-box {
        border-radius: 12px;
        padding: 18px 20px;
    }
    .stat-box-green { background: #f0fdf4; border: 1px solid #bbf7d0; }
    .stat-box-blue { background: #eff6ff; border: 1px solid #bfdbfe; }
    .stat-box-purple { background: #faf5ff; border: 1px solid #e9d5ff; }
    .stat-box-orange { background: #fff7ed; border: 1px solid #fed7aa; }
    
    .stat-title-green { color: #166534; font-size: 15px; font-weight: 600; margin: 0; }
    .stat-val-green { color: #15803d; font-size: 28px; font-weight: 800; margin-top: 4px; }
    
    .stat-title-blue { color: #1e40af; font-size: 15px; font-weight: 600; margin: 0; }
    .stat-val-blue { color: #1d4ed8; font-size: 28px; font-weight: 800; margin-top: 4px; }
    
    .stat-title-purple { color: #6b21a8; font-size: 15px; font-weight: 600; margin: 0; }
    .stat-val-purple { color: #7e22ce; font-size: 28px; font-weight: 800; margin-top: 4px; }
    
    .stat-title-orange { color: #9a3412; font-size: 15px; font-weight: 600; margin: 0; }
    .stat-val-orange { color: #c2410c; font-size: 28px; font-weight: 800; margin-top: 4px; }

    /* Tabs Styling */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: #f3f4f6;
        border-radius: 10px;
        padding: 4px;
        gap: 6px;
    }
    [data-testid="stTabs"] button {
        border-radius: 8px;
        font-weight: 600;
        color: #4b5563;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        background: #ffffff !important;
        color: #111827 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .status-answered { color: #16a34a; font-weight: 700; }
    .status-pending { color: #ca8a04; font-weight: 700; }

    .admin-icon-badge {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, #1E5620, #2D7D32);
        color: #ffffff;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        box-shadow: 0 4px 14px rgba(30,86,32,0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# HEADER BAR
# ==========================================================

head_left, head_right = st.columns([3, 1])

with head_left:
    st.markdown(
        """
        <div class="admin-header">
            <div class="admin-title-wrap">
                <span class="admin-icon-badge">🌿</span>
                <h1>Farm Admin Panel</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with head_right:
    if st.button("🚪 Logout", key="admin_dash_logout_btn", use_container_width=True):
        logout_user()
        st.rerun()


# ==========================================================
# DASHBOARD OVERVIEW STATS CARD
# ==========================================================

with st.container(border=True):
    st.markdown("### 📊 Dashboard Overview")
    
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(
            f"""
            <div class="stat-box stat-box-green">
                <div style="font-size:22px; margin-bottom:4px;">👨‍🌾</div>
                <div class="stat-title-green">Total Farmers</div>
                <div class="stat-val-green">{len(farmers)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with s2:
        st.markdown(
            f"""
            <div class="stat-box stat-box-blue">
                <div style="font-size:22px; margin-bottom:4px;">💼</div>
                <div class="stat-title-blue">Total Workers</div>
                <div class="stat-val-blue">{len(advisers)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with s3:
        st.markdown(
            f"""
            <div class="stat-box stat-box-purple">
                <div style="font-size:22px; margin-bottom:4px;">📈</div>
                <div class="stat-title-purple">This Month (Farmers)</div>
                <div class="stat-val-purple">{len(new_farmers)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with s4:
        st.markdown(
            f"""
            <div class="stat-box stat-box-orange">
                <div style="font-size:22px; margin-bottom:4px;">📊</div>
                <div class="stat-title-orange">This Month (Workers)</div>
                <div class="stat-val-orange">{len(new_advisers)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================================
# 4 MANAGEMENT TABS
# ==========================================================

tab_regs, tab_farmers, tab_workers, tab_expert = st.tabs(
    ["👤 New Regs", "👨‍🌾 Farmers", "💼 Workers", "💬 Ask Expert"]
)


# ----------------------------------------------------------
# TAB 1: PENDING FARMER REGISTRATIONS
# ----------------------------------------------------------
with tab_regs:
    with st.container(border=True):
        st.markdown("### Pending Farmer Registrations")
        
        if not pending:
            st.info("No pending registrations.")
        else:
            for farmer in pending:
                st.markdown("---")
                col_name, col_phone, col_loc, col_act = st.columns([2, 2, 2, 2])
                with col_name:
                    st.write(f"**{farmer['full_name']}**")
                with col_phone:
                    st.write(farmer['mobile'])
                with col_loc:
                    st.write(farmer['email'] or 'N/A')
                with col_act:
                    c_app, c_del = st.columns(2)
                    with c_app:
                        if st.button("Approve", key=f"app_{farmer['id']}", type="primary", use_container_width=True):
                            approve_user(farmer["id"])
                            st.success("Farmer approved.")
                            st.rerun()
                    with c_del:
                        if st.button("🗑️", key=f"del_p_{farmer['id']}", use_container_width=True):
                            delete_user_by_id(farmer["id"])
                            st.warning("Registration deleted.")
                            st.rerun()


# ----------------------------------------------------------
# TAB 2: FARMERS MANAGEMENT
# ----------------------------------------------------------
with tab_farmers:
    with st.container(border=True):
        h_col, b_col = st.columns([4, 1])
        with h_col:
            st.markdown("### Farmers Management")
        with b_col:
            if st.button("➕ Add Farmer", key="open_add_farmer_modal_btn", type="primary", use_container_width=True):
                show_add_farmer_modal()

        if farmers:
            st.markdown("---")
            for f in farmers:
                c_id, c_name, c_phone, c_date, c_act = st.columns([1, 2.5, 2, 2, 2])
                with c_id:
                    st.write(f"#{f['id']}")
                with c_name:
                    st.write(f"**{f['full_name']}**")
                with c_phone:
                    st.write(f['mobile'])
                with c_date:
                    st.write(str(f['created_at'])[:10])
                with c_act:
                    e_btn, d_btn = st.columns(2)
                    with e_btn:
                        if st.button("✏️", key=f"edit_f_btn_{f['id']}", use_container_width=True):
                            show_edit_farmer_modal(f['id'], f['full_name'], f['mobile'], f['email'] or '')
                    with d_btn:
                        if st.button("🗑️", key=f"del_f_btn_{f['id']}", use_container_width=True):
                            delete_user_by_id(f['id'])
                            st.warning(f"Farmer deleted.")
                            st.rerun()
                st.markdown("<hr style='margin:4px 0; border:0; border-top:1px solid #f0f0f0;'>", unsafe_allow_html=True)
        else:
            st.info("No farmers registered yet. Click 'Add Farmer' to get started.")


# ----------------------------------------------------------
# TAB 3: WORKERS MANAGEMENT
# ----------------------------------------------------------
with tab_workers:
    with st.container(border=True):
        hw_col, bw_col = st.columns([4, 1])
        with hw_col:
            st.markdown("### Workers Management")
        with bw_col:
            if st.button("➕ Add Worker", key="open_add_worker_modal_btn", type="primary", use_container_width=True):
                show_add_worker_modal()

        if advisers:
            st.markdown("---")
            for w in advisers:
                c_id, c_name, c_phone, c_spec, c_loc, c_act = st.columns([1, 2, 2, 2, 2, 2])
                with c_id:
                    st.write(f"#{w['id']}")
                with c_name:
                    st.write(f"**{w['full_name']}**")
                with c_phone:
                    st.write(w['phone'])
                with c_spec:
                    st.write(w['specialization'])
                with c_loc:
                    st.write(w['location'])
                with c_act:
                    ew_btn, dw_btn = st.columns(2)
                    with ew_btn:
                        if st.button("✏️", key=f"edit_w_btn_{w['id']}", use_container_width=True):
                            show_edit_worker_modal(w['id'], w['full_name'], w['specialization'], w['phone'], w['location'], w['crops'], w['diseases'])
                    with dw_btn:
                        if st.button("🗑️", key=f"del_w_btn_{w['id']}", use_container_width=True):
                            delete_adviser_by_id(w['id'])
                            st.warning("Worker deleted.")
                            st.rerun()
                st.markdown("<hr style='margin:4px 0; border:0; border-top:1px solid #f0f0f0;'>", unsafe_allow_html=True)
        else:
            st.info("No workers registered yet. Click 'Add Worker' to get started.")


# ----------------------------------------------------------
# TAB 4: ASK EXPERT QUERIES
# ----------------------------------------------------------
with tab_expert:
    with st.container(border=True):
        st.markdown("### Ask Expert Queries")
        st.caption("🔄 Auto-refreshes every few seconds — new farmer questions show up here without reloading the page.")

        @live_fragment("4s")
        def _render_expert_queries():
            # Re-queried fresh on every auto-refresh tick (not the `requests`
            # snapshot taken when the page first loaded), so a question a
            # farmer just submitted appears here within a few seconds.
            live_requests = get_help_requests()

            if not live_requests:
                st.info("No queries yet.")
                return

            st.markdown("---")
            for idx, q in enumerate(live_requests):
                # Wrapped in a form so typing an answer no longer triggers a
                # full-page rerun (and its 4 database queries) on every
                # keystroke — only the Answer/Update click submits it.
                with st.form(key=f"exp_form_{q['id']}"):
                    c_idx, c_quest, c_ans, c_stat, c_act = st.columns([0.5, 3, 3, 1.5, 1.5])
                    with c_idx:
                        st.write(f"#{idx + 1}")
                    with c_quest:
                        st.write(f"**{q['full_name']}**: {q['subject']}")
                        st.caption(q['message'])
                    with c_ans:
                        ans_val = st.text_area(
                            "Answer",
                            value=q['reply'] or "",
                            key=f"exp_ans_area_{q['id']}",
                            height=75,
                            label_visibility="collapsed",
                            placeholder="Write answer..."
                        )
                    with c_stat:
                        if q['status'] in ["Replied", "Answered"]:
                            st.markdown("<span class='status-answered'>Answered</span>", unsafe_allow_html=True)
                        else:
                            st.markdown("<span class='status-pending'>Pending</span>", unsafe_allow_html=True)
                    with c_act:
                        btn_label = "Update" if q['status'] in ["Replied", "Answered"] else "Answer"
                        submitted_answer = st.form_submit_button(btn_label, type="primary", use_container_width=True)

                    if submitted_answer:
                        if ans_val.strip():
                            reply_to_help_request(q['id'], ans_val)
                            st.success("Answer saved successfully!")
                            st.rerun()
                        else:
                            st.error("Write answer first.")
                st.markdown("<hr style='margin:8px 0; border:0; border-top:1px solid #f0f0f0;'>", unsafe_allow_html=True)

        _render_expert_queries()
