# GLFC-GUI
A GUI for the Great Lakes Fisheries Commission data carriage fabricated by SAFL and delivered in Fall/Winter 2026.


## Installation
- Download and install the [latest version of Python 3](https://www.python.org/downloads/). Make sure to check the "Add to Path" checkbox during installation. This just makes it easier to use Python on Windows because you can use any terminal (command prompt, PowerShell, etc.)
- Fork or Clone the [GLFC-GUI repo](https://github.com/SAFL-Engineering/GLFC-GUI) to a directory on your computer 
- Open your favorite terminal and change directory so you are in the directory where you just cloned/forked the Github repo
- Install all the required Python packages/libraries using the command: `pip install -r requirements.txt`
- You will need to create a `credentials.py` file that contains the IP address and port number for your MQTT broker and a username/password for your GUI. There is an example credential file located in the repo called `example_credentials.py`. Make a copy of this file and rename it `credentials.py`.  Update the fields with the details for your MQTT broker and set a username and password. 
- After all the packages have finished installing you are ready to start the GUI/HMI!
- Launch the GUI using the command `python GLFC_GUI_v0.py`
- To view the GUI open your browser and navigate to: http://127.0.0.1:8050/

