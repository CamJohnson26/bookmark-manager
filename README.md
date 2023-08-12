
# Usage
* Run the cli app
* Paste your new urls into ingest.txt
* Type bulk ingest in the cli
* In a terminal window, run `python3 cli_app.py`
* Type 'consume'. URLs will be consumed from ingest.txt and added to the database.
* Check in the input/history file to version control.
* If there were any errors, investigate and then run the retry commands

# Old notes
Install python dev tools: `sudo apt-get install python3-dev`
`sudo apt-get install build-essential`
sudo apt install python2-dev
sudo apt-get install libxml2-dev libxslt-dev

Ignore all the reqs and just use Python 3.9

Actually you can't, because of https://askubuntu.com/questions/1239829/modulenotfounderror-no-module-named-distutils-util
Going to try deleting requirements.txt and installing manually. I think part of the problem is some packages aren't compatible with 3.10, but I can't use 3.9 because of Debian.

geckodriver has a stupid install process. Download the release from mozilla github, sudo chmod +x it, and drop into /usr/local/bin.
Then venv isn't gonna pick it up because it's not in the path, so you have to move geckodriver manually into the venv bin folder
https://stackoverflow.com/questions/65318382/expected-browser-binary-location-but-unable-to-find-binary-in-default-location


pip freeze > requirements.txt How do I add a path to PYTHONPATH in virtualenv, Sometimes the trickiest part of setting up a virtual environment on Windows is finding your python distribution. If the installer didn't add it to your PATH variable,​  Then do any of the following steps: Create or modify an entry for python.pythonPath with the full path to the Python executable (if you edit settings.json Windows: "python.pythonPath": "c:/python36/python.exe", macOS/Linux: "python.pythonPath": "/home/python36/python", You can also use

You can add to the python path in the settings, view all interpreters, and then the little 'Paths' button but it's not doing anything

I don't get it, the pycharm /usr/bin folder in the paths selection has different content than ls in terminal.
Maybe pycharm needs sudo permissions. Forget it this is too much trouble.

Pyppeteer also is crashing, won't work with the installed version.

Ok I'm pretty sure it's because I was running PyCharm through flatpak. Use the jetbrains toolbox instead.

