import streamlit as st
import time

def popup():
    # Ensure session state has a counter
    if "last_popup" not in st.session_state:
        st.session_state["last_popup"] = time.time()

    # Show pop-up every 10 seconds
    if time.time() - st.session_state["last_popup"] > 1:  # Change 10 to any interval you want
        st.toast("🔔 Reminder: Check your calendar!", icon="📅")
        st.session_state["last_popup"] = time.time()  # Reset timer
