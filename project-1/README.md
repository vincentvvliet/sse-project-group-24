# Running the experiment on Windows

1. Make sure you DON'T already have a version of python 3.11 or python 3.14 already installed. Installation will quietly fail, and I haven't figured out how to make the script find python versions yet. If you do have either of them installed, uninstall them via Apps & features.
2. Open powershell with administrator privileges.
3. Navigate to the folder containing the script and run it with ".\experiment.ps1"

It should then install both versions of python, install energibridge, install requirements.txt, and then run the python code with the experiment.