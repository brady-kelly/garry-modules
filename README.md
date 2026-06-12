## Working Setup

### Virtual Environments
Python offers [virtual environments](https://docs.python.org/3/library/venv.html) as a sort of light weight containerization for most of the system code needed to run a Python script, but unlike real containerization like with Docker, a virtual environment does not include application code. That is located next to the virtual environment in the project folder. This makes your project more portable, and avoids having to reconfigure your system code for all the varied needs ah projects.

Because these are like an interface between the installed Python on your system and the application code that uses it, it's better to keep these out of source control and create them fresh in whatever locations you work on application code. Follow these steps to create a virtual environment, or *venv*, in your working folder.

1. Open a terminal (unless explicitly otherwise, this means open a terminal inside VSCode.)
2. Create the venv:
   1. Enter the command `python -m venv .venv`
   2. Note that these are different words, the second one, that starts with a `.`, is the name of the folder to create, and the first one is the sub-command to create it.
   3. If VSCode shows a popup asking to select the new folder for the workspace, say yes.
3. Activate the venv:
   1. Enter the command `.\.venv\Scripts\Activate.ps1`
   2. This is a Powershell command, because that is the default terminal type for VSCode.
   3. You should now see the active venv folder name at the beginning of the command prompt.




