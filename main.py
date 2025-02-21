import streamlit as st
from streamlit_extras.let_it_rain import rain
from streamlit_calendar import calendar
import Dashboard as DB
import ToDoList as TDL
import Calendar

DB.main()
TDL.todo()
def example():
    rain(
        emoji="🎈",
        font_size=54,
        falling_speed=5,
        animation_length="5",
    )
#example()
#Calendar.showCalendar()
