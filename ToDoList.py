#This class handles the to do list functionality

import streamlit as st
import pandas as pd
from Timer import Timer
from supabase import create_client

# Initialize Supabase
supabase_url = "https://rpygalqqsnuajcsdbkut.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJweWdhbHFxc251YWpjc2Ria3V0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAxNjg3MDYsImV4cCI6MjA1NTc0NDcwNn0.ZFgjCTQAiHCuwubyfP1tdTajHRG96XsZWoPIRZYT60o"
supabase = create_client(supabase_url, supabase_key)

class todo:
    def __init__(self, user_id):
        self.user_id = user_id  # Store user_id
        if 'kudoPoints' not in st.session_state:
            # Fetch from DB and ensure it doesn't return None
            st.session_state['kudoPoints'] = self.get_kudo_points_from_db() or 0  # Fallback to 0 if None
    
    def add_task(self, task, label):
        if 'todoList' not in st.session_state:
            st.session_state['todoList'] = []
        if task:
            st.session_state['todoList'].append({"task": task, "label": label, "done": False})
            st.success(f"Task '{task}' added with the label {label}")
        else:
            st.error("Please enter a task")

    def display_tasks(self, label):
        if 'todoList' in st.session_state and st.session_state['todoList']:
            for i, task in enumerate(st.session_state['todoList']):
                if isinstance(task, dict) and task.get("label") == label:
                    checked = st.checkbox(task["task"], value=task["done"], key=f"{task['task']}_{label}_{i}")

                    if checked and not task["done"]:
                        task["done"] = True
                        # Ensure 'kudoPoints' is an integer before incrementing
                        if isinstance(st.session_state['kudoPoints'], int):
                            st.session_state['kudoPoints'] += 10  # Add points
                            self.update_kudo_points_in_db(10)  # Update DB
                        else:
                            st.session_state['kudoPoints'] = 10  # Initialize if not a valid integer
                        # Move task from "In Progress" or "Important" to "Done"
                        if task["label"] in ["In Progress", "Important"]:
                            task["label"] = "Done"
                        st.rerun()

    def get_kudo_points_from_db(self):
        """ Fetch the user's kudo points from Supabase """
        response = supabase.table("events").select("kudo_points").eq("user_id", self.user_id).execute()
        if response.data:
            return response.data[0]["kudo_points"]  # Return stored points
        return 0  # Default if no record found

    def update_kudo_points_in_db(self, points):
        """ Update kudo points in Supabase """
        current_points = self.get_kudo_points_from_db()  # Get current points
        if current_points is None:  # Just in case the value is None
            current_points = 0
        new_points = current_points + points  # Add new points
        supabase.table("events").update({"kudo_points": new_points}).eq("user_id", self.user_id).execute()

