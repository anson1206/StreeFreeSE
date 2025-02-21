import streamlit as st
from streamlit_calendar import calendar
import datetime
import uuid


def showCalendar():
    st.markdown("## Interactive Calendar with Event Input 📆")

    # Ensure session state contains an event list
    if "events" not in st.session_state:
        st.session_state["events"] = []

    # Ensure session state contains a selected event
    if "selected_event" not in st.session_state:
        st.session_state["selected_event"] = None

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
                            "resourceId": resource_id,
                        }
                        if new_event not in st.session_state["events"] and new_event["title"]:
                            st.session_state["events"].append(new_event)
                    st.success(f"✅ Event '{title}' added!")

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

    if "resource" in mode:
        if mode == "resource-daygrid":
            calendar_options.update({
                "initialDate": str(datetime.date.today()),
                "initialView": "resourceDayGridDay",
                "resourceGroupField": "building",
            })
        elif mode == "resource-timeline":
            calendar_options.update({
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth",
                },
                "initialDate": str(datetime.date.today()),
                "initialView": "resourceTimelineDay",
                "resourceGroupField": "building",
            })
        elif mode == "resource-timegrid":
            calendar_options.update({
                "initialDate": str(datetime.date.today()),
                "initialView": "resourceTimeGridDay",
                "resourceGroupField": "building",
            })
    else:
        if mode == "daygrid":
            calendar_options.update({
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "dayGridDay,dayGridWeek,dayGridMonth",
                },
                "initialDate": str(datetime.date.today()),
                "initialView": "dayGridMonth",
            })
        elif mode == "timegrid":
            calendar_options.update({"initialView": "timeGridWeek"})
        elif mode == "timeline":
            calendar_options.update({
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "timelineDay,timelineWeek,timelineMonth",
                },
                "initialDate": str(datetime.date.today()),
                "initialView": "timelineMonth",
            })
        elif mode == "list":
            calendar_options.update({
                "initialDate": str(datetime.date.today()),
                "initialView": "listMonth",
            })
        elif mode == "multimonth":
            calendar_options.update({"initialView": "multiMonthYear"})

    # Display calendar with user-inputted & scraped events
    state = calendar(
        events=st.session_state["events"],
        options=calendar_options,
        custom_css="""
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        } 
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
        """,
        key=f"{mode}-{len(st.session_state['events'])}",  # Unique key to force re-render
        # The `key` parameter in the `calendar` function is used to force Streamlit to re-render the calendar component whenever the key changes.
        # By setting the key to a unique value that changes when the number of events or the calendar mode changes,
        # it ensure that the calendar is updated to reflect the latest state.
    )

    # Update session state when events are modified in the UI
    if state.get("eventsSet") is not None:
        if isinstance(state["eventsSet"], list):
            st.session_state["events"] = state["eventsSet"]

    # Handle event click
    if state.get("eventClick") is not None:
        event_id = state["eventClick"]["event"]["id"]
        st.session_state["selected_event"] = next(
            (event for event in st.session_state["events"] if event["id"] == event_id), None
        )

    # Edit or delete selected event
    if st.session_state["selected_event"]:
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
                index=["a", "b", "c", "d", "e", "f"].index(st.session_state["selected_event"]["resourceId"])
            )

            # Submit buttons for updating or deleting the event
            update_submitted = st.form_submit_button("Update Event")
            delete_submitted = st.form_submit_button("Delete Event")

            if update_submitted:
                st.session_state["selected_event"].update({
                    "title": title,
                    "color": color,
                    "start": f"{start_date}T{start_time}",
                    "end": f"{end_date}T{end_time}",
                    "resourceId": resource_id,
                })
                st.success(f"✅ Event '{title}' updated!")
                st.session_state["selected_event"] = None

            if delete_submitted:
                st.session_state["events"].remove(st.session_state["selected_event"])
                st.success(f"✅ Event '{title}' deleted!")
                st.session_state["selected_event"] = None
                st.rerun()
