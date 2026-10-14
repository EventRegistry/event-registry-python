"""
Python SDK for Event Registry / NewsAPI.ai (https://newsapi.ai) - search and analyze news articles, events and mentions.

Typical use:

    from eventregistry import EventRegistry, QueryArticlesIter

    er = EventRegistry(apiKey = "YOUR_API_KEY")
    q = QueryArticlesIter(conceptUri = er.getConceptUri("Tesla"), lang = "eng")
    for article in q.execQuery(er, sortBy = "date", maxItems = 100):
        print(article["title"])

The main classes:

- `eventregistry.EventRegistry.EventRegistry` makes the requests and provides the suggest / lookup methods
- `eventregistry.QueryArticles`, `eventregistry.QueryEvents`, `eventregistry.QueryMentions`: searching for articles, events and mentions
- `eventregistry.QueryArticle`, `eventregistry.QueryEvent`: details about the individual articles and events
- `eventregistry.Query`: the advanced query language (`ComplexArticleQuery`, `BaseQuery`, `CombinedQuery`)
- `eventregistry.ReturnInfo`: which details the returned items should have
- `eventregistry.TopicPage`, `eventregistry.Recent`, `eventregistry.Trends`, `eventregistry.Counts`, `eventregistry.Analytics`
- `eventregistry.Exceptions`: the errors raised when a request fails

Guides and examples: https://github.com/EventRegistry/event-registry-python/wiki
"""
from eventregistry._version import __version__

from eventregistry.Base import *
from eventregistry.Exceptions import *
from eventregistry.EventForText import *
from eventregistry.ReturnInfo import *
from eventregistry.Query import *
from eventregistry.QueryEvents import *
from eventregistry.QueryEvent import *
from eventregistry.QueryArticles import *
from eventregistry.QueryArticle import *
from eventregistry.QueryMentions import *
from eventregistry.QueryStory import *
from eventregistry.Counts import *
from eventregistry.Info import *
from eventregistry.Recent import *
from eventregistry.Trends import *
from eventregistry.Analytics import *
from eventregistry.TopicPage import *
from eventregistry.EventRegistry import *
# importing the eventregistry.Query module replaced the Query class (from Base) in the package namespace - set it back
from eventregistry.Base import Query

import sys as _sys

# "from eventregistry import *" imports only the public classes, functions and constants of the modules (their __all__),
# not the modules that they import themselves (datetime, json, os, ...), which would overwrite the names in the user's code
__all__ = []
for _name in ("Base", "Exceptions", "EventForText", "ReturnInfo", "Query", "QueryEvents", "QueryEvent", "QueryArticles", "QueryArticle",
              "QueryMentions", "QueryStory", "Counts", "Info", "Recent", "Trends", "Analytics", "TopicPage", "EventRegistry"):
    __all__ += _sys.modules["eventregistry." + _name].__all__
del _name
