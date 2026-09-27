"""
Small helper so parts of a page can auto-refresh themselves on a timer,
without the user having to manually reload — used for things like "new
farmer question" showing up on the Admin side, or "adviser's reply"
showing up on the farmer side, within a few seconds of happening.

Streamlit has no cross-session push notifications (each browser tab is
its own independent session), so this uses Streamlit's own built-in
`st.fragment(run_every=...)` (Streamlit 1.37+) to re-query the shared
database every few seconds and re-render just that piece of the page —
not the whole page, so it doesn't reset scroll position, open dropdowns,
or in-progress form input elsewhere on the page.

Purely presentational/plumbing — never touches model inference or
changes any stored value; it only re-reads what's already there sooner.
"""

import streamlit as st


def live_fragment(run_every="4s"):
    """Decorator: turns a function into an auto-refreshing Streamlit
    fragment. Falls back to a plain (non-auto-refreshing) function on
    Streamlit versions that don't support fragments yet, so the page
    still works — it just won't update itself until the next full
    page rerun on those older versions.
    """
    if hasattr(st, "fragment"):
        try:
            return st.fragment(run_every=run_every)
        except TypeError:
            try:
                return st.fragment()
            except Exception:
                pass

    def _identity(func):
        return func

    return _identity
