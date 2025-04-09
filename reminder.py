'''
tasklist /FI "IMAGENAME eq python.exe"
taskkill /PID 33676 /F
'''

import tkinter as tk
# from tkinter import ttk, messagebox
import argparse
import time
import threading
import datetime

# root = None
stop_reminder = False

class ReminderApp:
    def __init__(self, message = "Reminder!", minutes = 30):
        # global root
        self.message = message
        self.minutes = minutes
        self.root = tk.Tk()
        #root = self.root
        #self.root.attributes("-topmost", True)
        #self.root.configure(bg="#AAAADE") # rgb'
        # self.root.geometry("220x92")
        self.root.withdraw()  # Hide the main window

#   def show_reminder(self):
#       # Create a toplevel window
#       popup = tk.Toplevel(self.root)
#       popup.title("Reminder")
#       popup.configure(bg="#AAAADE")

#       # Add a label with the message
#       label = tk.Label(popup, text=self.message, padx=20, pady=10, bg="#AAAADE")
#       label.pack()


    def run(self):
        global stop_reminder
        while not stop_reminder:
            print("sleeping... ")
            time.sleep(self.minutes * 60)
            if not stop_reminder:
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print(f"it's time {current_time}")
                popup = tk.Toplevel(self.root)
                popup.attributes("-topmost", True) # Make the popup topmost
                popup.title("Reminder")
                popup.configure(bg="#AAAADE")
                popup.geometry("220x40")
                popup.minsize(220, 40)
                popup.maxsize(920, 40)

                # Add a label with the message
                label = tk.Label(popup, text=self.message, padx=20, pady=10, bg="#AAAADE")
                label.pack()
                popup.wait_window()

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
        print("exiting...")
