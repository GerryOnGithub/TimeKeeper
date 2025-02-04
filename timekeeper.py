# installation
# Windows
#   pip install pyyaml
# Linux
#   sudo apt-get install python-yaml
#   sudo apt-get install python3-tk
import tkinter as tk
from   tkinter import ttk, messagebox, filedialog
import yaml
import csv
import os
from datetime import datetime
from collections import defaultdict

YAML_FILE = "tasks.yaml"
BACKUP_YAML_FILE = "tasks_backup.yaml"
DATE_FORMAT = "%Y-%m-%d %H:%M"

# _tasks = {"Away": [], "Scrum": []}
_tasks = {"": [] }
current_task = None
start_time = None
# flashing = False

# Load tasks from YAML file
def load_tasks(startup):
   global _tasks, current_task, start_time
   if os.path.exists(YAML_FILE):
        with open(YAML_FILE, 'r') as file:
           _tasks = yaml.load(file, Loader=yaml.UnsafeLoader)

        #if 'current_task' in tasks:
        #    current_task = tasks['current_task']
        #    start_time = datetime.strptime(tasks['start_time'], DATE_FORMAT)
        #    if startup == False:
        #        task_var.set(current_task)
   #else:
   #    save_tasks()

# Save tasks to YAML file
def save_tasks():
   tasks_to_save = _tasks.copy()
  # if current_task:
  #     tasks_to_save['current_task'] = current_task
  #     tasks_to_save['start_time'] = start_time.strftime(DATE_FORMAT)
   with open(YAML_FILE, 'w') as file:
       yaml.dump(tasks_to_save, file)

# Backup tasks to backup YAML file
def backup_tasks():
    with open(BACKUP_YAML_FILE, 'w') as file:
        yaml.dump(_tasks, file)

def on_closing():
    stop_task()
    save_tasks()
    root.destroy()

def start_task(task):
    global current_task, start_time
    if current_task:
        stop_task()
    #if task == "Away":
    #    current_task = task
    #    flash_away()
    #    return
    current_task = task
    start_time = datetime.now()
    update_running_time()

# Stop recording time for the current task
def stop_task():
    global current_task, start_time
    if current_task and start_time: # and current_task != "Away":
        end_time = datetime.now()
        # duration = (end_time - start_time).total_seconds() / 60  # duration in minutes
        duration = round((end_time - start_time).total_seconds() / 60)  # Round to nearest minute
        _tasks[current_task].append((start_time.strftime(DATE_FORMAT), duration))
        save_tasks()
    current_task = None
    start_time = None

# Update running time display
def update_running_time():
    if current_task and start_time:
        elapsed = datetime.now() - start_time
        running_time.set(f"{elapsed.seconds // 3600:02}:{(elapsed.seconds // 60) % 60:02}:{elapsed.seconds % 60:02}")
    else:
        running_time.set("00:00:00")
    root.after(1000, update_running_time)

# def flash_away():
#     global flashing
#    if task_var.get() == "Away":
#        if flashing:
#            running_time_label.config(background="red")
#        else:
#            running_time_label.config(background="white")
#        flashing = not flashing
#        root.after(500, flash_away)
#    else:
#        running_time_label.config(background="white")
#        flashing = False

def edit_yaml():
    if not os.path.exists(YAML_FILE):
        return

    current = current_task  # Store current task
    stop_task()  # Stop the current task if running
    backup_tasks()  # Backup current tasks

    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack(expand=True, fill=tk.BOTH)

    editor_window = tk.Toplevel(frame)
    editor_window.title("Edit Tasks")

    text_area = tk.Text(frame, wrap=tk.WORD)
    text_area.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    with open(YAML_FILE, 'r') as file:
        text_area.insert(tk.END, file.read())

    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text_area.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_area.config(yscrollcommand=scrollbar.set)

    def save_changes():
        with open(YAML_FILE, 'w') as file:
            file.write(text_area.get("1.0", tk.END))
        load_tasks(False)  # Reload tasks from the edited YAML file
        task_dropdown['values'] = sorted(list(_tasks.keys()))
        if current:  # Restart previous task if it exists
            task_var.set(current)
            start_task(current)
        editor_window.destroy()

    def cancel_changes():
        if current:  # Restart previous task if it exists
            task_var.set(current)
            start_task(current)
        editor_window.destroy()

    save_button = tk.Button(editor_window, text="Save", command=save_changes)
    save_button.pack(side=tk.LEFT, padx=5, pady=5)

    cancel_button = tk.Button(editor_window, text="Cancel", command=cancel_changes)
    cancel_button.pack(side=tk.RIGHT, padx=5, pady=5)


def edit_yaml_test():
    root = tk.Tk()
    root.title("Text Widget with Scrollbar")

    frame = tk.Frame(root)
    frame.pack(expand=True, fill=tk.BOTH)

    text_area = tk.Text(frame, wrap=tk.WORD)
    text_area.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text_area.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_area.config(yscrollcommand=scrollbar.set)

    sample_text = "\n".join([f"Line {i}" for i in range(0, 101)]) # 100 lines of text
    text_area.insert(tk.END, sample_text)

def endofday():
    stop_task()
    task_var.set('')
    save_tasks()

# Initialize a dictionary to store summarized data
summary = defaultdict(lambda: defaultdict(float))

def summarize():
    summary = defaultdict(lambda: defaultdict(int))

    # Iterate over each task and its entries in the data dictionary
    for task, entries in _tasks.items():
        if task in ['start_time', 'current_task']:
            continue

        for entry in entries:
            try:
                date_str, duration = entry
                date_obj = datetime.strptime(date_str, DATE_FORMAT).date()
                formatted_date = date_obj.strftime("%Y-%m-%d")
                summary[formatted_date][task] += duration
            except ValueError as e:
                print(f"Error parsing date '{date_str}': {e}")

    return summary

# TODO if minutes are 0 write empty string
def export_to_csv():
    stop_task()
    summary = summarize()
    csv_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if csv_file:
        # Extract all unique dates and tasks
        dates = sorted(summary.keys())
        tasks = sorted({task for tasks in summary.values() for task in tasks})

        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(["Task"] + dates)

            # Write the data rows
            for task in tasks:
                row = [task]
                for date in dates:
                    row.append(summary.get(date, {}).get(task, 0))
                writer.writerow(row)

        os.startfile(csv_file)

# Function to handle delete key press
def on_delete_key(event):
    selected_task = task_var.get()
    if selected_task == "":
        return

    if selected_task and selected_task in _tasks:
        stop_task()
        del _tasks[selected_task]
        task_dropdown['values'] = list(_tasks.keys())
        task_var.set("")  # Set to empty value after deletion
        print(f"Deleted task: {selected_task}")
        save_tasks()

def on_task_selected(event):
    selected_task = task_var.get()
    #if selected_task == "Select Task":
    #    stop_task()
    #    return

    start_task(selected_task)
#    if selected_task == "Away":
#        flash_away()
#    else:
#        task_dropdown.config(foreground="black")

def on_task_changed(event):
    selected_task = task_var.get()
    if selected_task == "":
        save_tasks()

    if selected_task not in _tasks:
        _tasks[selected_task] = []
        #task_dropdown['values'] = sorted(list(_tasks.keys()))
        task_dropdown['values'] = sorted(list(_tasks.keys()), key=str.lower)
        save_tasks()

    start_task(selected_task)
#    if selected_task == "Away":
#        flash_away()
#    else:
#        task_dropdown.config(foreground="black")

def reset():
    response = messagebox.askyesno("Confirm Reset", "Are you sure you wish to reset all tasks to zero?")
    if response:
        stop_task()
        backup_tasks()
        for key in _tasks:
            _tasks[key].clear()
        task_dropdown['values'] = sorted(list(_tasks.keys()))
        save_tasks()

def on_lost_focus(event):
    selected_task = task_var.get()
#    if selected_task == "Select Task":
#        stop_task()
#        return

    if selected_task not in _tasks:
        _tasks[selected_task] = []
        #task_dropdown['values'] = list(_tasks.keys())
        task_dropdown['values'] = sorted(list(_tasks.keys()), key=str.lower)
        save_tasks()
        start_task(selected_task)

#    start_task(selected_task)
#    if selected_task == "Away":
#        flash_away()
#    else:
#        task_dropdown.config(foreground="black")

# Create main window
root = tk.Tk()
root.title("TK")
root.geometry("220x95")
root.attributes("-topmost", True)
root.configure(bg="#AAAADE") # rgb

def disable_maximize(event=None):
    root.state('normal')

root.bind('<Map>', disable_maximize)

# Dropdown for task selection
task_var = tk.StringVar(value="")
task_dropdown = ttk.Combobox(root, textvariable=task_var)
task_dropdown['values'] = sorted(list(_tasks.keys()))
task_dropdown.pack(pady=3, padx=3, fill=tk.X, expand=True, anchor='n')

task_dropdown.bind("<<ComboboxSelected>>", on_task_selected)
task_dropdown.bind("<Return>", on_task_changed)
task_dropdown.bind("<FocusOut>", on_lost_focus)
task_dropdown.bind("<Delete>", on_delete_key)

# Running time display
running_time = tk.StringVar(value="00:00:00")
running_time_label = tk.Label(root, textvariable=running_time, font=("Helvetica", 12))
running_time_label.pack(pady=0)

# button_frame = tk.Frame(root)
# button_frame.pack(side=tk.BOTTOM, pady=10)

button_frame = tk.Frame(root, bg=root.cget("bg"), highlightthickness=0, borderwidth=0)
button_frame.pack(side=tk.BOTTOM, pady=4)

edit_button = tk.Button(button_frame, text="Edit", command=edit_yaml)
edit_button.pack(side=tk.LEFT, padx=6, pady=3)

reset_button = tk.Button(button_frame, text="Reset", command=reset)
reset_button.pack(side=tk.LEFT, padx=6, pady=3)  # Use LEFT to keep them in the same row

eod_button = tk.Button(button_frame, text="EoD", command=endofday)
eod_button.pack(side=tk.LEFT, padx=6, pady=3)  # Use LEFT to keep them in the same row

export_button = tk.Button(button_frame, text="Export", command=export_to_csv)
export_button.pack(side=tk.LEFT, padx=6, pady=3)

# Load initial tasks and start the main loop
load_tasks(True)
task_dropdown['values'] = sorted(list(_tasks.keys()), key=str.lower)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
