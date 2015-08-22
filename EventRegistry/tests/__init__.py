def Assert(condition, msg):
    if not condition:
        print msg

from .QueryEvents import *
from .QueryArticles import *
from .AutoSuggestions import *