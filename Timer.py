import time
import streamlit as st

class Timer:
    def __init__(self):
        if "timer_running" not in st.session_state:
            st.session_state.timer_running = False
        if "timer_seconds" not in st.session_state:
            st.session_state.timer_seconds = 0

    def start_timer(self, minutes):
        st.session_state.timer_seconds = minutes * 60
        st.session_state.timer_running = True

    def stop_timer(self):
        st.session_state.timer_running = False

    def display_timer(self):
        timer_placeholder = st.sidebar.empty()
        while st.session_state.timer_running and st.session_state.timer_seconds > 0:
            mins, secs = divmod(st.session_state.timer_seconds, 60)
            timer_placeholder.write(f"⏳ Timer: {mins:02d}:{secs:02d}")
            time.sleep(1)
            st.session_state.timer_seconds -= 1
            if not st.session_state.timer_running:
                break
        if st.session_state.timer_seconds == 0:
            timer_placeholder.write("⏰ Time's up!")
        else:
            timer_placeholder.write("⏹ Timer stopped.")
