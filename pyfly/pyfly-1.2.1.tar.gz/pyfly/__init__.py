from .core import task, TaskDataQueue, TaskSet, FlyQueen, async_task, sleep
from .runners import FlyMaster, FlySlave
from .events import task_success, task_fail 
import traceback
try:
    from .web import WebApp
except:
    print(traceback.format_exc())
    print("You should to install dash, if you want to run master on this pc!")

__version__ = "1.2.1"