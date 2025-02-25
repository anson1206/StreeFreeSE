import streamlit as st
import ToDoList
from ToDoList import todo
from Timer import Timer
from NCFCalendarScraper import scraper_page  # Import scraper page
import Calendar
from datetime import datetime, timedelta
from MagicWand import magic_wand
from Scheduler import popup, randomImage
from TaskTimer import TaskTime
from supabase import create_client, Client
import json


# Initialize Supabase
url = "https://rpygalqqsnuajcsdbkut.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJweWdhbHFxc251YWpjc2Ria3V0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAxNjg3MDYsImV4cCI6MjA1NTc0NDcwNn0.ZFgjCTQAiHCuwubyfP1tdTajHRG96XsZWoPIRZYT60o"  # Replace with your Supabase API key
supabase: Client = create_client(url, key)


def fetch_sticky_notes(user_id):
    """Retrieve sticky notes from Supabase for the given user_id."""
    response = supabase.table("events").select("sticky_notes").eq("user_id", user_id).execute()

    if response.data and response.data[0]["sticky_notes"]:  # Ensure sticky_notes is not None
        return json.loads(response.data[0]["sticky_notes"])

    return []  # Return an empty list if no data exists


def update_sticky_notes(user_id, sticky_notes):
    """Update sticky notes in Supabase for the given user_id."""

    # Ensure sticky_notes is a JSON array
    sticky_notes_json = json.dumps(sticky_notes)

    # Try updating existing sticky notes
    response = supabase.table("events").update({
        "sticky_notes": sticky_notes_json
    }).eq("user_id", user_id).execute()

    # If no record exists, insert a new one
    if response.data == []:
        response = supabase.table("events").insert({
            "user_id": user_id,
            "sticky_notes": sticky_notes_json
        }).execute()

    return response


def calculate_weekly_event_hours():
    """Calculate the total hours spent on each event type within the current week (Monday-Sunday)."""
    if "events" not in st.session_state or not st.session_state["events"]:
        st.write("No events found in the calendar.")
        return

    now = datetime.now()
    week_start = datetime(now.year, now.month, now.day) - timedelta(days=now.weekday())  # Monday 00:00
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)  # Sunday 23:59:59

    event_durations = {}

    for event in st.session_state["events"]:
        try:
            event_start = datetime.fromisoformat(event["start"])
            event_end = datetime.fromisoformat(event["end"])

            # Ensure event_end is properly set (fixing zero-length events)
            if event_end <= event_start:
                event_end = event_start + timedelta(minutes=1)  # Assume a minimum duration

            # Adjust event start and end within the week boundaries
            adjusted_start = max(event_start, week_start)
            adjusted_end = min(event_end, week_end)

            # Calculate valid duration (in hours)
            duration = (adjusted_end - adjusted_start).total_seconds() / 3600
            duration = max(0, duration)  # Ensure no negative durations

            if duration > 0:
                event_name = event["title"]
                event_durations[event_name] = event_durations.get(event_name, 0) + duration

        except Exception as e:
            st.write(f"Error processing event '{event.get('title', 'Unknown Event')}': {e}")

    if event_durations:
        st.subheader("⏳ Weekly Event Hours Breakdown")
        for event_name, hours in event_durations.items():
            st.write(f"📌 **{event_name}**: {hours:.2f} hours")
    else:
        st.write("No tracked events for this week.")


def main():
    user_id = st.session_state.get("user_id")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Calendar", "Scheduler", "To-Do List", "Task Timer", "Website Scraper", "Magic Wand"])

    if page == "Dashboard":
        st.title("📌 Student Dashboard")
        st.write("Welcome to your student dashboard! Here you can see your upcoming events and tasks at a glance.")

        st.subheader("📅 Upcoming Events (Next 7 Days)")

        if "events" in st.session_state and st.session_state["events"]:
            now = datetime.now()
            one_week_later = now + timedelta(days=7)  # Define the 7-day window

            # Filter events occurring within the next 7 days
            upcoming_events = [
                event for event in st.session_state["events"]
                if now <= datetime.fromisoformat(event["start"]) <= one_week_later
            ]

            # Sort events by date
            upcoming_events.sort(key=lambda e: datetime.fromisoformat(e["start"]))

            with st.expander("Upcoming Events"):
                if upcoming_events:
                    for event in upcoming_events:
                        st.write(f"📆 **{event['start']}** - {event['title']}")
                else:
                    st.write("No upcoming events in the next 7 days.")

        Calendar.showCalendar()
        # Display weekly event hours tracking
        calculate_weekly_event_hours()

        # Display To-Do List
        st.subheader("✅ To-Do List")
        if user_id:
            todo = ToDoList.todo(user_id)  # Pass user_id when creating an instance
        else:
            st.error("User not logged in!")  # Display error if user_id is not available
        todo.display_tasks("Important")

        # Sticky Notes Section
        st.subheader("📝 Sticky Notes")
        if "sticky_notes" not in st.session_state or st.session_state.sticky_notes is None:
            st.session_state.sticky_notes = fetch_sticky_notes(user_id) or []

        # Input for adding a sticky note
        note_input = st.text_area("Write your note:", height=100)

        if st.button("Submit"):
            if note_input.strip():
                cleaned_note = note_input.strip()
                st.session_state.sticky_notes.append(cleaned_note)  # Add note to local session state
                update_sticky_notes(user_id, st.session_state.sticky_notes)  # Update Supabase

        # Display Sticky Notes
        if st.session_state.sticky_notes:
            st.write("### 🗒️ Your Sticky Notes:")

            # Pair notes with their index for correct deletion mapping
            notes_with_indices = list(enumerate(st.session_state.sticky_notes, start=1))

            for note_number, note in notes_with_indices:
                st.markdown(
                    f"""
                    <div style="background-color: #FFEB3B; padding: 10px; margin: 5px 0; border-radius: 5px;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.2); font-size: 16px; font-weight: bold; color: black;
                    max-width: 400px; word-wrap: break-word; white-space: pre-wrap; overflow-wrap: break-word;">
                    <strong>{note_number}:</strong> {note}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Input to delete a sticky note by number
        note_to_delete = st.text_input("Enter the number of the sticky note you want to delete:")

        if st.button("Delete"):
            if note_to_delete.isdigit():
                note_to_delete = int(note_to_delete)

                # Ensure the number is valid
                if 1 <= note_to_delete <= len(st.session_state.sticky_notes):
                    # Adjust index for correct deletion
                    del st.session_state.sticky_notes[note_to_delete - 1]
                    update_sticky_notes(user_id, st.session_state.sticky_notes)  # Update Supabase
                    st.success(f"Sticky Note #{note_to_delete} deleted.")
                    st.rerun()  # Refresh the page
                else:
                    st.error("Invalid note number. Please enter a valid number.")
            else:
                st.error("Please enter a valid number.")

    elif page == "Calendar":
        st.title('📅 Calendar')
        Calendar.showCalendar()
                
    elif page == "Scheduler":
        st.title("📅 Scheduler")
        popup()
        randomImage()

    elif page == "Task Timer":
        st.title("⏱️ Task Timer")
        st.write("Track how long you spend on each task.")

        taskTime = TaskTime()
        task_name = st.text_input("ENTER TASK NAME:")

        if st.button("Start Timer"):
            if task_name.strip():
                taskTime.start_timer(task_name)
            else:
                st.error("Please enter a task name before starting the timer.")

        if st.button("Stop Timer"):
            taskTime.stop_timer()
        st.write("\n")
        st.title("Task Times")
        st.write("CURRENT TASK:")

        taskTime.display_timer()
        taskTime.show_task_times()
        task_delete = st.number_input("ENTER TASK NUMBER FOR DELETION:", min_value=1, step=1)
        if st.button("Delete Task"):
            taskTime.delete_task(task_delete - 1)
            st.success(f"Task #{task_delete} deleted.")
            st.rerun()


    elif page == "To-Do List":
        st.title("✅ To-Do List")
        st.write("Manage your tasks and keep track of what needs to be done.")

        todo = ToDoList.todo(user_id)
        col1, col2, col3, col4 = st.columns(4)

        # Timer integration
        timer = Timer()

        # Sidebar Timer Controls
        minutes = st.sidebar.number_input("Set Timer (minutes)", min_value=1, max_value=60, value=5)
        start_button = st.sidebar.button("Start Timer")
        stop_button = st.sidebar.button("Stop Timer")

        # Start Timer
        if start_button and not st.session_state.timer_running:
            timer.start_timer(minutes)
            timer.display_timer()

        # Stop Timer
        if stop_button:
            timer.stop_timer()

        with col1:
            st.header("Create")
            userInput = st.text_input("Enter a task")
            label = st.selectbox("Label", ["Doing", "Important", "Done"])
            if st.button("Add Task"):
                todo.add_task(userInput, label)
        with col2:
            st.header("Doing")
            todo.display_tasks("Doing")
        with col3:
            st.header("Important")
            todo.display_tasks("Important")
        with col4:
            st.header("Done")
            todo.display_tasks("Done")

        if user_id:
            todo_instance = ToDoList.todo(user_id)  # Create an instance of todo
            st.subheader(f"Kudo Points: {todo_instance.get_kudo_points_from_db()}")  # Call the method properly
        else:
            st.error("User not logged in!")  # Display error if user_id is not available



    elif page == "Website Scraper":
        scraper_page()  # Load the scraper page

    elif page == "Magic Wand":
        magic_wand() #load magic wand


