import streamlit as st

def render_uncertainty_badge(u: float):
    """
    Render a colored uncertainty badge.
    u = fused uncertainty (0–1)
    """

    if u < 0.02:
        st.success(f"🟢 **Low Uncertainty** ({u:.4f})")
    elif u < 0.06:
        st.warning(f"🟡 **Medium Uncertainty** ({u:.4f})")
    else:
        st.error(f"🔴 **High Uncertainty** ({u:.4f})")
