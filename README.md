geckodriver has a stupid install process. Download the release from mozilla github, sudo chmod +x it, and drop into /usr/local/bin.
Then venv isn't gonna pick it up because it's not in the path, so you have to move geckodriver manually into the venv bin folder
https://stackoverflow.com/questions/65318382/expected-browser-binary-location-but-unable-to-find-binary-in-default-location


pip freeze > requirements.txtHow do I add a path to PYTHONPATH in virtualenv, Sometimes the trickiest part of setting up a virtual environment on Windows is finding your python distribution. If the installer didn't add it to your PATH variable,​  Then do any of the following steps: Create or modify an entry for python.pythonPath with the full path to the Python executable (if you edit settings.json Windows: "python.pythonPath": "c:/python36/python.exe", macOS/Linux: "python.pythonPath": "/home/python36/python", You can also use

You can add to the python path in the settings, view all interpreters, and then the little 'Paths' button but it's not doing anything

I don't get it, the pycharm /usr/bin folder in the paths selection has different content than ls in terminal.
Maybe pycharm needs sudo permissions. Forget it this is too much trouble.

Pyppeteer also is crashing, won't work with the installed version.

Ok I'm pretty sure it's because I was running PyCharm through flatpak. Use the jetbrains toolbox instead.

