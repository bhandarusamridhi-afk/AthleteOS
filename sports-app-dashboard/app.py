"""
AthleteOS - A unified physical + mental performance platform (mock-up).

Two points of view:
  * Athlete dashboard - personal readiness, physical & mental trends, daily check-in.
  * Coach dashboard   - whole-team readiness, at-risk flags, per-athlete drilldown.

Login is a simple role selector with demo credentials (no real auth) so the
demo is easy and safe to host on Streamlit Community Cloud.
"""

import streamlit as st

import mock_data as md
import athlete_view
import coach_view

st.set_page_config(
    page_title="AthleteOS",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Demo credentials -----------------------------------------------------------
DEMO_USERS = {
    # username: (password, role, display_name / athlete_name)
    "coach": ("coach123", "coach", md.COACH["name"]),
    "maya": ("athlete123", "athlete", "Maya Thompson"),
    "diego": ("athlete123", "athlete", "Diego Ramirez"),
    "aiko": ("athlete123", "athlete", "Aiko Tanaka"),
    "liam": ("athlete123", "athlete", "Liam O'Connor"),
    "sara": ("athlete123", "athlete", "Sara Nilsson"),
}


def _init_session() -> None:
    md.init_data()
    if "auth" not in st.session_state:
        st.session_state.auth = None  # dict: {role, name}


def _login_screen() -> None:
    st.markdown(
        "<h1 style='margin-bottom:0'>🏅 AthleteOS</h1>"
        "<p style='color:#6b7280;margin-top:4px'>Unified physical &amp; mental "
        "performance platform</p>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Sign in")
        role = st.radio(
            "I am a...",
            ["Athlete", "Coach"],
            horizontal=True,
        )

        if role == "Coach":
            default_user = "coach"
        else:
            default_user = "maya"

        with st.form("login"):
            username = st.text_input("Username", value=default_user)
            password = st.text_input("Password", type="password", value="")
            submit = st.form_submit_button("Enter dashboard", use_container_width=True)

        if submit:
            user = DEMO_USERS.get(username.strip().lower())
            if user and password == user[0]:
                st.session_state.auth = {"role": user[1], "name": user[2]}
                st.rerun()
            else:
                st.error("Invalid credentials. Use the demo logins on the right.")

    with col2:
        st.markdown("### Demo logins")
        st.info(
            "**Coach**\n\n"
            "- Username: `coach`\n"
            "- Password: `coach123`"
        )
        st.info(
            "**Athletes** (password `athlete123` for all)\n\n"
            "- `maya` · Maya Thompson (Sprint)\n"
            "- `diego` · Diego Ramirez (Football)\n"
            "- `aiko` · Aiko Tanaka (Swimming)\n"
            "- `liam` · Liam O'Connor (Basketball)\n"
            "- `sara` · Sara Nilsson (Distance Run)"
        )


def _sidebar() -> None:
    auth = st.session_state.auth
    with st.sidebar:
        st.markdown("## 🏅 AthleteOS")
        st.caption("Physical + mental, unified")
        st.divider()
        role_label = "Coach" if auth["role"] == "coach" else "Athlete"
        st.markdown(f"**{auth['name']}**")
        st.caption(f"Signed in as {role_label}")
        st.divider()
        if st.button("Log out", use_container_width=True):
            st.session_state.auth = None
            st.rerun()
        st.divider()
        st.caption(
            "Mock-up demo. Data is sample-generated and resets on reload. "
            "New check-ins persist for the current session."
        )


def main() -> None:
    _init_session()

    if st.session_state.auth is None:
        _login_screen()
        return

    _sidebar()
    auth = st.session_state.auth

    if auth["role"] == "coach":
        coach_view.render()
    else:
        athlete_view.render(auth["name"])


if __name__ == "__main__":
    main()
