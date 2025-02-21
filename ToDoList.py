#This class handles the to do list functionality

import streamlit as st
import pandas as pd
from Timer import Timer

class todo:
    
    def __init__(self):
        self.tasks = []
        if 'kudoPoints' not in st.session_state:
            st.session_state['kudoPoints'] = 0  # Initialize in session state
        if 'todoList' not in st.session_state:
            st.session_state['todoList'] = []  # Initialize in session state



    #User adds a task to the list
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
                    # Ensure unique key
                    checked = st.checkbox(task["task"], value=task["done"], key=f"{task['task']}_{label}_{i}")

                    if checked and not task["done"]:
                        task["done"] = True
                        st.session_state['kudoPoints'] += 10  # Award Kudo Points

                        # Move task from "In Progress" or "Important" to "Done"
                        if task["label"] in ["In Progress", "Important"]:
                            task["label"] = "Done"

                        st.rerun()  # Refresh UI
                        st.balloons()  # Celebrate with balloons
    @staticmethod
    def get_kudo_points():
        return st.session_state.get('kudoPoints', 0)

