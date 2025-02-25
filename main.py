import streamlit as st
from streamlit_extras.let_it_rain import rain
from streamlit_calendar import calendar
import Dashboard as DB
import ToDoList as TDL
import Calendar
import Database as Data
"""
main.py
This file is the main fie of the app. 
The user is directed to this file when they run the app.
"""


user_id = st.session_state.get("user_id")
#checks if the user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    Data.login_page()
#if the user is logged in, the app will display the dashboard
else:
    DB.main()
    TDL.todo(user_id)