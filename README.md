# Installation Process
# Step 1 - Navigation
Navigate to the directory that you want to install the `JARVIS` package into inside terminal, or your favorite code editor. Any terminal window should suffice.
## Mac
This can be done with commands like `ls` to list options, and `cd <foldername>` to enter a directory.
## Windows
Use the `dir` and `cd <foldername>` commands as needed

# Step 2 - GitHub Clone
Install git project to your local computer by running this command to download the `JARVIS` project:
``` Command Shell
git clone https://github.com/TheIronmaker/JARVIS.git
```

# Step 3 - Package Installation
You will need to download various packages to assist in the overall program. The required packages change depending on use-cases. You do not need to download and run MediaPipe (a large image processing library) if you do not plan on using a camera. It is a use-case based program, with a modular approach.

It is highly recommended to install the packages into a virtual environment, rather than directly into the computers main storage. Doing so could break python as it may interfere with system packages.

Since this project uses the MediaPipe library for image processing and tracking, it is required to use python 3.12. You can go to the python website and install python 3.12 onto your computer. The venv should be created with this version.

## Venv Creation:
Run this command to create the virtual environment folder on a Windows computer. *Note: You may rename the second "venv" to anything you like. It is just the name of the folder. __Keep the first venv there!__*
``` Command Shell
py -3.12 -m venv venv
```
Alternate version in case the first doesn't work:
```
python3.12 -m venv venv
```
Or maybe:
```
python3.12 -m venv venv
```

## Initialize venv
While inside of the folder containing the venv, initialize it with a command:
### Mac
```
source venv/bin/activate
```

### Windows
```
.\venv\Scripts\activate.bat
```
Or if using PowerShell:
```
.\venv\Scripts\activate.ps1
```

## Install Packages to venv
Once you have created the virtual environment, you can install the necessary packages. This project uses a `.toml` file, and the installation is very similar to a `requirements.txt` file. Run this command to install: *Note: Make sure to include the __period__ at the end.*
```
pip install -e .
```

### Main Program Startup
You should be able to run the main program at this point. Navigate to the core directory. This is found with:
```
cd src/jarvis/core
```
Run the `main.py` program with:
```
python -m main
```
# Finished!
Your program should be running at this point. If not, please review your installation process, and if there is a bug, submit a request and I will do my best to resolve any issues. Happy coding!