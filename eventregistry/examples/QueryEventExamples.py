"""
examples that show how to obtain information about an individual event
"""
from eventregistry import *

er = EventRegistry()

# iterate over all articles that belong to a particular event with a given URI
# limit to only articles in English language
iter = QueryEventArticlesIter("eng-2940883")
for art in iter.execQuery(er, lang = "eng"):
    print art

# get event info about event with a particular uri
q = QueryEvent("eng-88")
q.setRequestedResult(RequestEventInfo(
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(lang = ["eng", "spa", "slv"]))))
eventRes = er.execQuery(q)

# get list of 10 articles about the event
q.setRequestedResult(RequestEventArticles(page = 1, count = 10))        # get 10 articles about the event (any language is ok) that are closest to the center of the event
eventRes = er.execQuery(q)

# get information about how reporting about the event was trending over time
q.setRequestedResult(RequestEventArticleTrend())
eventRes = er.execQuery(q)

# get the tag cloud of top words for the event
q.setRequestedResult(RequestEventKeywordAggr())
eventRes = er.execQuery(q)

# obtain in one call information about two events with given uris
q = QueryEvent(["spa-32", "spa-45"])
q.setRequestedResult(RequestEventArticles(page =1, count = 200))
res = er.execQuery(q)


