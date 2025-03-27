import tkinter as tk
from tkinter import ttk, messagebox
import argparse
import time
import threading

''''
root.title("TK v1.09")
root.geometry("220x92")
root.configure(bg="#AAAADE") # rgb'
'''

class ReminderApp:
    def __init__(self, message="Reminder!", minutes=30):
        self.message = message
        self.minutes = minutes
        self.root = tk.Tk()
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#AAAADE") # rgb'
        self.root.withdraw()  # Hide the main window

    def show_reminder(self):
        messagebox.showinfo("Reminder", self.message)

    def run(self):
        while True:
            time.sleep(self.minutes * 60)
            self.show_reminder()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple reminder application.")
    parser.add_argument("message", nargs="?", default="Reminder!", help="The message to display in the reminder.")
    parser.add_argument("minutes", nargs="?", type=int, default=30, help="The number of minutes between reminders.")

    args = parser.parse_args()

    app = ReminderApp(message=args.message, minutes=args.minutes)

    # Run the reminder in a separate thread to prevent blocking
    reminder_thread = threading.Thread(target=app.run)
    reminder_thread.daemon = True  # Allow the main program to exit even if the thread is running
    reminder_thread.start()

    try:
        tk.mainloop()
    except KeyboardInterrupt:
        print("Exiting...")
