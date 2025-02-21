#This class handles the to do list functionality

import streamlit as st
import pandas as pd
from Timer import Timer

class todo:
    
    def __init__(self):
        self.tasks = []
        if 'kudoPoints' not in st.session_state:
            st.session_state['kudoPoints'] = 0  # Initialize in session state


    #User adds a task to the list
    def add_task(self, task, label):
        if 'todoList' not in st.session_state:
            st.session_state['todoList'] = []
        if task:
            st.session_state['todoList'].append({"task": task, "label": label, "done": False})
            st.success(f"Task '{task}' added with the label {label}")
        else:
            st.error("Please enter a task")

    #Goes through the list of tasks and displays them based on the label
    def display_tasks(self, label):
        if 'todoList' in st.session_state and st.session_state['todoList']:
            for i, task in enumerate(st.session_state['todoList']):
                if task["label"] == label:
                    if st.checkbox(task["task"], value=task["done"], key=f"{label}_{i}"):
                        if not task["done"]:
                            task["done"] = True
                            st.session_state['kudoPoints'] += 10  # Update session state
                            st.balloons()
    @staticmethod
    def get_kudo_points():
        return st.session_state.get('kudoPoints', 0)

