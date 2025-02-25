import streamlit as st
import time
from datetime import datetime
import pytz
import random

def popup():
    # Ensure session state has a counter
    if "last_popup" not in st.session_state:
        st.session_state["last_popup"] = time.time()



    # Show pop-up every 10 seconds
    if time.time() - st.session_state["last_popup"] > 10:  # Change 10 to any interval you want
        st.toast("🔔 Reminder: Check your calendar!", icon="📅")
        st.session_state["last_popup"] = time.time()  # Reset timer

    # Dining hall hours
    dining_hours = {
        "Monday": [("Breakfast", "08:00 AM", "10:00 AM"), ("Lunch", "11:00 AM", "02:00 PM"), ("Dinner", "05:00 PM", "07:30 PM")],
        "Tuesday": [("Breakfast", "08:00 AM", "10:00 AM"), ("Lunch", "11:00 AM", "02:00 PM"), ("Dinner", "05:00 PM", "07:30 PM")],
        "Wednesday": [("Breakfast", "08:00 AM", "10:00 AM"), ("Lunch", "11:00 AM", "02:00 PM"), ("Dinner", "05:00 PM", "07:30 PM")],
        "Thursday": [("Breakfast", "08:00 AM", "10:00 AM"), ("Lunch", "11:00 AM", "02:00 PM"), ("Dinner", "05:00 PM", "07:30 PM")],
        "Friday": [("Breakfast", "08:00 AM", "10:00 AM"), ("Lunch", "11:00 AM", "02:00 PM"), ("Dinner", "05:00 PM", "07:30 PM")],
        "Saturday": [("Brunch", "11:00 AM", "01:00 PM"), ("Dinner", "05:00 PM", "07:00 PM")],
        "Sunday": [("Brunch", "11:00 AM", "01:00 PM"), ("Dinner", "05:00 PM", "07:00 PM")]
    }

    # Get current day and time
    timezone = pytz.timezone("America/New_York")
    now = datetime.now(timezone)
    current_time = now.strftime("%I:%M %p")
    current_day = now.strftime("%A")

    # Debug: Check current time and day
    st.write(f"Current time: {current_time}, Current day: {current_day}")
    st.write("CEO Hours: 8 am - 5 pm")
    st.write("WRC Hours: 8 am - 5 pm")
    st.write("CWC Hours: 8 am - 5 pm")
    st.write("QRC Hours: 8 am - 5 pm")
    st.link_button("Go to WRC Appointment Site", "https://ncf.mywconline.com/")

    st.write("HAM Hours: ")

    for meal, open_time, closing_time in dining_hours[current_day]:
        # Debug: Check dining hall hours
        st.write(f"Checking {meal} hours: {open_time} - {closing_time}")
        if open_time <= now.strftime("%I:%M %p") <= closing_time:
            st.toast(f"Reminder: Dining hall {meal} is open!", icon="🍽️")
            st.session_state["last_popup"] = time.time()
        elif now.strftime("%I:%M %p") == closing_time:
            st.toast(f"Reminder: Dining hall {meal} is closing now!", icon="🍽️")
            st.session_state["last_popup"] = time.time()
        elif now.strftime("%I:%M %p") > closing_time:
            st.toast(f"Reminder: Dining hall {meal} is closed!", icon="🍽️")
            st.session_state["last_popup"] = time.time()


def randomImage():
    if "show_image" not in st.session_state:
        st.session_state["show_image"] = False

    if st.button("Show Random Image and dining hall message"):
        st.session_state["show_image"] = not st.session_state["show_image"]

    if st.session_state["show_image"]:
        memelinks = [
            "https://i.insider.com/674df55be45a68623a276ce1?width=1000&format=jpeg&auto=webp",
            "https://images.saatchiart.com/saatchi/1678766/art/7982375/7049784-HSC00002-7.jpg",
            "https://i.pinimg.com/564x/e9/03/d9/e903d94d703f3e12eb34b28698e19e8b.jpg",
            "https://www.photory.app/_next/static/images/Confidence%20meme-e356aadf3ce8579d5d10e9eddd087cec.jpg",
            "https://i.pinimg.com/736x/11/7a/06/117a06da233d2b377d392b8a877f7e58.jpg",
            "https://i.pinimg.com/564x/64/60/e3/6460e3ca975aec7fcaaf32583e70ae25.jpg"
        ]

        if memelinks:
            meme_link = random.choice(memelinks)
            st.image(meme_link, caption="Stay Focused!")

