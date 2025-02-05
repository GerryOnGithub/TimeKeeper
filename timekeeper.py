"""
installation
 Windows
   pip install pyyaml
   pip install openpyxl pandas
 Linux
   sudo apt-get install python-yaml
   sudo apt-get install python3-tk
"""
import tkinter as tk
from   tkinter import ttk, messagebox, filedialog
import yaml
import csv
import os
import pandas as pd
from datetime import datetime
from collections import defaultdict

YAML_FILE = "tasks.yaml"
BACKUP_YAML_FILE = "tasks_backup.yaml"
DATE_FORMAT = "%Y-%m-%d %H:%M"

_tasks = {"": [] }
current_task = None
start_time = None

"""
Example of _tasks
{
    "coding": [
        ["2024-02-05", 120],
        ["2024-02-06", 90]
    ],
    "reading": [
        ["2024-02-05", 45],
        ["2024-02-06", 60]
    ],
    "start_time": "2024-02-05T08:00:00",
    "current_task": "coding"
}
"""

# Load tasks from YAML file
def load_tasks(startup):
   global _tasks, current_task, start_time
   if os.path.exists(YAML_FILE):
        with open(YAML_FILE, 'r') as file:
           _tasks = yaml.load(file, Loader=yaml.UnsafeLoader)

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
    if current_task and start_time and current_task != "":
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

    editor_window = tk.Toplevel()  # Use Toplevel, no new Tk()
    editor_window.title("Edit Tasks")

    frame = tk.Frame(editor_window)  # Attach frame to the editor window
    frame.pack(expand=True, fill=tk.BOTH)

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
        editor_window.destroy()  # Close only the edit window

    def cancel_changes():
        if current:  # Restart previous task if it exists
            task_var.set(current)
            start_task(current)
        editor_window.destroy()  # Close only the edit window

    save_button = tk.Button(editor_window, text="Save", command=save_changes)
    save_button.pack(side=tk.LEFT, padx=5, pady=5)

    cancel_button = tk.Button(editor_window, text="Cancel", command=cancel_changes)
    cancel_button.pack(side=tk.RIGHT, padx=5, pady=5)

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

def summarize_to_dataframe_values_good_structure_wrong(summary):
    # Convert the nested defaultdict to a list of dictionaries
    data = []
    for date, tasks in summary.items():
        row = {"date": date}
        row.update(tasks)  # Add task durations as columns
        data.append(row)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Fill missing task columns with 0 (in case not all tasks are present every day)
    df.fillna(0, inplace=True)

    return df

def summarize_to_dataframe(summary):
    data = []

    for task, entries in summary.items():
        #if not isinstance(entries, list):
        #    continue  # Skip non-list entries (e.g., metadata like 'start_time')

        for entry in entries:
            if isinstance(entry, list) and len(entry) == 2:
                date, duration = entry

                # if isinstance(date, str) and isinstance(duration, (int, float)):  # Validate types
                data.append({"task": task, "date": date, "duration": duration})

    # Create DataFrame
    df = pd.DataFrame(data)

    # Pivot to make tasks rows and dates columns
    df = df.pivot(index="task", columns="date", values="duration")

    # Fill missing values with 0
    df.fillna(0, inplace=True)

    return df

def summarize_to_dataframe_ugly(summary):
    data = []

    for task, entries in summary.items():
        # Ensure task data is a list of [date, duration] pairs
        if not isinstance(entries, list):
            continue  # Skip non-list entries (e.g., metadata like 'start_time')

        for entry in entries:
            if isinstance(entry, list) and len(entry) == 2:
                date, duration = entry
                if isinstance(date, str) and isinstance(duration, (int, float)):  # Validate types
                    data.append({"task": task, "date": date, "duration": duration})

    # Create DataFrame
    df = pd.DataFrame(data)

    # Pivot to make tasks rows and dates columns
    df = df.pivot(index="task", columns="date", values="duration")

    # Fill missing values with 0
    df.fillna(0, inplace=True)

    return df

def export_to_csv():
    stop_task()
    summary = summarize()
#    dataframe = summarize_to_dataframe(summary);

    data = []
    csv_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if csv_file:
        # Extract all unique dates and tasks
        dates = sorted(summary.keys())
        tasks = sorted({task for tasks in summary.values() for task in tasks})
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Task"] + dates) # Write the header row
            data.append(["Task"] + dates) # Write the header row
            # Write the data rows
            for task in tasks:
                row = [task]
                for date in dates:
                    # Convert minutes to hours, round to 1 decimal place
                    # If minutes are 0, write an empty string
                    duration = summary.get(date, {}).get(task, 0)
                    row.append(f"{duration/60:.1f}" if duration > 0 else "")
                writer.writerow(row)
                data.append(row)

            # Add total row
            total_row = ["Total"]
            for date in dates:
                daily_total = sum(summary.get(date, {}).get(task, 0) for task in tasks)
                total_row.append(f"{daily_total/60:.1f}" if daily_total > 0 else "")
            writer.writerow(total_row)
            data.append(total_row)

            # for .xlsx
            # total_row = ["Total"] + [f"=SUM(B{len(tasks)+2}:B{len(tasks)+1+dates_count})" for dates_count in range(len(dates))]

        dataframe = pd.DataFrame(data)
        with pd.ExcelWriter("./test.xlsx", engine='openpyxl') as writer:
            dataframe.to_excel(writer, index=False)

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
        save_tasks()

    resize_dropdown()

def on_task_selected(event):
    # print(f"task selected")
    selected_task = task_var.get()
    if selected_task == current_task:
        return;
    if selected_task != current_task:
        on_task_changed(event)
    #if selected_task == "Select Task":
    #    stop_task()
    #    return
    # start_task(selected_task)

def on_task_changed(event):
    # print(f"task changed")
    selected_task = task_var.get()
    if selected_task == current_task:
        return;

    if selected_task not in _tasks:
        _tasks[selected_task] = []
        save_tasks()  # Save immediately
        # load_tasks(False)  # Reload tasks from file (ensures consistency)

        # Explicitly update dropdown values
        # task_dropdown['values'] = sorted(list(_tasks.keys()))
        sort_tasks()
        task_var.set(selected_task)  # necessary?
        resize_dropdown()

    start_task(selected_task)
    print(f"start task: {selected_task}")

def on_lost_focus(event):
    # print(f"lost focus")
    selected_task = task_var.get()
    if selected_task == current_task:
        return;

    if selected_task not in _tasks:
        _tasks[selected_task] = []
        #task_dropdown['values'] = list(_tasks.keys())
        #task_dropdown['values'] = sorted(list(_tasks.keys()), key=str.lower)
        sort_tasks()
        save_tasks()
        start_task(selected_task)

def on_task_changed_old(event):
    print(f"task changed")
    selected_task = task_var.get()
    if selected_task not in _tasks:
        _tasks[selected_task] = []
        save_tasks()
        load_tasks()
        sort_tasks()
        resize_dropdown()

    start_task(selected_task)
    print(f"start task: {selected_task}")

def sort_tasks():
    task_dropdown['values'] = sorted(list(_tasks.keys()), key=str.lower)

def reset():
    response = messagebox.askyesno("Confirm Reset", "Are you sure you wish to reset all tasks to zero?")
    if response:
        stop_task()
        backup_tasks()
        for key in _tasks:
            _tasks[key].clear()
        sort_tasks()
        save_tasks()

# Create main window
root = tk.Tk()
root.title("TK")
root.geometry("220x95")
root.attributes("-topmost", True)
root.configure(bg="#AAAADE") # rgb

def disable_maximize(event=None):
    root.state('normal')

def resize_dropdown():
    task_dropdown.config(height=len(task_dropdown['values']))

root.bind('<Map>', disable_maximize)

load_tasks(True)

# Dropdown for task selection
task_var = tk.StringVar(value="")
task_dropdown = ttk.Combobox(root, textvariable=task_var)
task_dropdown['values'] = sorted(list(_tasks.keys()))
task_dropdown.pack(pady=3, padx=3, fill=tk.X, expand=True, anchor='n')

# task_dropdown.config(height=len(task_dropdown['values']))
resize_dropdown()
sort_tasks()

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

task_dropdown['values'] = sorted(list(_tasks.keys()), key=str.lower)

root.protocol("WM_DELETE_WINDOW", on_closing)

print(f"running...")
root.mainloop()