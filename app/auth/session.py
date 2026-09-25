import streamlit as st


# ==========================================================
# SESSION INITIALIZATION
# ==========================================================

def initialize_session():
    """Initialize authentication-related session state."""

    defaults = {
        "authenticated": False,
        "user_id": None,
        "user_name": None,
        "user_mobile": None,
        "user_email": None,
        "user_role": None,
        "otp_pending": False,
        "otp_mobile": None,
        "otp_purpose": None,
        "registration_pending": False,
        "current_page": "Welcome",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ==========================================================
# LOGIN SESSION
# ==========================================================

def create_login_session(user):
    """Create an authenticated session after successful verification."""

    st.session_state.authenticated = True
    st.session_state.user_id = user["id"]
    st.session_state.user_name = user["full_name"]
    st.session_state.user_mobile = user["mobile"]
    st.session_state.user_email = user["email"]
    st.session_state.user_role = user["role"]

    st.session_state.otp_pending = False
    st.session_state.otp_mobile = None
    st.session_state.otp_purpose = None
    st.session_state.registration_pending = False
    st.session_state.current_page = "Welcome"


# ==========================================================
# LOGOUT
# ==========================================================

def logout_user():
    """Clear the authenticated session."""

    keys_to_clear = [
        "authenticated",
        "user_id",
        "user_name",
        "user_mobile",
        "user_email",
        "user_role",
        "otp_pending",
        "otp_mobile",
        "otp_purpose",
        "registration_pending",
        "current_page",
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    initialize_session()


# ==========================================================
# AUTHENTICATION CHECK
# ==========================================================

def is_authenticated():
    """Return True only when the user has completed authentication."""

    return bool(
        st.session_state.get("authenticated", False)
        and st.session_state.get("user_id") is not None
    )


def require_authentication():
    """
    Check whether the user is authenticated.

    Returns:
        True  -> access allowed
        False -> access denied
    """

    initialize_session()

    return is_authenticated()


# ==========================================================
# CURRENT USER
# ==========================================================

def get_current_user():
    """Return current logged-in user information."""

    if not is_authenticated():
        return None

    return {
        "id": st.session_state.get("user_id"),
        "full_name": st.session_state.get("user_name"),
        "mobile": st.session_state.get("user_mobile"),
        "email": st.session_state.get("user_email"),
        "role": st.session_state.get("user_role"),
    }


# ==========================================================
# ROLE CHECK
# ==========================================================

def is_farmer():
    """Check whether the logged-in user is a Farmer."""

    return (
        is_authenticated()
        and st.session_state.get("user_role") == "Farmer"
    )


def is_admin():
    """Check whether the logged-in user is an Admin."""

    return (
        is_authenticated()
        and st.session_state.get("user_role") == "Admin"
    )