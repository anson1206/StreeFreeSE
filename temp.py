import streamlit as st
from streamlit_calendar import calendar
import datetime
import uuid
import Database as DB

def showCalendar():
    """
    st.markdown("## Interactive Calendar with Event Input 📆")

    # Ensure session state contains an event list
    if "events" not in st.session_state:
        st.session_state["events"] = []

    if "eventClick" not in st.session_state:
        st.session_state["eventClick"] = None

    # Ensure session state contains a user_id
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None  # This should be set after login

    # Load events from the database if not already loaded
    if len(st.session_state["events"]) == 0 and st.session_state["user_id"]:
        DB.load_events(st.session_state["user_id"])

    """

    # Calendar mode selection
    st.header("Calendar Mode Selection")
    mode = st.selectbox(
        "Calendar Mode:",
        (
            "daygrid",
            "timegrid",
            "timeline",
            "resource-daygrid",
            "resource-timegrid",
            "resource-timeline",
            "list",
            "multimonth",
        ),
    )

    # Calendar resources
    calendar_resources = [
        {"id": "a", "building": "Building A", "title": "Room A"},
        {"id": "b", "building": "Building A", "title": "Room B"},
        {"id": "c", "building": "Building B", "title": "Room C"},
        {"id": "d", "building": "Building B", "title": "Room D"},
        {"id": "e", "building": "Building C", "title": "Room E"},
        {"id": "f", "building": "Building C", "title": "Room F"},
    ]

    # Render the calendar (assuming no extra options needed)
    if len(st.session_state["events"]) > 0:
        calendar(st.session_state["events"])  # Pass only the events
    else:
        st.write("No events available.")

    # Event input form inside an expander
    st.header("Add Events to the Calendar")
    with st.expander("Add a New Event"):
        with st.form("event_form"):
            st.write("### Add a New Event")

            # Input fields for event details
            title = st.text_input("Event Title")
            color = st.color_picker("Pick a Color", "#FF6C6C")
            start_date = st.date_input("Start Date", datetime.date.today())
            end_date = st.date_input("End Date", datetime.date.today())
            start_time = st.time_input("Start Time", datetime.time(9, 0))
            end_time = st.time_input("End Time", datetime.time(10, 0))
            resource_id = st.selectbox(
                "Resource ID", ["a", "b", "c", "d", "e", "f"], index=0
            )

            # Submit button for the form
            submitted = st.form_submit_button("Add Event")

            if submitted:
                # Check if the end date is before the start date
                if end_date < start_date:
                    st.error("End date cannot be before start date. Please select a valid date range.")
                else:
                    # Calculate the number of days between start and end dates
                    num_days = (end_date - start_date).days + 1

                    # Create separate events for each day within the date range
                    for i in range(num_days):
                        event_date = start_date + datetime.timedelta(days=i)
                        new_event = {
                            "id": str(uuid.uuid4()),  # Add unique id
                            "title": title,
                            "color": color,
                            "start": f"{event_date}T{start_time}",
                            "end": f"{event_date}T{end_time}",
                            "resource_id": resource_id,
                        }
                        if new_event not in st.session_state["events"] and new_event["title"]:
                            st.session_state["events"].append(new_event)
                            DB.save_event(new_event, st.session_state["user_id"])  # Save event to the database
                    st.success(f"✅ Event '{title}' added!")


    # Initialize selected_event to None or any default value
    selected_event = None
    
    # Your existing code here, including event selection handling
    if "eventClick" in st.session_state and st.session_state["eventClick"]:
        event_id = st.session_state["eventClick"]["event"]["id"]
        selected_event = next(
            (event for event in st.session_state["events"] if event["id"] == event_id), None
        )
    
    # Now you can safely check the value of selected_event
    if selected_event:
        # Proceed with your logic for displaying the event form
        st.write(f"Selected Event: {selected_event['title']}")
    else:
        st.write("No event selected")

    # Edit or delete selected event
    if "selected_event" in st.session_state and st.session_state["selected_event"]:
        with st.form("edit_event_form"):
            st.write("### Edit Event")

            # Input fields for editing event details
            title = st.text_input("Event Title", st.session_state["selected_event"]["title"])
            color = st.color_picker("Pick a Color", st.session_state["selected_event"]["color"])
            start_date = st.date_input("Start Date", datetime.date.fromisoformat(
                st.session_state["selected_event"]["start"].split("T")[0]))
            end_date = st.date_input("End Date", datetime.date.fromisoformat(
                st.session_state["selected_event"]["end"].split("T")[0]))
            start_time = st.time_input("Start Time", datetime.time.fromisoformat(
                st.session_state["selected_event"]["start"].split("T")[1]))
            end_time = st.time_input("End Time", datetime.time.fromisoformat(
                st.session_state["selected_event"]["end"].split("T")[1]))
            resource_id = st.selectbox(
                "Resource ID", ["a", "b", "c", "d", "e", "f"],
                index=["a", "b", "c", "d", "e", "f"].index(st.session_state["selected_event"]["resource_id"])
            )

            # Submit buttons for updating or deleting the event
            update_submitted = st.form_submit_button("Update Event")
            delete_submitted = st.form_submit_button("Delete Event")

            if update_submitted:
                # Update event in session state
                for event in st.session_state["events"]:
                    if event["id"] == st.session_state["selected_event"]["id"]:
                        event.update({
                            "title": title,
                            "color": color,
                            "start": f"{start_date}T{start_time}",
                            "end": f"{end_date}T{end_time}",
                            "resource_id": resource_id,
                        })
                        break

                # Update the event in the database
                DB.update_event(st.session_state["selected_event"]["id"], {
                    "title": title,
                    "color": color,
                    "start": f"{start_date}T{start_time}",
                    "end": f"{end_date}T{end_time}",
                    "resource_id": resource_id,
                })
                st.success(f"✅ Event '{title}' updated!")
                st.session_state["selected_event"] = None
                st.session_state["calendar_refresh"] += 1  # Increment to trigger re-render
                st.rerun()

            if delete_submitted:
                st.session_state["events"].remove(st.session_state["selected_event"])
                st.success(f"✅ Event '{title}' deleted!")

                # Delete event from the database
                DB.delete_event(st.session_state["selected_event"]["id"])
                st.session_state["selected_event"] = None
                st.rerun()
