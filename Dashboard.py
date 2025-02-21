import streamlit as st
import ToDoList
from ToDoList import todo 
from Timer import Timer
from NCFCalendarScraper import scraper_page  # Import scraper page
import Calendar
from datetime import datetime, timedelta
from MagicWand import magic_wand
from Scheduler import popup
from TaskTimer import TaskTime

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Scheduler", "To-Do List","Task Timer", "NCF Website Scraper", "Magic Wand"])

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

        # Display To-Do List
        st.subheader("✅ To-Do List")
        todo = ToDoList.todo()
        todo.display_tasks("Important")

        # Sticky Notes Section
        st.subheader("📝 Sticky Notes")

        if "sticky_notes" not in st.session_state:
            st.session_state.sticky_notes = []  # List to store multiple sticky notes

        note_input = st.text_area("Write your note:", height=100)

        if st.button("Submit"):
            if note_input.strip():  # Prevent empty notes
                cleaned_note = note_input.strip()  # Remove leading/trailing newlines
                st.session_state.sticky_notes.append(cleaned_note)

        # Display Submitted Sticky Notes
        if st.session_state.sticky_notes:
            st.write("### 🗒️ Your Sticky Notes:")
            # Display sticky notes with corresponding number
            for idx, note in enumerate(st.session_state.sticky_notes[::-1]):  # Display most recent first
                note_number = len(st.session_state.sticky_notes) - idx  # Number corresponding to the note
                st.markdown(
                    f"""
                    <div style="
                        background-color: #FFEB3B;
                        padding: 10px;
                        margin: 5px 0;
                        margin-top: 0;
                        padding-top: 0;
                        border-radius: 5px;
                        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
                        font-size: 16px;
                        font-weight: bold;
                        color: black;
                        max-width: 400px;
                        word-wrap: break-word;
                        white-space: pre-wrap;
                        overflow-wrap: break-word;">
                        <strong>{note_number}:</strong> {note}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Input to delete a sticky note by its number
        note_to_delete = st.text_input("Enter the number of the sticky note you want to delete:")

        if st.button("Delete"):
            if note_to_delete.isdigit():
                note_to_delete = int(note_to_delete)
                if 1 <= note_to_delete <= len(st.session_state.sticky_notes):
                    # Remove the sticky note with the corresponding number
                    st.session_state.sticky_notes.pop(len(st.session_state.sticky_notes) - note_to_delete)
                    st.success(f"Sticky Note #{note_to_delete} deleted.")
                    st.rerun()  # Rerun to refresh the page and remove the deleted sticky note
                else:
                    st.error("Invalid note number. Please enter a valid number.")
            else:
                st.error("Please enter a valid number.")


    elif page == "Scheduler":
        st.title("📅 Scheduler")
        st.write("Here you can manage your class schedule and deadlines.")

    elif page == "Task Timer":
        st.title("⏱️ Task Timer")
        st.write("Track how long you spend on each task.")

        taskTime = TaskTime()
        task_name = st.text_input("Enter the task name")

        if st.button("Start Timer"):
            if task_name.strip():
                taskTime.start_timer(task_name)
            else:
                st.error("Please enter a task name before starting the timer.")

        if st.button("Stop Timer"):
            taskTime.stop_timer()
        st.title("⏱️ Task Timer")
        st.write("Track how long you spend on each task.")



        taskTime.display_timer()
        taskTime.show_task_times()
        task_delete = st.number_input("Enter the task number you want to delete", min_value=1, step=1)
        if st.button("Delete Task"):
            taskTime.delete_task(task_delete - 1)
            st.success(f"Task #{task_delete} deleted.")
            st.rerun()


    elif page == "To-Do List":
        st.title("✅ To-Do List")
        st.write("Manage your tasks and keep track of what needs to be done.")

        todo = ToDoList.todo()
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
            label = st.selectbox("Label", ["In Progress", "Important", "Done"])
            if st.button("Add Task"):
                todo.add_task(userInput, label)
        with col2:
            st.header("Doing")
            todo.display_tasks("In Progress")
        with col3:
            st.header("Important")
            todo.display_tasks("Important")
        with col4:
            st.header("Done")
            todo.display_tasks("Done")
            
        st.subheader(f"Kudo Points: {todo.get_kudo_points()}")  # Display the points


    elif page == "NCF Website Scraper":
        scraper_page()  # Load the scraper page

    elif page == "Magic Wand":
        magic_wand()

    elif page == "Scheduler":
        popup()


if __name__ == "__main__":
    main()
