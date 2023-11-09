j
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
// command adapter from here: https://stackoverflow.com/questions/35841969/python-portable-pyinstaller
python -m nuitka --standalone --remove-output --windows-disable-console main.py
```

In the main.dist output folder copy the `notes_colors.json` file and the `wav` and `midi` folders.