import streamlit as st
from streamlit_extras.let_it_rain import rain
from streamlit_calendar import calendar
import Dashboard as DB
import ToDoList as TDL
import Calendar
import Database as Data

user_id = st.session_state.get("user_id") 
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False  # Initially not logged in

if not st.session_state.logged_in:
    Data.login_page()  # Show login page
else:
    DB.main()  # Show dashboard after login
    TDL.todo(user_id)  # Show ToDo List