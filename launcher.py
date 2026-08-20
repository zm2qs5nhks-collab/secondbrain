import sys, os
os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(__file__))

import webbrowser
from threading import Timer
Timer(4, lambda: webbrowser.open("http://localhost:8501")).start()

from streamlit.web import cli
sys.argv = ["streamlit", "run", "app.py"]
try:
    cli.main()
except SystemExit:
    pass
