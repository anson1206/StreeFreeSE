import time
import streamlit as st

class TaskTime:

    def __init__(self):
        if "timer_running" not in st.session_state:
            st.session_state.timer_running = False
        if "start_time" not in st.session_state:
            st.session_state.start_time = 0
        if "elapsed_time" not in st.session_state:
            st.session_state.elapsed_time = 0
        if "current_task" not in st.session_state:
            st.session_state.current_task = ""
        if "task_times" not in st.session_state:
            st.session_state.task_times = []
        if "last_break" not in st.session_state:
            st.session_state.last_break = time.time()
        if "break_shown" not in st.session_state:
            st.session_state.break_shown = False

    #Starts the timer
    def start_timer(self, task_name):
        st.session_state.start_time = time.time()
        st.session_state.timer_running = True
        st.session_state.current_task = task_name

    #Stops the timer
    def stop_timer(self):
        st.session_state.timer_running = False
        elapsed_time = time.time() - st.session_state.start_time
        st.session_state.elapsed_time += elapsed_time
        st.session_state.task_times.append({
            "task": st.session_state.current_task,
            "time": st.session_state.elapsed_time
        })
        # Reset elapsed time for the next task
        st.session_state.elapsed_time = 0

    #Displays the timer
    def display_timer(self):
        timer_placeholder = st.empty()
        #shows the timer
        while st.session_state.timer_running:
            elapsed_time = time.time() - st.session_state.start_time + st.session_state.elapsed_time
            mins, sec = divmod(elapsed_time, 60)
            timer_placeholder.write(f"Task: {st.session_state.current_task} | Time elapsed: {int(mins)} minutes {int(sec)} seconds")
            time.sleep(1)
            #checks if a certain aqmount of time has passed and gives a message
            if elapsed_time >= 15 and not st.session_state.break_shown:
                st.toast("Take a break!")
                st.session_state.break_shown = True
        if not st.session_state.timer_running:
            elapsed_time = st.session_state.elapsed_time
            mins, sec = divmod(elapsed_time, 60)
            timer_placeholder.write(f"Task: {st.session_state.current_task} | Time elapsed: {int(mins)} minutes {int(sec)} seconds")

    #Shows the tasks with their times
    def show_task_times(self):
        if st.session_state.task_times:
            st.write("Task Times")
            for idx, task_time in enumerate(st.session_state.task_times):
                mins, sec = divmod(task_time["time"], 60)
                st.write(f"{idx + 1}. Task: {task_time['task']} | Time: {int(mins)} minutes {int(sec)} seconds")
        else:
            st.write("No tasks yet")

    #Deletes a task
    def delete_task(self, task_index):
        if 0 <= task_index < len(st.session_state.task_times):
            del st.session_state.task_times[task_index]