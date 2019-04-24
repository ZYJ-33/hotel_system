
import sys
from os.path import abspath
from os.path import dirname
import app
from functions import hotel_sys_thread
import _thread


sys.path.insert(0, abspath(dirname(__file__)))
thread = _thread.start_new_thread(hotel_sys_thread, ())
application = app.app
