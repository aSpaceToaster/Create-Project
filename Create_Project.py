#Author: Hannes Aubrecht (They/Them)
#Version: 1.1.1.1

from tkinter import *
from tkinter import ttk
import os
import platform

# SETUP ###########################################################################################

# Define constants
FILE_EXT = ".txt"
TASK_STATE_OPTIONS = [ "C  - Complete", "IP - In Progress", "TD - To Do" ]
SYSTEM = platform.system()
IS_PI = platform.platform().count( "rpi" ) >= 1

# Determine os, Define file locations
if( SYSTEM == "Windows" ):
	PROJECT_DIRECTORY = "C:\\Users\\Space Toaster\\Documents\\Projects"
	if( not os.path.isdir( PROJECT_DIRECTORY ) ):
		PROJECT_DIRECTORY = "Projects"
		if( not os.path.isdir( PROJECT_DIRECTORY ) ):
			os.mkdir( PROJECT_DIRECTORY )
	PROJECT_DIRECTORY += "\\"
elif( SYSTEM == "Darwin" ):
	PROJECT_DIRECTORY = "/Users/SpaceToaster/Documents/Projects"
	if( not os.path.isdir( PROJECT_DIRECTORY ) ):
		PROJECT_DIRECTORY = "Projects"
		if( not os.path.isdir( PROJECT_DIRECTORY ) ):
			os.mkdir( PROJECT_DIRECTORY )
	PROJECT_DIRECTORY += "/"
elif( SYSTEM == "Linux" ):
	PROJECT_DIRECTORY = "/home/user/space-toaster/projects"
	if( not os.path.isdir( PROJECT_DIRECTORY ) ):
		PROJECT_DIRECTORY = "projects"
		if( not os.path.isdir( PROJECT_DIRECTORY ) ):
			os.mkdir( PROJECT_DIRECTORY )
	PROJECT_DIRECTORY += "/"
else:
	print( "Please run this code on windows, mac os, or linux")
	quit()

# Setup for raspberry pi
if( IS_PI	):
	try:
		from gpiozero import *
		testPinOut = LED( 20 )
		testPinIn = digitalInputDevice( 21 )
		testPinOut.on()
		if( not testPinIn.value ):
			IS_PI = False
		testPinOut.off()
	except Exception as e:
		IS_PI = False


# Init vars
tasks = []
taskStates = []
materials = []
materialQtys = []
projects = []
projectNames = []
title = []
state = []
currTask = ""



# FUNCTIONS ####################################################################################### 

# PROJECTS ----------------------------------------------------------------------------------------

# Reads project names from folder
def readProjects():
  # Find folder contents
	projectFolder = os.listdir( PROJECT_DIRECTORY )
	
	# Remove non-.txt files from list
	for project in projectFolder:
		if project.count( FILE_EXT ) == 0:
			projectFolder.remove( project )
  
  # Update variables and GUI
	projects = projectFolder
	projectNames.clear()
	for project in projects:
		projectNames.append( project[ 0 : project.index( ".txt" ) ] )

# Read the information stored in a project file, store it in lists
def interpretFile( filename ):
	try:
		# Clear vars
		state.clear()
		title.clear()
		tasks.clear()
		taskStates.clear()
		materials.clear()
		materialQtys.clear()

		# Read file contents
		contents = open( filename ).read()
		state.append( contents.splitlines()[ 1 ] )
		title.append( contents[ contents.index( 'NAME' ) + 6 : contents.index( 'TASKS' ) - 2 ] )
		taskSect = contents[ contents.index( 'TASKS' ) + 7 : contents.index( 'MATERIALS' ) - 2].splitlines()
		materialSect = contents[ contents.index( 'MATERIALS' ) + 11 : len( contents ) ].splitlines()

		# Parse tasks and task states
		if taskSect:
			for line in taskSect:
				tasks.append( line[ 0 : line.index( ' - ' ) ] )
				taskStates.append( line[ line.index( ' - ' ) + 3 : len( line ) ] )

		# Parse materials and material quantities
		if materialSect:
			for line in materialSect:
				materials.append( line[ 0 : line.index( ' - ' ) ] )
				materialQtys.append( line[ line.index( ' - ' ) + 3 : len( line ) ] )

		# Save state and title to StringVars
		if state and title:
			projState.set( state[ 0 ] )
			projTitle.set( title[ 0 ] )

	except OSError as e:
		# Thrown if selected file is not found
		print( "File not found exception: " + str(e) )
	except ValueError:
		# Thrown if selected file does not contain project file formatting
		print( "File not a project file" )
	except Exception as e:
		# Catch-all error case
		print( e )

# updates vars and GUI on project select
def selectProject():
  # Select and read file
	projectName = currentProject.get()
	interpretFile( PROJECT_DIRECTORY + projectName + FILE_EXT )
	currProj.config( text="Editing: " + projectName )
	
	# set materials
	for item in materialList.get_children():
		materialList.delete( item )
	for material, qty in zip( materials, materialQtys ):
		materialList.insert( "", "end", values=( material, qty ) )
  
	# set tasks
	for item in taskList.get_children():
		taskList.delete( item )
	for task, state in zip( tasks, taskStates ):
		taskList.insert( "", "end", values=( task, state ) )

# creates a new project file
def newProject():
	# Create input GUI
	inputWindow = Toplevel( root )
	inputWindow.geometry( "300x200" )
	inputWindow.title( "New Project" )
	inputWindow.transient( root )
	inputWindow.grab_set()
	inputWindow.focus_force()
	ttk.Label( inputWindow, text="Project Name" ).pack()
	ttk.Label( inputWindow, text="Must be a valid file name" ).pack()
	ttk.Entry( inputWindow, textvariable=projName ).pack()
	
	# Saves new project
	def saveProj():
		# create and set up new project file
		file = open( PROJECT_DIRECTORY + projName.get() + ".txt", mode="x" )
		file.write( "STATE:\nTD\n\n" )
		file.write( "NAME:\n" + projName.get() + "\n\n" )
		file.write( "TASKS:\n\n" )
		file.write( "MATERIALS:" )
		file.close()

		# Selects new project
		readProjects()
		dropdown.set_menu( projectNames[0], *projectNames )
		currentProject.set( projName.get() )
		selectProject()
		inputWindow.destroy()
	ttk.Button( inputWindow, text="Save", command=saveProj ).pack()

# Saves edited project to file
def save():
	# Open file to write to
	file = open( PROJECT_DIRECTORY + currentProject.get() + ".txt", mode="w" )
	
	# Write project name and state
	file.write( "STATE:\n" + projState.get() + "\n\n" )
	file.write( "NAME:\n" + projTitle.get() + "\n\n" )
	
	# Write tasks
	file.write( "TASKS:\n " )
	for task, state in zip( tasks, taskStates ):
		file.write( task + " - " + state + "\n" )
	
	# Write materials
	file.write( "\nMATERIALS:\n" )
	for material, qty in zip( materials, materialQtys ):
		file.write( material + " - " + qty + "\n" )
	
	# Close file
	file.close()

# Removes a project
def deleteProject():
  # Create input GUI
	inputWindow = Toplevel( root )
	inputWindow.transient( root )
	inputWindow.grab_set()
	inputWindow.focus_force()
	ttk.Label( inputWindow, text="Delete this project?" ).pack()
	
	# Delete project, clear GUI
	def deleteProjectForRealz():
		filePath = PROJECT_DIRECTORY + currentProject.get() + ".txt"
		if os.path.exists( filePath ):
			os.remove( filePath )
		projectNames.pop( projectNames.index( currentProject.get() ) )
		if( projectNames ):
			dropdown.set_menu( projectNames[0], *projectNames )
		else:
			dropdown.set_menu( "-----", *projectNames )
		currProj.config( text="Editing: -----" )
		for item in materialList.get_children():
			materialList.delete( item )
		for item in taskList.get_children():
			taskList.delete( item )
		inputWindow.destroy()

	# Cancel project deletion
	def cancel():
		inputWindow.destroy()

	ttk.Button( inputWindow, text="Yes", command=deleteProjectForRealz ).pack()
	ttk.Button( inputWindow, text="No", command=cancel ).pack()

# change a project state
def editProject():
  # Create input GUI
	inputWindow = Toplevel( root )
	newState = StringVar( root )
	inputWindow.geometry( "300x200" )
	inputWindow.title( "Change Project State" )
	inputWindow.transient( root )
	inputWindow.grab_set()
	inputWindow.focus_force()
	stateFrame = ttk.Frame( inputWindow )
	stateFrame.pack()
	ttk.Label( stateFrame, text="New State:" ).pack( side="left" )
	ttk.OptionMenu( stateFrame, newState, TASK_STATE_OPTIONS[ 0 ], *TASK_STATE_OPTIONS ).pack( side="left" )
	
	# Save project state
	def save():
		projState.set( newState.get()[ 0:2 ] )
		projectState.config( text="\tProject State: " + projState.get() )
		inputWindow.destroy()
	ttk.Button( inputWindow, text="Save", command=save ).pack()

# TASKS -------------------------------------------------------------------------------------------

# Adds a task to the list
def addTask():
  # Create input GUI
	inputWindow = Toplevel( root )
	inputWindow.geometry( "300x200" )
	inputWindow.title( "Add a Task" )
	inputWindow.transient( root )
	inputWindow.grab_set()
	inputWindow.focus_force()
	nameFrame = ttk.Frame( inputWindow )
	nameFrame.pack()
	ttk.Label( nameFrame, text="Task Name:" ).pack( side="left" )
	ttk.Entry( nameFrame, textvariable=task ).pack( side="left" )
	
	# Save new task
	def saveTask():
		tasks.append( task.get() )
		taskStates.append( "TD" )
		taskList.insert( "", "end", values=( task.get(), "TD" ) )
		inputWindow.destroy()
	ttk.Button( inputWindow, text="Save", command=saveTask ).pack()

# Removes a task from the list
def removeTask():
	selected = taskList.selection()
	if selected:
		idx = taskList.index( selected[0] )
		tasks.pop( idx )
		taskStates.pop( idx )
		taskList.delete( taskList.get_children()[ idx ] )

# Changes a task state
def editTask():
	if taskList.selection():
		# Create input GUI
		currState.set( "TD" )
		inputWindow = Toplevel( root )
		inputWindow.geometry( "300x200" )
		inputWindow.minsize( width=300, height=200 )
		inputWindow.title( "Editing Task State" )
		inputWindow.transient( root )
		inputWindow.grab_set()
		inputWindow.focus_force()
		stateFrame = ttk.Frame( inputWindow )
		stateFrame.pack()
		ttk.Label( stateFrame, text="Task State:" ).pack( side="left" )
		ttk.OptionMenu( stateFrame, currState, TASK_STATE_OPTIONS[0], *TASK_STATE_OPTIONS ).pack( side="left" )

		# Save task state
		def save():
			taskStates[ taskList.index( taskList.selection()[0] ) ] = currState.get()[ 0:2 ]
			taskList.set( taskList.selection(), "State", value=currState.get()[ 0:2 ] )
			inputWindow.destroy()
		ttk.Button( inputWindow, text="Save", command=save ).pack()

# MATERIALS ---------------------------------------------------------------------------------------

# Adds a material and its corresponding quantity
def	addMaterial():
  # Create input GUI
	inputWindow = Toplevel( root )
	inputWindow.geometry( "300x200" )
	inputWindow.title( "Add a Material" )
	inputWindow.transient( root )
	inputWindow.grab_set()
	inputWindow.focus_force()
	matInFrame = ttk.Frame( inputWindow )
	matInFrame.pack()
	qtyInFrame = ttk.Frame( inputWindow )
	qtyInFrame.pack()
	ttk.Label( matInFrame, text="Material:" ).pack( side="left" )
	ttk.Entry( matInFrame, textvariable=material ).pack( side="left" )
	ttk.Label( qtyInFrame, text="Quantity:" ).pack( side="left" )
	ttk.Entry( qtyInFrame, textvariable=currQty ).pack( side="left" )
	ttk.Label( inputWindow, text="Qty: num/weight/\"-1\" for NA/\"-2\" for undetermined" ).pack()
	
	# Save material and quantity
	def save():
		materials.append( material.get() )
		materialQtys.append( currQty.get() )
		materialList.insert( "", "end", values=( material.get(), currQty.get() ) )
		inputWindow.destroy()
	ttk.Button( inputWindow, text="Save", command=save ).pack()

# Removes a material from the list
def removeMaterial():
	selected = materialList.selection()
	if selected:
		idx = materialList.index( selected[0] )
		materials.pop( idx )
		materialQtys.pop( idx )
		materialList.delete( materialList.get_children()[ idx ] )

# Edit a material quantity
def editMaterial():
	if materialList.selection():
		# Create input GUI
		currQty.set( materialQtys[ materialList.index( materialList.selection()[0] ) ] )
		inputWindow = Toplevel( root )
		inputWindow.geometry( "300x200" )
		inputWindow.title( "Editing Material Quantity" )
		inputWindow.transient( root )
		inputWindow.grab_set()
		inputWindow.focus_force()
		qtyInFrame = ttk.Frame( inputWindow )
		qtyInFrame.pack()
		ttk.Label( qtyInFrame, text="New Quantity: " ).pack( side="left" )
		ttk.Entry( qtyInFrame, textvariable=currQty).pack( side="left" )
		ttk.Label( inputWindow, text="Qty: num/weight/\"-1\" for NA/\"-2\" for undetermined" ).pack()

		# Save material quantity
		def save():
			materialQtys[ materialList.index( materialList.selection()[0] ) ] =	currQty.get()
			materialList.set( materialList.selection()[0], "Quantity", value= currQty.get() )
			inputWindow.destroy()
		ttk.Button( inputWindow, text="Save", command=save ).pack()


# MAIN CODE #######################################################################################

# Read project filenames
readProjects()


# Create GUI window, change theme based on OS
root = Tk()
root.geometry( "650x450" )
root.minsize( width=550, height=350 )
root.title( "Project Tracker" )
style = ttk.Style( root )
if( SYSTEM == "Windows" ):
	style.theme_use( 'vista' )
elif( SYSTEM == "Darwin" ):
	style.theme_use( 'aqua' )
else:
	style.theme_use( 'alt' )
mainFrame = ttk.Frame( root )
mainFrame.pack( fill="both", expand=True )


# Init GUI StringVars
currentProject = StringVar( root )
if( projectNames ):
	currentProject.set( projectNames[0] )
else:
	currentProject.set( "-----" )
task = StringVar( root )
currState = StringVar( root )
material = StringVar( root )
currQty = StringVar( root )
projName = StringVar( root )
projState = StringVar( root )
projTitle = StringVar( root )


# Project tools
projToolFrame = ttk.Frame( mainFrame )
projToolFrame.pack()
projSelectFrame = ttk.Frame( projToolFrame )
projSelectFrame.pack()
projButtonFrame = ttk.Frame( projToolFrame )
projButtonFrame.pack()
projInfoFrame = ttk.Frame( projToolFrame )
projInfoFrame.pack()

# Select, New
dropdown = ttk.OptionMenu( projSelectFrame, currentProject, currentProject.get(), *projectNames )
dropdown.pack( side="left", expand=True )
select = ttk.Button( projSelectFrame, text="Select Project", command=selectProject )
select.pack( side="left", expand=True )
newProj = ttk.Button( projSelectFrame, text="New Project", command=newProject )
newProj.pack( side="left", expand=True )

# Project control
edtProject = ttk.Button( projButtonFrame, text="Change State", command=editProject )
edtProject.pack( side="left", expand=True )
saveProj = ttk.Button( projButtonFrame, text="Save", command=save )
saveProj.pack( side="left", expand=True )
delProj = ttk.Button( projButtonFrame, text="Delete Project", command=deleteProject )
delProj.pack( side="left", expand=True )
quitBtn = ttk.Button( projButtonFrame, text="Quit Editor", command=quit )
quitBtn.pack( side="left", expand=True )

# Current project info
currProj = ttk.Label( projInfoFrame, text="Editing: -----" )
currProj.pack( side="left" )
projectState = ttk.Label( projInfoFrame, text="\tProject State: --" )
projectState.pack( side="right" )


# Material and material quantity display
materialFrame = ttk.Frame( mainFrame )
materialFrame.pack( side="left", fill="both", expand=True, padx=10, pady=10 )
materialListFrame = ttk.Frame( materialFrame )
materialListFrame.pack( fill="both", expand=True )
materialList = ttk.Treeview( materialListFrame, columns=( "Material", "Quantity" ), show="headings" )
materialList.heading( "Material", text="Material" )
materialList.heading( "Quantity", text="Quantity" )
materialList.column( "Material", width=150 )
materialList.column( "Quantity", width=80, anchor="center" )
for material, qty in zip( materials, materialQtys ):
	materialList.insert( "", "end", values=( material, qty ) )
materialScrollbar = ttk.Scrollbar( materialListFrame, orient="vertical", command=materialList.yview )
materialList.configure( yscroll=materialScrollbar.set )
materialScrollbar.pack( side="right", fill="y" )
materialList.pack( fill="both", expand=True )

# Material control buttons
materialButtonFrame = ttk.Frame( materialFrame )
materialButtonFrame.pack()
newMaterial = ttk.Button( materialButtonFrame, text="Add Material", command=addMaterial )
newMaterial.pack( side="left", expand=True )
delMaterial = ttk.Button( materialButtonFrame, text="Remove Material", command=removeMaterial )
delMaterial.pack( side="left", expand=True )
edtMaterial = ttk.Button( materialButtonFrame, text="Edit Quantity", command=editMaterial )
edtMaterial.pack( side="left", expand=True )


# Task list
taskFrame = ttk.Frame( mainFrame )
taskFrame.pack( side="left", fill="both", expand=True, padx=10, pady=10 )
taskListFrame = ttk.Frame( taskFrame )
taskListFrame.pack( fill="both", expand=True )
taskList = ttk.Treeview( taskListFrame, columns=( "Task", "State" ), show="headings" )
taskList.heading( "Task", text="Task" )
taskList.heading( "State", text="State" )
taskList.column( "Task", width=150 )
taskList.column( "State", width= 80, anchor="center" )
for task, state in zip( tasks, taskStates ):
	taskList.insert( "", "end", values=( task, state ) )
taskScrollbar = ttk.Scrollbar( taskListFrame, orient="vertical", command=taskList.yview )
taskList.configure( yscroll=taskScrollbar.set )
taskScrollbar.pack( side="right", fill="y" )
taskList.pack( fill="both", expand=True )

# Task control buttons
taskButtonFrame = ttk.Frame( taskFrame )
taskButtonFrame.pack()
newTask = ttk.Button( taskButtonFrame, text="Add Task", command=addTask )
newTask.pack( side="left" )
delTask = ttk.Button( taskButtonFrame, text="Remove Task", command=removeTask )
delTask.pack( side="left" )
edtTask = ttk.Button( taskButtonFrame, text="Edit Task", command=editTask)
edtTask.pack(	side="left" )


# Keep GUI running until closed or quit button is pressed
root.mainloop()