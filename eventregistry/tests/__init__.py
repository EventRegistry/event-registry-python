import unittest
from .DataValidator import *
from .TestAnalytics import *
from .TestAutoSuggestions import *
from .TestInfo import *
from .TestInvalidQueries import *
from .TestQueryArticle import *
from .TestQueryArticles import *
from .TestQueryArticlesComplex import *
from .TestQueryEvent import *
from .TestQueryEvents import *
from .TestQueryEventsComplex import *


def runTests():
    unittest.main();
