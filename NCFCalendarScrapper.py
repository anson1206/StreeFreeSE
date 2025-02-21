import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import uuid

class NCFCalendarScraper:
    def __init__(self, url="https://www.ncf.edu/academics/academic-calendar/"):
        self.url = url
        self.academic_events = []

    def fetch_calendar(self):
        """Fetches the NCF academic calendar and parses events."""
        headers = {
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) == 2:
                        date_text = cols[0].text.strip()
                        event_text = cols[1].text.strip()

                        # Convert date to proper format (YYYY-MM-DD)
                        try:
                            event_date = datetime.datetime.strptime(date_text, "%a, %b %d").replace(year=datetime.datetime.today().year).date()
                        except ValueError:
                            continue  # Skip invalid dates

                        self.academic_events.append({
                            "date": str(event_date),
                            "event": event_text
                        })

            return self.academic_events
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching the calendar: {e}")
            return []

    def get_dataframe(self):
        """Returns the scraped academic calendar as a DataFrame."""
        return pd.DataFrame(self.academic_events)

def scraper_page():
    st.title("📅 NCF Academic Calendar Scraper")
    st.write("Click the button below to fetch academic events from NCF.")

    scraper = NCFCalendarScraper()

    # Ensure scraped events are stored temporarily before adding them to the calendar
    if "scraped_events" not in st.session_state:
        st.session_state["scraped_events"] = []

    if st.button("Scrape NCF Calendar"):
        scraped_events = scraper.fetch_calendar()
        if scraped_events:
            st.session_state["scraped_events"] = scraped_events  # Store in session state
            df = scraper.get_dataframe()
            st.success(f"Successfully scraped {len(scraped_events)} events!")
            st.write(df)
        else:
            st.warning("No events found. Please try again later.")

    # Only show this button if events were scraped
    if st.session_state["scraped_events"]:
        if st.button("Add Events to Calendar"):
            if "events" not in st.session_state:
                st.session_state["events"] = []  # Ensure events list exists

            # Create a set of existing event titles in the calendar
            existing_event_titles = {event["title"] for event in st.session_state["events"]}

            # Convert events into the format used in `calendar.py`
            for event in st.session_state["scraped_events"]:
                if event["event"] not in existing_event_titles:  # Prevent duplicates
                    new_event = {
                        "id": str(uuid.uuid4()),  # Add unique id
                        "title": event["event"],
                        "color": "#FF5733",  # Default color
                        "start": f"{event['date']}T09:00:00",  # Default 9 AM
                        "end": f"{event['date']}T10:00:00",  # Default 10 AM
                        "resourceId": "a"  # Assign default resource
                    }
                    st.session_state["events"].append(new_event)
                    existing_event_titles.add(event["event"])  # Add to set to track duplicates

            # Clear scraped events after adding
            st.session_state["scraped_events"] = []
            st.success("✅ Events added to your calendar! Go to the Dashboard to see them.")