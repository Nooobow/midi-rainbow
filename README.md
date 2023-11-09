NOTE: Application requires midi/wav folders not included in this repository.

To run the application with Python (v3.11.6 was used), run the following commands:

```
python -m venv .venv
.venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

Then run the application from main.py:

```
python main.py
```

To build standalone version of the program run the following:
```
// command adapted from here: https://stackoverflow.com/questions/35841969/python-portable-pyinstaller
python -m nuitka --standalone --remove-output --windows-disable-console main.py
```
Copy the `note_colors.json` file and the `wav` and `midi` folders into the `main.dist` output folder created by the build command.

You should now be able to run the exe from that folder.