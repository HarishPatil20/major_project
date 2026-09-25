import base64
import streamlit as st

from auth.authentication import (
    register_user,
    authenticate_user,
    create_login_otp,
    verify_login_otp,
    create_password_reset_otp,
    reset_password,
    get_login_status,
    validate_mobile,
    validate_email,
    validate_password,
)

from auth.database import get_user_by_mobile
from auth.database import get_pending_farmers, approve_user

from auth.session import (
    initialize_session,
    create_login_session,
    logout_user,
    is_authenticated,
    is_admin,
    get_current_user,
)

import os
import runpy


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Smart Crop Advisory",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# SESSION INITIALIZATION
# ==========================================================

initialize_session()


# ==========================================================
# GLOBAL CSS
# ==========================================================

st.markdown(
    """
<style>
.main {
    background-color: #f7faf7;
}
.brand {
    text-align: center;
    padding: 35px 0 20px 0;
}
.brand-title {
    font-size: 42px;
    font-weight: 800;
    color: #176b2c;
    margin-bottom: 8px;
}
.brand-subtitle {
    font-size: 18px;
    font-weight: 600;
    color: #4CAF50;
}
.auth-container {
    max-width: 900px;
    margin: auto;
}
.auth-hero {
    background: linear-gradient(135deg, #123524 0%, #1f6b45 58%, #66a86f 100%);
    border-radius: 24px;
    color: white;
    padding: clamp(24px, 4vw, 44px);
    margin: 0 auto 24px;
    max-width: 1180px;
    box-shadow: 0 18px 42px rgba(18, 53, 36, 0.2);
}
.auth-hero-copy {
    padding: 8px 0;
}
.auth-hero-eyebrow {
    color: #d5f5d8;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.auth-hero-title {
    font-size: clamp(30px, 4vw, 48px);
    font-weight: 850;
    line-height: 1.08;
    margin: 12px 0 10px;
}
.auth-hero-text {
    color: #e3f4e5;
    font-size: 15px;
    line-height: 1.55;
    max-width: 520px;
}
.auth-hero-image {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,.35);
}
.auth-panel {
    background: #ffffff;
    border: 1px solid #dbe8dd;
    border-radius: 20px;
    padding: clamp(18px, 3vw, 30px);
    max-width: 760px;
    margin: 0 auto;
    box-shadow: 0 10px 28px rgba(20, 54, 27, 0.06);
}
.reset-box {
    background: #f1f8f2;
    border: 1px solid #c8e6c9;
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
}
.reset-title {
    text-align: center;
    color: #2E7D32;
    font-weight: 700;
}
@media (max-width: 700px) {
    .auth-hero { border-radius: 18px; padding: 22px; }
    .auth-hero-image { margin-top: 18px; }
    .auth-panel { border-radius: 16px; padding: 18px 14px; }
}
.security-box {
    background: #eef8ef;
    border-left: 5px solid #2e8b45;
    padding: 15px;
    border-radius: 8px;
    margin-top: 15px;
}
.protected-banner {
    background: #eaf6ec;
    border: 1px solid #b7d9bd;
    border-radius: 12px;
    padding: 18px;
    margin: 15px 0;
}
</style>
""",
    unsafe_allow_html=True,
)


# ==========================================================
# AUTHENTICATION PAGE
# ==========================================================

def show_authentication():

    # ======================================================
    # BRAND HEADER
    # ======================================================

    hero_image = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "assets",
        "welcome_page.png",
    )

    image_data = ""
    if os.path.exists(hero_image):
        with open(hero_image, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("ascii")

    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                linear-gradient(120deg, rgba(6, 91, 35, .96), rgba(16, 121, 54, .86)),
                url(data:image/png;base64,{image_data});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .block-container {{ max-width: 960px; padding-top: 5vh; }}
        .login-brand {{ text-align: center; color: white; margin-bottom: 22px; }}
        .login-mark {{ display: inline-flex; align-items: center; justify-content: center; width: 54px; height: 54px; border-radius: 14px; background: #f4c430; color: #176b2c; font-size: 30px; margin-bottom: 10px; }}
        .login-brand h1 {{ color: white; font-size: clamp(28px, 4vw, 38px); margin: 0; }}
        .login-brand p {{ color: #ccebd0; margin: 6px 0 0; font-size: 14px; }}
        [data-testid="stTabs"] {{ background: rgba(255,255,255,.97); border-radius: 15px; padding: 16px 22px 24px; box-shadow: 0 18px 45px rgba(0,0,0,.2); }}
        [data-testid="stTabs"] [data-baseweb="tab-list"] {{ justify-content: center; gap: 18px; }}
        [data-testid="stTabs"] button {{ color: #53705a; font-weight: 700; }}
        [data-testid="stTabs"] button[aria-selected="true"] {{ color: #16833a; }}
        [data-testid="stTextInput"] input {{ border-radius: 9px; background: #fbfdfb; }}
        [data-testid="stButton"] button[kind="primary"] {{ background: linear-gradient(90deg, #1fc52d, #16ae2a); border: 0; border-radius: 9px; min-height: 44px; font-weight: 800; }}
        .login-security {{ background: #eff5f0; color: #7a8e7e; border-radius: 10px; padding: 11px 13px; margin-top: 17px; font-size: 12px; }}
        .admin-login-head {{ text-align: center; padding: 4px 0 12px; }}
        .admin-login-icon {{ display: inline-flex; align-items: center; justify-content: center; width: 54px; height: 54px; border-radius: 50%; background: #18752b; color: white; font-size: 28px; margin-bottom: 9px; }}
        .admin-login-title {{ color: #172b1b; font-size: 25px; font-weight: 800; }}
        .admin-login-subtitle {{ color: #7a8e7e; font-size: 13px; margin-top: 4px; }}
        .admin-demo {{ color: #7a8e7e; text-align: center; font-size: 12px; margin-top: 12px; }}
        @media (max-width: 600px) {{ .block-container {{ padding: 2rem .7rem; }} [data-testid="stTabs"] {{ padding: 10px 12px 18px; }} }}
        </style>
        <div class="login-brand">
            <div class="login-mark">♧</div>
            <h1>Smart Crop Advisory</h1>
            <p>Smart Solutions for Farmers</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ======================================================
    # FORGOT PASSWORD FLOW
    # ======================================================

    if st.session_state.get("auth_mode") == "forgot_password":

        st.markdown("---")

        # ==================================================
        # STEP 1 — MOBILE NUMBER
        # ==================================================

        if st.session_state.get("reset_step", "mobile") == "mobile":

            st.markdown(
                '<h2 class="reset-title">🔐 Reset Your Password</h2>',
                unsafe_allow_html=True,
            )

            st.write("Enter your registered mobile number to continue.")

            reset_mobile = st.text_input(
                "📱 Registered Mobile Number",
                max_chars=10,
                placeholder="Enter your 10-digit mobile number",
                key="reset_mobile",
            )

            st.write("")

            if st.button(
                "Send OTP →",
                type="primary",
                use_container_width=True,
                key="send_reset_otp_button",
            ):

                if not validate_mobile(reset_mobile):
                    st.error("Please enter a valid 10-digit mobile number.")
                else:
                    success, otp, message = create_password_reset_otp(reset_mobile)

                    if success:
                        st.session_state["reset_mobile_number"] = reset_mobile
                        st.session_state["reset_step"] = "otp"
                        st.session_state["reset_verified"] = False
                        # Development mode
                        st.session_state["reset_dev_otp"] = otp

                        st.success("OTP generated successfully.")
                        st.rerun()
                    else:
                        st.error(message)

            st.write("")

            if st.button(
                "← Back to Login",
                use_container_width=True,
                key="reset_back_login_button",
            ):
                st.session_state["auth_mode"] = "login"
                st.session_state["reset_step"] = None
                st.session_state["reset_mobile_number"] = None
                st.session_state["reset_verified"] = False
                st.session_state["reset_dev_otp"] = None
                st.rerun()

        # ==================================================
        # STEP 2 — OTP VERIFICATION
        # ==================================================

        elif st.session_state.get("reset_step") == "otp":

            st.markdown(
                '<h2 class="reset-title">📱 OTP Verification</h2>',
                unsafe_allow_html=True,
            )

            reset_mobile = st.session_state.get("reset_mobile_number", "")

            st.info("Enter the 6-digit OTP to verify your account.")
            st.caption(f"Mobile ending in: ****{reset_mobile[-4:]}")

            reset_otp = st.text_input(
                "🔢 Enter 6-digit OTP",
                max_chars=6,
                placeholder="Enter OTP",
                key="reset_otp",
            )

            # ------------------------------------------------
            # DEVELOPMENT OTP
            # ------------------------------------------------

            if st.session_state.get("reset_dev_otp"):
                st.warning(
                    "Development mode OTP: "
                    + str(st.session_state["reset_dev_otp"])
                )

            st.write("")

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "✅ Verify OTP",
                    type="primary",
                    use_container_width=True,
                    key="verify_reset_otp_button",
                ):
                    if not reset_otp.isdigit() or len(reset_otp) != 6:
                        st.error("Please enter a valid 6-digit OTP.")
                    else:
                        verified, message = verify_login_otp(reset_mobile, reset_otp)

                        if verified:
                            st.session_state["reset_step"] = "password"
                            st.session_state["reset_verified"] = True
                            st.session_state["reset_dev_otp"] = None

                            st.success("OTP verified successfully.")
                            st.rerun()
                        else:
                            st.error(message)

            with col2:
                if st.button(
                    "← Back",
                    use_container_width=True,
                    key="reset_back_mobile_button",
                ):
                    st.session_state["reset_step"] = "mobile"
                    st.session_state["reset_verified"] = False
                    st.session_state["reset_dev_otp"] = None
                    st.rerun()

        # ==================================================
        # STEP 3 — NEW PASSWORD
        # ==================================================

        elif (
            st.session_state.get("reset_step") == "password"
            and st.session_state.get("reset_verified", False)
        ):

            st.markdown(
                '<h2 class="reset-title">🔑 Create New Password</h2>',
                unsafe_allow_html=True,
            )

            st.write(
                "Your mobile number has been verified. "
                "Create a new secure password."
            )

            st.markdown(
                """
<div class="reset-box">
🔒 Your new password is securely hashed before being stored in the database.
</div>
""",
                unsafe_allow_html=True,
            )

            new_password = st.text_input(
                "🔑 New Password",
                type="password",
                placeholder="Enter your new password",
                key="new_password",
            )

            confirm_new_password = st.text_input(
                "🔐 Confirm New Password",
                type="password",
                placeholder="Re-enter your new password",
                key="confirm_new_password",
            )

            st.write("")

            if st.button(
                "Reset Password →",
                type="primary",
                use_container_width=True,
                key="reset_password_button",
            ):
                if not new_password:
                    st.error("Please enter a new password.")
                elif not confirm_new_password:
                    st.error("Please confirm your new password.")
                elif new_password != confirm_new_password:
                    st.error("New passwords do not match.")
                else:
                    success, message = reset_password(
                        st.session_state["reset_mobile_number"],
                        new_password,
                    )

                    if success:
                        st.session_state["auth_mode"] = "login"
                        st.session_state["reset_step"] = None
                        st.session_state["reset_verified"] = False
                        st.session_state["reset_mobile_number"] = None
                        st.session_state["reset_dev_otp"] = None

                        st.success(
                            "🎉 Password reset successfully. "
                            "You can now login with your new password."
                        )
                        st.rerun()
                    else:
                        st.error(message)

            st.write("")

            if st.button(
                "← Back to Login",
                use_container_width=True,
                key="password_back_login_button",
            ):
                st.session_state["auth_mode"] = "login"
                st.session_state["reset_step"] = None
                st.session_state["reset_verified"] = False
                st.session_state["reset_mobile_number"] = None
                st.session_state["reset_dev_otp"] = None
                st.rerun()

        return

    # ======================================================
    # LOGIN / REGISTRATION TABS
    # ======================================================

    login_tab, admin_tab, registration_tab = st.tabs(
        ["🔐 Farmer Login", "🛡️ Admin Login", "📝 Farmer Registration"]
    )

    # ======================================================
    # LOGIN
    # ======================================================

    with login_tab:

        st.subheader("↪ Phone Login")
        st.write("Enter your phone number and password to receive an OTP.")

        mobile = st.text_input(
            "📱 Registered Mobile Number",
            max_chars=10,
            placeholder="Enter your 10-digit mobile number",
            key="login_mobile",
        )

        password = st.text_input(
            "🔑 Password",
            type="password",
            placeholder="Enter your password",
            key="login_password",
        )

        if st.button(
            "Forgot Password?",
            use_container_width=True,
            key="forgot_password_button",
        ):
            st.session_state["auth_mode"] = "forgot_password"
            st.session_state["reset_step"] = "mobile"
            st.session_state["reset_verified"] = False
            st.rerun()

        st.write("")

        if st.button(
            "Send OTP",
            type="primary",
            use_container_width=True,
            key="login_continue_button",
        ):
            if not validate_mobile(mobile):
                st.error("Please enter a valid 10-digit mobile number.")
            elif not password:
                st.error("Please enter your password.")
            else:
                user = authenticate_user(mobile, password)

                allowed, status_message = get_login_status(user)

                if not allowed:
                    st.error(status_message)
                else:
                    success, otp, message = create_login_otp(mobile)

                    if success:
                        st.session_state["otp_pending"] = True
                        st.session_state["otp_mobile"] = mobile
                        st.session_state["otp_purpose"] = "login"
                        # Development mode
                        st.session_state["dev_otp"] = otp

                        st.success(
                            "Login credentials verified. "
                            "Complete OTP verification."
                        )
                        st.rerun()
                    else:
                        st.error(message)

        st.markdown(
            '<div class="login-security">🛡 Your information is secure. Farmer accounts require OTP verification and admin approval.</div>',
            unsafe_allow_html=True,
        )

    with admin_tab:

        st.markdown(
            """
            <div class="admin-login-head">
                <div class="admin-login-icon">♢</div>
                <div class="admin-login-title">Farm Admin</div>
                <div class="admin-login-subtitle">Sign in to access the admin panel</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        admin_mobile = st.text_input(
            "Admin Mobile Number",
            max_chars=10,
            placeholder="Enter admin mobile number",
            key="admin_login_mobile",
        )
        admin_password = st.text_input(
            "Admin Password",
            type="password",
            placeholder="Enter admin password",
            key="admin_login_password",
        )

        if st.button(
            "Continue as Admin →",
            type="primary",
            use_container_width=True,
            key="admin_login_continue_button",
        ):
            if not validate_mobile(admin_mobile) or not admin_password:
                st.error("Enter a valid admin mobile number and password.")
            else:
                admin_user = authenticate_user(admin_mobile, admin_password)
                if admin_user is None or admin_user["role"] != "Admin":
                    st.error("Admin account not found or credentials are invalid.")
                else:
                    success, otp, message = create_login_otp(admin_mobile)
                    if success:
                        st.session_state["otp_pending"] = True
                        st.session_state["otp_mobile"] = admin_mobile
                        st.session_state["otp_purpose"] = "admin_login"
                        st.session_state["dev_otp"] = otp
                        st.success("Admin credentials verified. Complete OTP verification.")
                        st.rerun()
                    else:
                        st.error(message)

        st.markdown(
            '<div class="admin-demo">🔒 Admin access is protected with OTP verification.</div>',
            unsafe_allow_html=True,
        )

    # ======================================================
    # REGISTRATION
    # ======================================================

    with registration_tab:

        st.subheader("Create Your Account")
        st.write("Register to access the protected agriculture platform.")

        full_name = st.text_input(
            "👤 Full Name",
            placeholder="Enter your full name",
            key="register_name",
        )

        reg_mobile = st.text_input(
            "📱 Mobile Number",
            max_chars=10,
            placeholder="Enter your 10-digit mobile number",
            key="register_mobile",
        )

        email = st.text_input(
            "✉️ Email Address",
            placeholder="example@email.com",
            key="register_email",
        )

        reg_password = st.text_input(
            "🔑 Create Password",
            type="password",
            placeholder="Minimum 8 characters",
            key="register_password",
        )

        confirm_password = st.text_input(
            "🔐 Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="confirm_password",
        )

        st.markdown(
            """
<div class="security-box">
🔒 Your password is securely hashed before database storage.
</div>
""",
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button(
            "Create Account & Verify →",
            type="primary",
            use_container_width=True,
            key="register_account_button",
        ):
            if not full_name.strip():
                st.error("Please enter your full name.")
            elif not validate_mobile(reg_mobile):
                st.error("Please enter a valid 10-digit mobile number.")
            elif not validate_email(email):
                st.error("Please enter a valid email address.")
            elif not reg_password:
                st.error("Please create a password.")
            elif reg_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                password_ok, password_message = validate_password(reg_password)

                if not password_ok:
                    st.error(password_message)
                else:
                    success, message = register_user(
                        full_name=full_name,
                        mobile=reg_mobile,
                        email=email,
                        password=reg_password,
                        role="Farmer",
                    )

                    if success:
                        otp_success, otp, otp_message = create_login_otp(reg_mobile)

                        if otp_success:
                            st.session_state["otp_pending"] = True
                            st.session_state["otp_mobile"] = reg_mobile
                            st.session_state["otp_purpose"] = "registration"
                            # Development mode
                            st.session_state["dev_otp"] = otp

                            st.success(
                                "Registration successful. "
                                "Complete OTP verification "
                                "to activate your account."
                            )
                            st.rerun()
                        else:
                            st.error(otp_message)
                    else:
                        st.error(message)

    # ======================================================
    # LOGIN / REGISTRATION OTP
    # ======================================================

    if st.session_state.get("otp_pending", False):

        st.markdown("---")
        st.subheader("📱 OTP Verification")

        otp_mobile = st.session_state.get("otp_mobile", "")
        otp_purpose = st.session_state.get("otp_purpose", "login")

        if otp_purpose == "registration":
            st.info("Complete OTP verification to activate your new account.")
        else:
            st.info("Complete OTP verification to access your account.")

        st.caption(f"Mobile ending in: ****{otp_mobile[-4:]}")

        otp_input = st.text_input(
            "Enter 6-digit OTP",
            max_chars=6,
            placeholder="Enter OTP",
            key="verification_otp",
        )

        # Development mode
        if st.session_state.get("dev_otp"):
            st.warning(
                "Development mode OTP: " + str(st.session_state["dev_otp"])
            )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "✅ Verify OTP",
                type="primary",
                use_container_width=True,
                key="verify_login_otp_button",
            ):
                if not otp_input.isdigit() or len(otp_input) != 6:
                    st.error("Please enter a valid 6-digit OTP.")
                else:
                    verified, message = verify_login_otp(otp_mobile, otp_input)

                    if verified:
                        user = get_user_by_mobile(otp_mobile)

                        if user:
                            create_login_session(user)
                            st.session_state["dev_otp"] = None
                            st.session_state["otp_pending"] = False

                            st.success("Authentication successful!")
                            st.rerun()
                        else:
                            st.error("Unable to load the user account.")
                    else:
                        st.error(message)

        with col2:
            if st.button(
                "Cancel Verification",
                use_container_width=True,
                key="cancel_login_otp_button",
            ):
                st.session_state["otp_pending"] = False
                st.session_state["otp_mobile"] = None
                st.session_state["otp_purpose"] = None
                st.session_state["dev_otp"] = None
                st.rerun()


# ==========================================================
# MAIN APPLICATION ROUTER
# ==========================================================

PROTECTED_PAGES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "protected_pages"
)


def run_protected_page(filename):
    """Run an existing protected page safely."""

    page_path = os.path.join(PROTECTED_PAGES_DIR, filename)

    if not os.path.exists(page_path):
        st.error("⚠️ This page is currently unavailable.")
        return

    try:
        runpy.run_path(page_path, run_name="__main__")
    except Exception as e:
        st.error("⚠️ Unable to load this section.")
        with st.expander("Technical Details"):
            st.exception(e)


def show_protected_application():

    user = get_current_user()

    # ======================================================
    # PROFESSIONAL DASHBOARD CSS
    # ======================================================

    st.markdown(
        """
<style>
.stApp {
    background: #f6f8f5;
}
.block-container {
    max-width: 1440px;
    padding: 1.4rem clamp(0.8rem, 3vw, 3rem) 3rem;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f4faf5 0%, #ffffff 100%);
    border-right: 1px solid #dce9de;
}
section[data-testid="stSidebar"] .block-container {
    padding: 1.2rem 1rem;
}
.sidebar-brand {
    text-align: center;
    padding: 8px 5px 20px 5px;
}
.sidebar-logo {
    font-size: 42px;
    line-height: 1;
    margin-bottom: 8px;
}
.sidebar-title {
    font-size: 20px;
    font-weight: 800;
    color: #176b2c;
    margin-bottom: 3px;
}
.sidebar-subtitle {
    font-size: 11px;
    color: #6d8172;
    font-weight: 600;
}
.user-card {
    background: #ffffff;
    border: 1px solid #d9e8dc;
    border-radius: 14px;
    padding: 14px;
    margin: 8px 0 20px 0;
    box-shadow: 0 3px 12px rgba(0,0,0,0.04);
}
.user-label {
    font-size: 10px;
    color: #78907d;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.user-name {
    font-size: 16px;
    font-weight: 750;
    color: #203c27;
    margin-top: 5px;
}
.user-role {
    font-size: 11px;
    color: #64806a;
    margin-top: 4px;
}
.nav-section {
    font-size: 10px;
    color: #78907d;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 18px 4px 7px 4px;
}
.nav-section + div button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 650;
}
@media (max-width: 768px) {
    .block-container { padding: 1rem 0.75rem 2rem; }
    section[data-testid="stSidebar"] .block-container { padding: 0.8rem 0.7rem; }
    .sidebar-logo { font-size: 32px; }
    .sidebar-title { font-size: 17px; }
}
.dashboard-header {
    background: linear-gradient(135deg, #176b2c 0%, #2e8b45 100%);
    border-radius: 18px;
    padding: 25px 30px;
    margin-bottom: 24px;
    box-shadow: 0 8px 25px rgba(23,107,44,0.16);
}
.dashboard-title {
    color: #ffffff;
    font-size: 30px;
    font-weight: 800;
    margin: 0;
}
.dashboard-subtitle {
    color: #e9f6eb;
    font-size: 14px;
    margin-top: 7px;
}
.dashboard-welcome {
    background: #ffffff;
    border: 1px solid #dce9de;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 20px;
}
.dashboard-welcome-title {
    color: #176b2c;
    font-size: 22px;
    font-weight: 750;
    margin-bottom: 5px;
}
.dashboard-welcome-text {
    color: #607064;
    font-size: 14px;
}
</style>
""",
        unsafe_allow_html=True,
    )

    if is_admin():
        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"] { display: none; }
            [data-testid="stAppViewContainer"] { margin-left: 0; }
            </style>
            """,
            unsafe_allow_html=True,
        )

    # ======================================================
    # SIDEBAR BRAND
    # ======================================================

    st.sidebar.markdown(
        """
<div class="sidebar-brand">
<div class="sidebar-logo">🌾</div>
<div class="sidebar-title">Smart Crop Advisory</div>
<div class="sidebar-subtitle">AI-Powered Farmer Assistant</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # ======================================================
    # USER PROFILE
    # ======================================================

    if user:
        full_name = user.get("full_name", "User")
        email = user.get("email", "")
        role = user.get("role", "Farmer")

        role_line = role + (" • " + email if email else "")

        st.sidebar.markdown(
            f"""
<div class="user-card">
<div class="user-label">Signed in as</div>
<div class="user-name">👤 {full_name}</div>
<div class="user-role">{role_line}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    # ======================================================
    # NAVIGATION
    # ======================================================

    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "Dashboard"

    def navigation_button(label, page, key):
        clicked = st.sidebar.button(
            label,
            use_container_width=True,
            key=key,
            type="primary" if st.session_state["active_page"] == page else "secondary",
        )
        if clicked and st.session_state["active_page"] != page:
            st.session_state["active_page"] = page
            st.rerun()

    st.sidebar.markdown('<div class="nav-section">Workspace</div>', unsafe_allow_html=True)
    navigation_button("⌂  Dashboard", "Dashboard", "nav_dashboard")

    st.sidebar.markdown('<div class="nav-section">Crop Intelligence</div>', unsafe_allow_html=True)
    navigation_button("🌿  Supported Species", "Supported Species", "nav_species")
    navigation_button("🔍  Disease Detection", "Disease Detection", "nav_detection")

    st.sidebar.markdown('<div class="nav-section">AI Tools</div>', unsafe_allow_html=True)
    navigation_button("🤖  Farmer Assistant", "Crop Assistant", "nav_crop_assistant")
    if not is_admin():
        navigation_button("💬  Ask an Adviser", "Ask an Adviser", "nav_ask_adviser")

    st.sidebar.markdown('<div class="nav-section">Live Farm Insights</div>', unsafe_allow_html=True)
    navigation_button("☀  Weather", "Weather", "nav_weather")
    navigation_button("📈  Market Prices", "Market Prices", "nav_market")

    if is_admin():
        st.sidebar.markdown('<div class="nav-section">Administration</div>', unsafe_allow_html=True)
        navigation_button("🛡️  Admin Panel", "Admin Panel", "nav_admin_panel")

    # ======================================================
    # ACCOUNT
    # ======================================================

    st.sidebar.markdown(
        '<div class="nav-section">⚙️ Account</div>',
        unsafe_allow_html=True,
    )

    if st.sidebar.button(
        "🚪 Sign Out",
        use_container_width=True,
        key="main_logout_button",
    ):
        logout_user()
        st.rerun()

    # ------------------------------------------------------
    # Current active page
    # ------------------------------------------------------

    selected_page = st.session_state["active_page"]

    # ======================================================
    # PAGE FILE MAPPING
    # ======================================================

    page_files = {
        "Dashboard": "00_Welcome_Page.py",
        "Supported Species": "01_Supported_Species_Info.py",
        "Disease Detection": "02_Upload_and_Classify.py",
        "Crop Assistant": "03_Talk_to_Our_Chatbot.py",
        "Ask an Adviser": "08_Ask_An_Adviser.py",
        "Weather": "05_Live_Weather.py",
        "Market Prices": "06_Live_Market_Prices.py",
        "Admin Panel": "07_Admin_Panel.py",
    }

    selected_file = page_files.get(selected_page, "00_Welcome_Page.py")

    # ======================================================
    # RUN ORIGINAL PROTECTED PAGE
    # ======================================================

    run_protected_page(selected_file)


# ==========================================================
# AUTHENTICATION GATE
# ==========================================================

if is_authenticated():
    show_protected_application()
else:
    show_authentication()