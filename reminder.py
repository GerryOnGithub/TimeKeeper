import tkinter as tk
# from tkinter import ttk, messagebox
import argparse
import time
import threading

root = None
stop_reminder = False

def disable_maximize(event = None):
    global root
    root.state('normal')

class ReminderApp:
    def __init__(self, message = "Reminder!", minutes = 30):
        self.message = message
        self.minutes = minutes
        self.root = tk.Tk()
        root = self.root
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#AAAADE") # rgb'
        self.root.bind('<Map>', disable_maximize)
        self.root.withdraw()  # Hide the main window
        # self.root.geometry("220x92")

    def show_reminder(self):
        # Create a toplevel window
        print(f"it's time")
        popup = tk.Toplevel(self.root)
        popup.title("Reminder")
        popup.configure(bg="#AAAADE")

        # Add a label with the message
        label = tk.Label(popup, text=self.message, padx=20, pady=10, bg="#AAAADE")
        label.pack()

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
