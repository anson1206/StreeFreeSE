import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import uuid
import Database as DB  # Import database functions

class NCFCalendarScraper:
    def __init__(self, url):
        self.url = url
        self.events = []

    def fetch_calendar(self):
        """Fetches events from the given URL."""
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
                    if len(cols) >= 2:  # Ensure there are enough columns
                        date_text = cols[0].text.strip()
                        event_text = cols[1].text.strip()

                        # Convert date to proper format (YYYY-MM-DD)
                        try:
                            event_date = datetime.datetime.strptime(date_text, "%a, %b %d").replace(
                                year=datetime.datetime.today().year
                            ).date()
                        except ValueError:
                            continue  # Skip invalid dates

                        self.events.append({
                            "date": str(event_date),
                            "event": event_text
                        })

            return self.events
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching the calendar: {e}")
            return []

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
    st.title("🌐 Universal Event Scraper & Database Backup")
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
            df = scraper.get_dataframe()
            st.success(f"✅ Successfully scraped {len(scraped_events)} events!")
            st.write(df)
        else:
            st.warning("⚠️ No events found. Try another URL.")

    if st.session_state.get("scraped_events"):
        if st.button("Save Events to Calendar"):
            save_events_to_database(st.session_state["scraped_events"], user_id)
            st.session_state["scraped_events"] = []  # Clear the scraped events list
