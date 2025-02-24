import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import uuid
import Database as DB  # Import database functions
import re
import datetime

class NCFCalendarScraper:
    def __init__(self, url):
        self.url = url
        self.events = []

    def fetch_calendar(self):
        """Fetches events from the given URL, handling various formats."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Try extracting data from tables first
            tables = soup.find_all("table")
            if tables:
                for table in tables:
                    rows = table.find_all("tr")
                    for row in rows:
                        cols = row.find_all(["td", "th"])
                        if len(cols) >= 2:
                            date_text = cols[0].get_text(strip=True)
                            event_text = cols[1].get_text(strip=True)
                            self.process_event(date_text, event_text)
            else:
                st.warning("⚠️ No tables found. Trying alternate formats...")

                # Try extracting events from lists or divs
                possible_event_blocks = soup.find_all(["li", "div", "p"])
                for block in possible_event_blocks:
                    text = block.get_text(strip=True)
                    if self.is_potential_event(text):
                        date_text, event_text = self.split_event_text(text)
                        self.process_event(date_text, event_text)

            if not self.events:
                st.warning("⚠️ No events extracted. The webpage structure may have changed.")

            return self.events

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching the calendar: {e}")
            return []

    def is_potential_event(self, text):
        """Checks if a text block contains a valid date and event."""
        try:
            parts = text.split(" - ", 1)  # Split on dash, common in academic calendars
            if len(parts) == 2:
                datetime.datetime.strptime(parts[0].strip(), "%b %d, %Y")  # Validate date format
                return True
        except ValueError:
            return False
        return False

    def split_event_text(self, text):
        """Splits a text block into a date and event text."""
        parts = text.split(" - ", 1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        return "", ""

    def process_event(self, date_text, event_text):
        """Converts date to YYYY-MM-DD format and stores the event."""
        try:
            event_date = self.parse_date(date_text)
            if event_date:
                self.events.append({
                    "date": str(event_date),
                    "event": event_text
                })
        except ValueError:
            st.warning(f"Skipping invalid date format: {date_text}")



    def parse_date(self, date_text):
        """Parses dates, including single dates and date ranges."""
        date_text = date_text.replace("–", "-")  # Normalize dashes
        current_year = datetime.datetime.today().year  # Get current year

        # 🔹 Handle date ranges (e.g., "Apr 9 - Aug 30")
        match = re.search(r"(\b[A-Za-z]{3,9}) (\d{1,2})\s*-\s*(\b[A-Za-z]{3,9})? (\d{1,2}),?\s*(\d{4})?", date_text)
        if match:
            start_month, start_day, end_month, end_day, year = match.groups()
            if not year:
                year = current_year  # Use current year if missing
            if not end_month:
                end_month = start_month  # If only one month is provided, assume same month
            date_text = f"{start_month} {start_day}, {year}"  # Take the start date only

        # 🔹 Handle single dates (e.g., "Mon, Sept 2" or "Wed, July 4")
        match = re.search(r"(\b[A-Za-z]{3,9}) (\d{1,2}),?\s*(\d{4})?", date_text)
        if match:
            month, day, year = match.groups()
            if not year:
                year = current_year  # If year is missing, use current year
            date_text = f"{month} {day}, {year}"

        # 🔹 Common date formats
        date_formats = [
            "%b %d, %Y",  # Example: "Jan 22, 2024"
            "%B %d, %Y",  # Example: "January 22, 2024"
            "%m/%d/%Y",  # Example: "01/22/2024"
        ]

        # 🔹 Try parsing the extracted date
        for fmt in date_formats:
            try:
                return datetime.datetime.strptime(date_text, fmt).date()
            except ValueError:
                continue  # Try the next format

        st.warning(f"⚠️Possible Missed Event check this date: {date_text}")
        return None

    def get_dataframe(self):
        """Returns the scraped events as a DataFrame."""
        return pd.DataFrame(self.events)


def save_events_to_database(events, user_id):
    """Saves scraped events to the database and adds them to session state like manually added events."""
    if not events:
        st.warning("No events to save.")
        return

    # Ensure session state has 'events'
    if 'events' not in st.session_state or st.session_state['events'] is None:
        st.session_state['events'] = []  # Initialize empty list if needed

    for event in events:
        try:
            new_event = {
                "id": str(uuid.uuid4()),  # Unique ID like manual events
                "title": event["event"],
                "color": "#FF5733",  # Default color (can be changed)
                "start": f"{event['date']}T09:00:00",
                "end": f"{event['date']}T10:00:00",
                "resource_id": "a",  # Default resource (can be changed)
            }

            # ✅ Add to session state just like manually added events
            if new_event not in st.session_state["events"]:
                st.session_state["events"].append(new_event)

            # ✅ Save to Supabase exactly like manually added events
            DB.save_event(new_event, user_id)

        except Exception as e:
            st.error(f"Failed to save event '{event['event']}': {e}")

    st.success("✅ Scraped events added to the calendar and saved to the database!")


def scraper_page():
    st.title("🌐 Website Event Scraper")
    st.write("Enter a URL containing a table of events, and we'll scrape & store them!")

    url = st.text_input("Enter the event webpage URL:", value="https://www.ncf.edu/academics/academic-calendar/")
    user_id = st.session_state.get("user_id")  # Ensure user is logged in

    if not user_id:
        st.error("⚠️ Please log in before scraping events.")
        return

    scraper = NCFCalendarScraper(url)

    if st.button("Scrape Events"):
        scraped_events = scraper.fetch_calendar()
        if scraped_events:
            st.session_state["scraped_events"] = scraped_events
            st.session_state["selected_events"] = []
            st.success(f"✅ Successfully scraped {len(scraped_events)} events!")
        else:
            st.warning("⚠️ No events found. Try another URL.")

    if "scraped_events" in st.session_state and st.session_state["scraped_events"]:
        st.subheader("📅 Review & Select Events to Add")

        # Convert events into a dropdown-friendly format
        event_options = [f"{event['date']} - {event['event']}" for event in st.session_state["scraped_events"]]

        # Dropdown multiselect for event selection
        selected_options = st.multiselect("Select events to add:", event_options, default=[])

        # "Save Selected Events" Button
        if st.button("Save Selected Events"):
            selected_events = [event for event in st.session_state["scraped_events"]
                               if f"{event['date']} - {event['event']}" in selected_options]

            if selected_events:
                save_events_to_database(selected_events, user_id)

                # 🔄 Ensure scraped events are fully merged into session state "events"
                if "events" not in st.session_state or not isinstance(st.session_state["events"], list):
                    st.session_state["events"] = []

                for event in selected_events:
                    new_event = {
                        "id": str(uuid.uuid4()),  # Ensure unique ID
                        "title": event["event"],
                        "color": "#FF5733",
                        "start": f"{event['date']}T09:00:00",
                        "end": f"{event['date']}T10:00:00",
                        "resource_id": "a",
                    }
                    if new_event not in st.session_state["events"]:
                        st.session_state["events"].append(new_event)

                # 🔄 Trigger UI refresh
                st.session_state["calendar_refresh"] += 1
                st.rerun()
            else:
                st.warning("⚠️ No events selected. Please choose at least one event.")

        # "Save All Events" Button
        if st.button("Save All Events"):
            save_events_to_database(st.session_state["scraped_events"], user_id)

            # 🔄 Ensure all scraped events are merged into session state "events"
            if "events" not in st.session_state or not isinstance(st.session_state["events"], list):
                st.session_state["events"] = []

            for event in st.session_state["scraped_events"]:
                new_event = {
                    "id": str(uuid.uuid4()),
                    "title": event["event"],
                    "color": "#FF5733",
                    "start": f"{event['date']}T09:00:00",
                    "end": f"{event['date']}T10:00:00",
                    "resource_id": "a",
                }
                if new_event not in st.session_state["events"]:
                    st.session_state["events"].append(new_event)

            # 🔄 Trigger UI refresh
            st.session_state["calendar_refresh"] += 1
            st.rerun()



