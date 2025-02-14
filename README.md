# TimeKeeper
Python program to track time.

![Alt-text](images/tk-1.png)

Goal 1: track time with the least amount of distruption

Goal 2: track time with the least amount of distraction

Goal 3: track time with the least amount of effort

### Install dependencies
pip install pyyaml

#### windows
pip install pyyaml

#### linux
sudo apt-get install python-yaml

sudo apt-get install python3-tk

### How To

To run: python ./timekeeper.v2.py

To start tracking: type a task name then go work on the task

To stop tracking: select the blank entry in the drop down

To restart tracking: select the entry from the drop down

To save to disk: select a different item from the drop down, or close the program (hit X), or Edit Tasks, or hit EoD (end of day)

To edit time assigned to a task (in seconds): hit the Edit button, edit, then Save

To delete a task: select it in the dropdown and hit the Delete key

To reset all task durations to zero: hit the Reset button

To stop tacking at the end of the day: hit the EoD button

To review tasks and time spent: hit the Export button

### Timesheets

Select Export to view summarized values in Excel. Insure Excel shows values to two decimal places (otherwise it may display rounded off values).

### Caveat

Saving happens often but not on a timer. For best results remember to hit EoD at end of day.