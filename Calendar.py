import streamlit as st
import datetime
import uuid
import Database as DB
from streamlit_calendar import calendar
"""
Calendar.oy
This file contains the code for the calendar feature of the app.
It handles all the functionalities of the calendar.
THis includes adding, editing, and deleting events.

"""

#Remove duplicates from the events list
def removeDuplicates(events):
    seen = set()
    unique_events = []
    for event in events:
        if "id" not in event or not event["id"]:
            event["id"] = str(uuid.uuid4())
        event_key = (event["title"], event["start"], event["end"], event["resource_id"])
        if event_key not in seen:
            unique_events.append(event)
            seen.add(event_key)
    return unique_events


def syncNewEvents():
    """Ensures newly created events get assigned a valid ID and syncs them to the database."""
    user_id = st.session_state.get("user_id")
    if not user_id:
        return

    db_events = DB.load_events(user_id) or []
    local_events = st.session_state.get("events", [])

    for local_event in local_events:
        if "id" not in local_event or not local_event["id"]:
            local_event["id"] = str(uuid.uuid4())  # Assign missing IDs

    # Remove duplicates and ensure all events are synced
    st.session_state["events"] = removeDuplicates(local_events + db_events)


def showCalendar():
    if 'events' not in st.session_state or st.session_state['events'] is None:
        st.session_state['events'] = []

    if "selected_event" not in st.session_state:
        st.session_state["selected_event"] = None

    if "calendar_refresh" not in st.session_state:
        st.session_state["calendar_refresh"] = 0

    syncNewEvents()

    st.header("Calendar Mode Selection")
    mode = st.selectbox(
        "Calendar Mode:",
        ("daygrid", "timegrid", "timeline", "resource-daygrid", "resource-timegrid", "resource-timeline", "list",
         "multimonth")
    )

    # Adding new event form
    st.header("Add Events to the Calendar")
    with st.expander("Add a New Event"):
        with st.form("event_form"):
            st.write("### Add a New Event")

            title = st.text_input("Event Title")
            color = st.color_picker("Pick a Color", "#FF6C6C")
            start_date = st.date_input("Start Date", datetime.date.today())
            end_date = st.date_input("End Date", datetime.date.today())
            start_time = st.time_input("Start Time", datetime.time(9, 0))
            end_time = st.time_input("End Time", datetime.time(10, 0))
            resource_id = st.selectbox("Resource ID", ["a", "b", "c", "d", "e", "f"], index=0)

            submitted = st.form_submit_button("Add Event")

            if submitted:
                if end_date < start_date:
                    st.error("End date cannot be before start date. Please select a valid date range.")
                else:
                    num_days = (end_date - start_date).days + 1

                    for i in range(num_days):
                        event_date = start_date + datetime.timedelta(days=i)
                        new_event = {
                            "id": str(uuid.uuid4()),
                            "title": title,
                            "color": color,
                            "start": f"{event_date}T{start_time}",
                            "end": f"{event_date}T{end_time}",
                            "resource_id": resource_id,
                        }
                        if new_event["title"]:
                            st.session_state["events"].append(new_event)
                            DB.save_event(new_event, st.session_state["user_id"])

                    st.session_state["events"] = removeDuplicates(st.session_state["events"])
                    st.success(f"✅ Event '{title}' added!")
                    st.rerun()

    # Calendar resources
    calendar_resources = [
        {"id": "a", "building": "Building A", "title": "Room A"},
        {"id": "b", "building": "Building A", "title": "Room B"},
        {"id": "c", "building": "Building B", "title": "Room C"},
        {"id": "d", "building": "Building B", "title": "Room D"},
        {"id": "e", "building": "Building C", "title": "Room E"},
        {"id": "f", "building": "Building C", "title": "Room F"},
    ]

    # Calendar options
    calendar_options = {
        "editable": "true",
        "navLinks": "true",
        "resources": calendar_resources,
        "selectable": "true",
    }

    if mode == "daygrid":
        calendar_options.update({"initialView": "dayGridMonth"})
    elif mode == "timegrid":
        calendar_options.update({"initialView": "timeGridWeek"})
    elif mode == "timeline":
        calendar_options.update({"initialView": "timelineMonth"})
    elif mode == "list":
        calendar_options.update({"initialView": "listMonth"})
    elif mode == "multimonth":
        calendar_options.update({"initialView": "multiMonthYear"})

    # Render the calendar
    state = calendar(
        events=st.session_state["events"],
        options=calendar_options,
        custom_css=""" 
        .fc-event-past { opacity: 0.8; } 
        .fc-event-time { font-style: italic; } 
        .fc-event-title { font-weight: 700; } 
        .fc-toolbar-title { font-size: 2rem; }
        """,
        key=f"{mode}-{len(st.session_state['events'])}-{st.session_state.get('calendar_refresh', 0)}",
    )

    if state.get("eventsSet") is not None:
        if isinstance(state["eventsSet"], list):
            st.session_state["events"] = state["eventsSet"]

    #Checks if the event was clicked
    if state.get("eventClick") is not None:
        if "eventClick" in state and "event" in state["eventClick"] and "id" in state["eventClick"]["event"]:
            clicked_event_id = state["eventClick"]["event"]["id"]
            try:
                st.session_state["selected_event"] = next(
                    (event for event in st.session_state.get("events", []) if
                     str(event.get("id")) == str(clicked_event_id)), None
                )
                if st.session_state["selected_event"]:
                    st.write(f"Event '{st.session_state['selected_event']['title']}' selected!")
                else:
                    st.error(f"No event found with id {clicked_event_id}")
            except KeyError as e:
                st.error(f"Error processing event click: {e}")
        else:
            st.write("No event clicked or event ID not found.")

    # Edit or delete selected event
    if st.session_state["selected_event"]:
        with st.form("edit_event_form"):
            st.write("### Edit Event")

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
            resource_id = st.selectbox("Resource ID", ["a", "b", "c", "d", "e", "f"],
                                       index=["a", "b", "c", "d", "e", "f"].index(
                                           st.session_state["selected_event"]["resource_id"]))

            update_submitted = st.form_submit_button("Update Event")
            delete_submitted = st.form_submit_button("Delete Event")

            #Updates the events with the new information
            if update_submitted:
                # Find the event in session state and update it
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

                # Reset selected event and trigger calendar refresh
                st.session_state["selected_event"] = None
                st.session_state["calendar_refresh"] += 1

                st.success(f"✅ Event '{title}' updated!")
                st.rerun()

            #Deletes the event the user selected
            if delete_submitted:
                # Remove the event from session state and database
                st.session_state["events"].remove(st.session_state["selected_event"])
                DB.delete_event(st.session_state["selected_event"]["id"])

                # Reset selected event and trigger calendar refresh
                st.session_state["selected_event"] = None
                st.session_state["calendar_refresh"] += 1

                st.success(f"✅ Event '{title}' deleted!")
                st.rerun()

