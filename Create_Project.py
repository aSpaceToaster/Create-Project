#Author: Hannes Aubrecht
#Version: 1.2

from tkinter import *
from tkinter import ttk
import os
from time import *
import platform


# define constants
FILE_EXT = ".txt"
TASK_STATE_OPTIONS = [ "C  - Complete", "IP - In Progress", "TD - To Do" ]
SYSTEM = platform.system()
IS_PI = platform.platform().count( "rpi" ) >= 1

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
	



# init vars
tasks = []
taskStates = []
materials = []
materialQtys = []
projects = []
projectNames = []
title = []
state = []
currTask = ""

# reads project names from folder
def readProjects():
	projectFolder = os.listdir( PROJECT_DIRECTORY )
	for project in projectFolder:
		if project.count( FILE_EXT ) == 0:
			projectFolder.remove( project )
	projects = projectFolder
	projectNames.clear()
	for project in projects:
		projectNames.append( project[ 0 : project.index( ".txt" ) ] )

# read the information stored in a project file, store it in lists
def interpretFile( filename ):
	try:
		# clear vars
		state.clear()
		title.clear()
		tasks.clear()
		taskStates.clear()
		materials.clear()
		materialQtys.clear()

		# read file contents
		contents = open( filename ).read()
		state.append( contents.splitlines()[ 1 ] )
		title.append( contents[ contents.index( 'NAME' ) + 6 : contents.index( 'TASKS' ) - 2 ] )
		taskSect = contents[ contents.index( 'TASKS' ) + 7 : contents.index( 'MATERIALS' ) - 2].splitlines()
		materialSect = contents[ contents.index( 'MATERIALS' ) + 11 : len( contents ) ].splitlines()

		# parse tasks and task states
		if taskSect:
			for line in taskSect:
				tasks.append( line[ 0 : line.index( ' - ' ) ] )
				taskStates.append( line[ line.index( ' - ' ) + 3 : len( line ) ] )

		# parse materials and material quantities
		if materialSect:
			for line in materialSect:
				materials.append( line[ 0 : line.index( ' - ' ) ] )
				materialQtys.append( line[ line.index( ' - ' ) + 3 : len( line ) ] )

		if state and title:
			projState.set( state[ 0 ] )
			projTitle.set( title[ 0 ] )

	except OSError as e:
		print( "File not found exception: " + str(e) )
	except ValueError:
		print( "File not a project file" )
	except Exception as e:
		print( e )

# updates vars and GUI on project select
def selectProject():
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
	inputWindow = Toplevel( root )
	inputWindow.geometry( "300x200" )
	inputWindow.title( "New Project" )
	inputWindow.transient( root )
	inputWindow.grab_set()
	inputWindow.focus_force()
	ttk.Label( inputWindow, text="Project Name" ).pack()
	ttk.Label( inputWindow, text="Must be a valid file name" ).pack()
	ttk.Entry( inputWindow, textvariable=projName ).pack()
	def saveProj():
		# create and set up new project file
		file = open( PROJECT_DIRECTORY + projName.get() + ".txt", mode="x" )
		file.write( "STATE:\nTD\n\n" )
		file.write( "NAME:\n" + projName.get() + "\n\n" )
		file.write( "TASKS:\n\n" )
		file.write( "MATERIALS:" )
		file.close()

		readProjects()
		dropdown.set_menu( projectNames[0], *projectNames )
		currentProject.set( projName.get() )
		selectProject()
		inputWindow.destroy()
	ttk.Button( inputWindow, text="Save", command=saveProj ).pack()

# saves edited project to file
def save():
	# open file
	file = open( PROJECT_DIRECTORY + currentProject.get() + ".txt", mode="w" )

	# project name and state
	file.write( "STATE:\n" + projState.get() + "\n\n" )
	file.write( "NAME:\n" + projTitle.get() + "\n\n" )

	# tasks
	file.write( "TASKS:\n " )
	for task, state in zip( tasks, taskStates ):
		file.write( task + " - " + state + "\n" )

	# materials
	file.write( "\nMATERIALS:\n" )
	for material, qty in zip( materials, materialQtys ):
		file.write( material + " - " + qty + "\n" )

	file.close()

# removes a project
def deleteProject():
	inputWindow = Toplevel( root )
	inputWindow.transient( root )
	inputWindow.grab_set()
	inputWindow.focus_force()
	ttk.Label( inputWindow, text="Delete this project?" ).pack()

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

	def cancel():
		inputWindow.destroy()

	ttk.Button( inputWindow, text="Yes", command=deleteProjectForRealz ).pack()
	ttk.Button( inputWindow, text="No", command=cancel ).pack()

# adds a task to the list
def addTask():
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
	def saveTask():
		tasks.append( task.get() )
		taskStates.append( "TD" )
		taskList.insert( "", "end", values=( task.get(), "TD" ) )
		inputWindow.destroy()
	ttk.Button( inputWindow, text="Save", command=saveTask ).pack()

#removes a task from the list
def removeTask():
	selected = taskList.selection()
	if selected:
		idx = taskList.index( selected[0] )
		tasks.pop( idx )
		taskStates.pop( idx )
		taskList.delete( taskList.get_children()[ idx ] )

# changes a task state
def editTask():
	if taskList.selection():
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
		def save():
			taskStates[ taskList.index( taskList.selection()[0] ) ] = currState.get()[ 0:2 ]
			taskList.set( taskList.selection(), "State", value=currState.get()[ 0:2 ] )
			inputWindow.destroy()
		ttk.Button( inputWindow, text="Save", command=save ).pack()

# adds a material and its corresponding quantity
def	addMaterial():
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
	def save():
		materials.append( material.get() )
		materialQtys.append( currQty.get() )
		materialList.insert( "", "end", values=( material.get(), currQty.get() ) )
		inputWindow.destroy()
	ttk.Button( inputWindow, text="Save", command=save ).pack()

# removes a material from the list
def removeMaterial():
	selected = materialList.selection()
	if selected:
		idx = materialList.index( selected[0] )
		materials.pop( idx )
		materialQtys.pop( idx )
		materialList.delete( materialList.get_children()[ idx ] )

# edit a material quantity
def editMaterial():
	if materialList.selection():
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
		def save():
			materialQtys[ materialList.index( materialList.selection()[0] ) ] =	currQty.get()
			materialList.set( materialList.selection()[0], "Quantity", value= currQty.get() )
			inputWindow.destroy()
		ttk.Button( inputWindow, text="Save", command=save ).pack()


# read project filenames
readProjects()


# Create GUI window
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


# Project selection tools
projToolFrame = ttk.Frame( mainFrame )
projToolFrame.pack()
projSelectFrame = ttk.Frame( projToolFrame )
projSelectFrame.pack()
projButtonFrame = ttk.Frame( projToolFrame )
projButtonFrame.pack()
dropdown = ttk.OptionMenu( projSelectFrame, currentProject, currentProject.get(), *projectNames )
dropdown.pack( side="left", expand=True )
select = ttk.Button( projSelectFrame, text="Select Project", command=selectProject )
select.pack( side="left", expand=True )
newProj = ttk.Button( projButtonFrame, text="New Project", command=newProject )
newProj.pack( side="left", expand=True )
saveProj = ttk.Button( projButtonFrame, text="Save", command=save )
saveProj.pack( side="left", expand=True )
delProj = ttk.Button( projButtonFrame, text="Delete Project", command=deleteProject )
delProj.pack(side="left", expand=True )
quitBtn = ttk.Button( projButtonFrame, text="Quit Editor", command=quit)
quitBtn.pack( side="left", expand=True )
currProj = ttk.Label( projToolFrame, text="Editing: -----" )
currProj.pack()


# material and material quantity display
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

materialButtonFrame = ttk.Frame( materialFrame )
materialButtonFrame.pack()
newMaterial = ttk.Button( materialButtonFrame, text="Add Material", command=addMaterial )
newMaterial.pack( side="left", expand=True )
delMaterial = ttk.Button( materialButtonFrame, text="Remove Material", command=removeMaterial )
delMaterial.pack( side="left", expand=True )
edtMaterial = ttk.Button( materialButtonFrame, text="Edit Quantity", command=editMaterial )
edtMaterial.pack( side="left", expand=True )


# Task list and task editing buttons
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

taskButtonFrame = ttk.Frame( taskFrame )
taskButtonFrame.pack()
newTask = ttk.Button( taskButtonFrame, text="Add Task", command=addTask )
newTask.pack( side="left" )
delTask = ttk.Button( taskButtonFrame, text="Remove Task", command=removeTask )
delTask.pack( side="left" )
edtTask = ttk.Button( taskButtonFrame, text="Edit Task", command=editTask)
edtTask.pack(	side="left" )

root.mainloop()