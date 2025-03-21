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
import time
import threading
import os
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

YAML_FILE = "tasks.yaml"
DATE_FORMAT = "%Y-%m-%d %H:%M"

_tasks = {"": [] }
current_task = None
start_time = None
flashing = False
red = False

"""
Example of _tasks, duration in minutes
{
    "coding": [
        ["2024-02-05", 180],
        ["2024-02-06", 43]
    ],
    "reading": [
        ["2024-02-05", 91],
        ["2024-02-06", 45]
    ],
    "start_time": "2024-02-05T08:00:00",
    "current_task": "coding"
}
"""

# Load tasks from YAML file
def load_tasks_from_disk():
   global _tasks, current_task, start_time
   if os.path.exists(YAML_FILE):
        with open(YAML_FILE, 'r') as file:
           _tasks = yaml.load(file, Loader=yaml.UnsafeLoader)

# Save tasks to YAML file
def save_tasks():
   tasks_to_save = _tasks.copy()
   with open(YAML_FILE, 'w') as file:
       yaml.dump(tasks_to_save, file)
   print(f"tasks saved to disk")

# Backup tasks to backup YAML file
def backup_tasks():
    filename = f"backup_{datetime.now().strftime('%A').lower()}.yaml"
    with open(filename, 'w') as file:
        yaml.dump(_tasks, file)
    filename = f"backup_{datetime.now().strftime('%A').lower()}.xlsx"
    continue_export_to_excel(filename, False)
    print(f"tasks back up ran")

def on_closing():
    stop_task()
    save_tasks()
    root.destroy()

def start_task(task):
    global current_task, start_time
    if current_task:
        stop_task()
    current_task = task
    start_time = datetime.now()
    update_running_time()

def stop_task():
    global current_task, start_time
    if current_task and start_time and current_task != "":
        end_time = datetime.now()
       # duration = round((end_time - start_time).total_seconds()) # seconds
        duration = round((end_time - start_time).total_seconds() / 60) # round to nearest minute
        _tasks[current_task].append((start_time.strftime(DATE_FORMAT), duration))
        save_tasks()
    current_task = None
    start_time = None

def update_running_time():
    if current_task and start_time:
        elapsed = datetime.now() - start_time
        running_time.set(f"{elapsed.seconds // 3600:02}:{(elapsed.seconds // 60) % 60:02}:{elapsed.seconds % 60:02}")
    else:
        running_time.set("00:00:00")
        if not flashing:
            flash_idle()
    root.after(1000, update_running_time)

def edit_yaml():
    if not os.path.exists(YAML_FILE):
        return

    current = current_task  
    stop_task() 
    backup_tasks()
    dropdown_string.set('')

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
        load_tasks_from_disk()  # Reload tasks from the edited YAML file
        load_tasks()
        resize_dropdown()
        if current:  # Restart previous task if it exists
            dropdown_string.set(current)
            start_task(current)
        editor_window.destroy()

    def cancel_changes():
        if current:  # Restart previous task if it exists
            dropdown_string.set(current)
            start_task(current)
        editor_window.destroy() 

    save_button = tk.Button(editor_window, text=" Save ", command=save_changes, bg="green", fg="white")
    save_button.pack(side=tk.LEFT, padx=5, pady=5)

    cancel_button = tk.Button(editor_window, text="Cancel", command=cancel_changes, bg="red", fg="white")
    cancel_button.pack(side=tk.RIGHT, padx=5, pady=5)

def end_of_day():
    stop_task()
    backup_tasks()
    dropdown_string.set('')
    save_tasks()
    flash_idle();

def show_reminder():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Reminder", "Please select a task to start your day!")
    root.destroy()

def flash():
    global red
    if red:
        running_time_label.config(background="red")
    else:
        running_time_label.config(background="white")
    red = not red

def flash_idle():
    global red
    global flashing

    if dropdown_string.get() == "":
        flashing = True 
        flash()
        root.after(999, flash_idle)
    else:
        flashing = False
        red = False
        flash()

# set a time for 6am. when the user signs on they will see this reminder to pick a task to start the day 
def schedule_reminder():
    now = datetime.now()
    target_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)
    time_to_wait = (target_time - now).total_seconds()
    time.sleep(time_to_wait)
    show_reminder()

def summarize():
    global current_task;
    if current_task:
        stop_task()
    dropdown_string.set('')

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

def maybe_export_to_excel():
    xlsx_file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if xlsx_file:
        continue_export_to_excel(xlsx_file, True)

def continue_export_to_excel(xlsx_file, launch):
    summary = summarize()

    data = []
    # xlsx_file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if xlsx_file:
        # Extract unique dates and tasks
        dates = sorted(summary.keys())  # Keep dates in normal order (Monday → Friday)
        tasks = sorted({task for tasks in summary.values() for task in tasks})

        data.append(["Tasks"] + dates)  # Create header row

        # Create data rows
        rows = []
        for task in tasks:
            row = [task]
            for date in dates:
                duration = summary.get(date, {}).get(task, 0)
                row.append(round(duration / 60, 2) if duration > 0 else None)
            rows.append(row)

        # Reverse sort date rows by task time (None at the bottom) to create a cascade of tasks M-F
        for col in reversed(range(1, len(dates) + 1)):  # sorting last date to first
            rows.sort(key=lambda x: (x[col] is None, x[col] if x[col] is not None else 0))

        data.extend(rows)  # Append sorted rows back

        columns = ["B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"] # should be enough...
        if len(columns) > len(dates):
            columns = columns[:len(dates)] # truncate to match number of dates
        sum_row = ["Sum"] + [f"=SUM({col}2:{col}{len(tasks)+1})" for col in columns]
        data.append(sum_row)

        dataframe = pd.DataFrame(data)
        # dataframe.fillna(0, inplace=True) # use this to prefill with 0's
        with pd.ExcelWriter(xlsx_file, engine='openpyxl') as writer:
            dataframe.to_excel(writer, index=False, header=False) # header is annoying...

        if launch:
            os.startfile(xlsx_file)

# Function to handle delete key press
def on_delete_key(event):
    selected_task = dropdown_string.get()
    if selected_task == "":
        return

    if selected_task and selected_task in _tasks:
        dropdown_string.set("")
        stop_task()
        del _tasks[selected_task]
        load_tasks()
        resize_dropdown()
        save_tasks()

def on_task_selected(event):
    # print(f"task selected")
    selected_task = dropdown_string.get()
    if selected_task == current_task:
        return;
    if selected_task != current_task:
        on_task_changed(event)

def on_task_changed(event):
    print(f"task changed...")
    selected_task = dropdown_string.get()
    if selected_task == current_task:
        return;

    if selected_task not in _tasks:
        _tasks[selected_task] = []
        save_tasks()  # Save immediately
        # load_tasks(False)  # Reload tasks from file (ensures consistency)

        # explicitly update dropdown values
        load_tasks()
        resize_dropdown()
        dropdown_string.set(selected_task)

    start_task(selected_task)
    print(f"start task: {selected_task}")

def on_lost_focus(event):
    # print(f"lost focus")
    selected_task = dropdown_string.get()
    if selected_task == current_task:
        return;

    if selected_task not in _tasks:
        _tasks[selected_task] = []
        load_tasks()
        resize_dropdown()
        save_tasks()
        start_task(selected_task)

# sort useful? yes and no...
def load_sort_tasks(sort):
    if sort == True:
        task_dropdown['values'] = sorted(list(_tasks.keys()), key=str.lower)
    else:
        task_dropdown['values'] = list(_tasks.keys())
    resize_dropdown()

def load_tasks():
    task_dropdown['values'] = list(_tasks.keys())

def reset():
    response = messagebox.askyesno("Confirm Reset", "Are you sure you wish to reset all tasks to zero?")
    if response:
        stop_task()
        backup_tasks()
        for key in _tasks:
            _tasks[key].clear()
        load_tasks()
        resize_dropdown()
        save_tasks()

def disable_maximize(event=None):
    root.state('normal')

def resize_dropdown():
    task_dropdown.config(height=len(task_dropdown['values']))

root = tk.Tk() # create main window
root.title("TK v1.08")
root.geometry("220x92")
root.attributes("-topmost", True)
root.configure(bg="#AAAADE") # rgb

root.bind('<Map>', disable_maximize)

load_tasks_from_disk()

dropdown_string = tk.StringVar(value="") # this string var represents the current value displayed in task_dropdown (below)

# dropdown for task selection
task_dropdown = ttk.Combobox(root, textvariable=dropdown_string)
task_dropdown.pack(pady=3, padx=3, fill=tk.X, expand=True, anchor='n')
load_tasks()
resize_dropdown()

task_dropdown.bind("<<ComboboxSelected>>", on_task_selected)
task_dropdown.bind("<Return>", on_task_changed)
task_dropdown.bind("<FocusOut>", on_lost_focus)
task_dropdown.bind("<Delete>", on_delete_key)

# running time display
running_time = tk.StringVar(value="00:00:00")
running_time_label = tk.Label(root, textvariable=running_time, font=("Helvetica", 12))
running_time_label.pack(pady=0)

button_frame = tk.Frame(root, bg=root.cget("bg"), highlightthickness=0, borderwidth=0)
button_frame.pack(side=tk.BOTTOM, pady=4)

eod_button = tk.Button(button_frame, text="EoD", command=end_of_day, bg="dark grey")
eod_button.pack(side=tk.LEFT, padx=6, pady=3)  # Use LEFT to keep them in the same row

export_button = tk.Button(button_frame, text="Export", command=maybe_export_to_excel, bg="green", fg="white")
export_button.pack(side=tk.LEFT, padx=6, pady=3)

edit_button = tk.Button(button_frame, text="Edit", command=edit_yaml, bg="#ADD8E6", fg="blue")
edit_button.pack(side=tk.LEFT, padx=6, pady=3)

reset_button = tk.Button(button_frame, text="Reset", command=reset, bg="#B22222", fg="white")
reset_button.pack(side=tk.LEFT, padx=6, pady=3)  # Use LEFT to keep them in the same row

task_dropdown['values'] = sorted(list(_tasks.keys()), key=str.lower)

root.protocol("WM_DELETE_WINDOW", on_closing)

# reminder for user to select a task at the beginning of the day
#reminder_thread = threading.Thread(target=schedule_reminder)
#reminder_thread.daemon = True
#reminder_thread.start()

print(f"running...")
root.mainloop()
