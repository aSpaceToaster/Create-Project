Author: Hannes Aubrecht
Version: 1.1
Title: Project Manager

IMPORTANT:
	This code will not run with a virtual machine, such as Google colab.
	In order to run this code, you will need to hava a python capable IDE, such as VSCode, or run it via the command line.
	To run this code with VSCode, install VSCode, then in VSCode, install python support, then right click the code file, and select open with -> VSCode.
	To run this code via command line, first install python 3.13 (https://www.python.org/downloads/release/python-31312/),
	then right click the file and select open with -> python 3.13

	The reason this code will not work on a virtual machine is that it needs access to a file system.
	This code will be able to create files on your machine, and also delete any files it creates.
	The first time this program runs, it will create the directory Projects,
	which will be located in the folder you run this code in. 
	It will only access files in this folder, although it will check if a few directories are present.
	if you have the following directory that corresponds to your OS, the code will run in that directory instead:
	C:\Users\Space Toaster\Documents\Projects (Windows)
	/Users/SpaceToaster/Documents/Projects		(MacOS)
	/home/user/space-toaster/projects					(Linux)


Test case:
Run code --------------------------------------------------- Opens main GUI
Use "Create Project" button                                  Opens popup GUI
Enter a project name in provided box, use "Save" button ---- Creates a new project file, updates main GUI, closes popup GUI
Select project from dropdown, use "Select Project" button    Reads project file, updates GUI
Use "Edit State" button ------------------------------------ Opens popup GUI
Select "IP" from dropdown, Save                              Changes project state to in progress, updates GUI
Use "Add Task" button -------------------------------------- Opens popup GUI
Enter task name, use "Save" button                           Adds new task to task list with a state of "TD", updates GUI
Select task in list, use "Edit Task" button ---------------- Opens popup GUI
Select "IP" from dropdown, Save                              Changes task state to in progress, updates GUI
Use "Save" button ------------------------------------------ Saves changes
Use "Quit Editor" button                                     Stops program
Rerun code, play around with it, try things.

To attempt to break this code:
	follow input guidelines given in GUI
	all inputs must be valid strings in python