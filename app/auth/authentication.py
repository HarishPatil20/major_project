import bcrypt
import random
from datetime import datetime, timedelta

from .database import (
    get_user_by_mobile,
    create_user,
    save_otp,
    get_latest_otp,
    increment_otp_attempt,
    mark_otp_used,
    mark_user_verified,
    update_user_password,
)


# ==========================================================
# PASSWORD SECURITY
# ==========================================================

def hash_password(password: str) -> str:
    """Create a secure bcrypt password hash."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


# ==========================================================
# USER VALIDATION
# ==========================================================

def validate_mobile(mobile: str) -> bool:
    """Validate Indian-style 10 digit mobile number."""
    mobile = mobile.strip()

    return (
        mobile.isdigit()
        and len(mobile) == 10
        and mobile[0] in "6789"
    )


def validate_email(email: str) -> bool:
    """Basic email validation."""
    email = email.strip()

    return (
        "@" in email
        and "." in email.split("@")[-1]
        and " " not in email
    )


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."

    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter."

    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number."

    return True, "Password is strong."


# ==========================================================
# REGISTRATION
# ==========================================================

def register_user(
    full_name: str,
    mobile: str,
    email: str,
    password: str,
    role: str = "Farmer"
):
    """Register a new user securely."""

    full_name = full_name.strip()
    mobile = mobile.strip()
    email = email.strip().lower()

    if not full_name:
        return False, "Please enter your full name."

    if not validate_mobile(mobile):
        return False, "Please enter a valid 10-digit mobile number."

    if not validate_email(email):
        return False, "Please enter a valid email address."

    password_ok, password_message = validate_password(password)

    if not password_ok:
        return False, password_message

    if role not in ["Farmer", "Admin"]:
        return False, "Invalid user role."

    if get_user_by_mobile(mobile):
        return False, "This mobile number is already registered."

    password_hash = hash_password(password)

    success, message = create_user(
        full_name=full_name,
        mobile=mobile,
        email=email,
        password_hash=password_hash,
        role=role
    )

    return success, message


# ==========================================================
# LOGIN
# ==========================================================

def authenticate_user(mobile: str, password: str):
    """
    Check user credentials.

    Returns:
        user record if valid
        None if invalid
    """

    mobile = mobile.strip()

    user = get_user_by_mobile(mobile)

    if user is None:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return user


def get_login_status(user):
    """Return a user-facing reason when an account cannot sign in yet."""
    if user is None:
        return False, "Invalid mobile number or password."
    if not user["is_verified"]:
        return False, "Please complete OTP verification before signing in."
    if user["role"] == "Farmer" and not user["is_approved"]:
        return False, "Your farmer account is waiting for admin approval."
    return True, "Account is ready for login."


# ==========================================================
# OTP GENERATION
# ==========================================================

def generate_otp() -> str:
    """Generate a secure 6-digit OTP."""
    return f"{random.SystemRandom().randint(100000, 999999)}"


def create_login_otp(mobile: str):
    """
    Generate and securely store an OTP.

    Returns the OTP only for the local development UI.
    In production this value would be sent through an SMS provider.
    """

    user = get_user_by_mobile(mobile)

    if user is None:
        return False, None, "User not found."

    otp = generate_otp()

    otp_hash = hash_password(otp)

    save_otp(
        mobile=mobile,
        otp_hash=otp_hash,
        expiry_minutes=5
    )

    return True, otp, "OTP generated successfully."


# ==========================================================
# OTP VERIFICATION
# ==========================================================

def verify_login_otp(mobile: str, entered_otp: str):
    """Verify OTP with expiry and attempt protection."""

    mobile = mobile.strip()
    entered_otp = entered_otp.strip()

    otp_record = get_latest_otp(mobile)

    if otp_record is None:
        return False, "OTP not found or already used."

    # Maximum 5 attempts
    if otp_record["attempts"] >= 5:
        mark_otp_used(otp_record["id"])
        return False, "Too many incorrect attempts. Please request a new OTP."

    # Check expiry
    try:
        expires_at = datetime.fromisoformat(
            otp_record["expires_at"]
        )

        if datetime.now() > expires_at:
            mark_otp_used(otp_record["id"])
            return False, "OTP has expired. Please request a new OTP."

    except (ValueError, TypeError):
        mark_otp_used(otp_record["id"])
        return False, "Invalid OTP record."

    # Check OTP
    if not verify_password(
        entered_otp,
        otp_record["otp_hash"]
    ):
        increment_otp_attempt(mobile)
        return False, "Invalid OTP."

    # OTP successful
    mark_otp_used(otp_record["id"])
    mark_user_verified(mobile)

    return True, "OTP verified successfully."


# ==========================================================
# USER INFORMATION
# ==========================================================

def get_authenticated_user(mobile: str):
    """Return current user information."""
    return get_user_by_mobile(mobile)


# ==========================================================
# PASSWORD RESET
# ==========================================================

def create_password_reset_otp(mobile: str):
    """Create an OTP for password reset."""
    mobile = mobile.strip()

    user = get_user_by_mobile(mobile)

    if user is None:
        return False, None, "No account found with this mobile number."

    otp = generate_otp()

    save_otp(
        mobile=mobile,
        otp_hash=hash_password(otp),
        expiry_minutes=5
    )

    return True, otp, "OTP generated successfully."


def reset_password(mobile: str, new_password: str):
    """Reset password after OTP verification."""
    mobile = mobile.strip()

    valid, message = validate_password(new_password)

    if not valid:
        return False, message

    password_hash = hash_password(new_password)

    success = update_user_password(
        mobile,
        password_hash
    )

    if not success:
        return False, "Unable to update password."

    return True, "Password reset successfully."