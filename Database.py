import streamlit as st
from supabase import create_client, Client
import datetime
import uuid

# Supabase credentials
url = "https://rpygalqqsnuajcsdbkut.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJweWdhbHFxc251YWpjc2Ria3V0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAxNjg3MDYsImV4cCI6MjA1NTc0NDcwNn0.ZFgjCTQAiHCuwubyfP1tdTajHRG96XsZWoPIRZYT60o"
supabase: Client = create_client(url, key)


def sign_in(email, password):
    """Sign in the user with email and password."""
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return response.user
    except Exception as e:
        st.error(f"Error signing in: {str(e)}")
        return None


def sign_up(email, password):
    try:
        # Sign up the user
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        # Print out the entire response for debugging
        print("Response from Supabase:", response)

        # Check if 'user' exists in response
        if response and "error" not in response:
            # Show a warning message instructing the user to verify their email
            st.warning("Account created! Please verify your email before signing in.")

            # Force the user to log in manually after verification
            return None  # Do not log the user in automatically
        else:
            st.error("Error creating account. Please try again.")
            st.write(response)  # Debugging info
            return None

    except Exception as e:
        st.error(f"Error creating account: {str(e)}")
        return None


def load_events(user_id):
    """Fetch events from Supabase for the user."""
    response = supabase.table("events").select("*").eq("user_id", user_id).execute()
    st.session_state["events"] = response.data


def save_event(event, user_id):
    """Save a new event to Supabase."""
    try:
        if isinstance(user_id, str):  # If user_id is a string, convert to UUID
            user_id = uuid.UUID(user_id)
        elif not isinstance(user_id, uuid.UUID):
            raise ValueError("user_id must be a valid UUID string or UUID object")

        if "id" in event:
            del event["id"]  # Ensure 'id' field is not included in the event data

        event["user_id"] = str(user_id)  # Add user_id as a string

        response = supabase.table("events").insert(event).execute()
        return response
    except ValueError as e:
        st.error(f"Error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")


def update_event(event_id, updated_event):
    """Update an event in Supabase."""
    response = supabase.table("events").update(updated_event).eq("id", event_id).execute()
    return response


def delete_event(event_id):
    try:
        # Ensure event_id is treated as a string (UUID)
        response = supabase.table("events").delete().eq("id", str(event_id)).execute()
        return response
    except Exception as e:
        st.error(f"Database error: {e}")



def login_page():
    """Display login page."""
    st.title("Login or Create Account")
    login_option = st.radio("Choose an option", ["Login", "Sign Up"])

    if login_option == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            user = sign_in(email, password)
            if user:
                st.session_state["user_id"] = user.id
                st.session_state["email"] = email
                st.session_state.logged_in = True  # Ensure logged_in state is updated
                load_events(user.id)  # Load events when user logs in
                st.rerun()  # Refresh the app to show the dashboard

    elif login_option == "Sign Up":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        sign_up_button = st.button("Create Account")

        if sign_up_button:
            user = sign_up(email, password)
            if user:
                st.session_state["user_id"] = user.id
                st.session_state["email"] = email
                st.session_state.logged_in = True  # Ensure logged_in state is updated
                load_events(user.id)  # Load events when user signs up
                # Redirect to the login page after sign up success
                st.session_state["signup_successful"] = True
                st.rerun()  # Refresh to show the login page with success message
                st.success("Account created successfully! Please log in to continue.")
                st.rerun()  # Forces the page to refresh and show login page