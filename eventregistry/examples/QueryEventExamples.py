"""
examples that show how to obtain information about an individual event
"""
from eventregistry import *

er = EventRegistry()

#
# NOTE: if you don't have access to historical data, you have to change the event URI
# to some recent event that you can access in order to run the example
#

eventUri = "eng-2940883"

# iterate over all articles that belong to a particular event with a given URI
iter = QueryEventArticlesIter(eventUri)
for art in iter.execQuery(er):
    print(art)

# iterate over the articles in the event, but only return those that mention Obama in the title
iter = QueryEventArticlesIter(eventUri,
    keywords = "Obama",
    keywordsLoc = "title")
for art in iter.execQuery(er):
    print(art)


# iterate over the articles in the event, but only select those that are in English or German language
iter = QueryEventArticlesIter(eventUri,
    lang = ["eng", "deu"])
for art in iter.execQuery(er):
    print(art)


# iterate over the articles in the event, but only select those that are from sources located in United States
iter = QueryEventArticlesIter(eventUri,
    sourceLocationUri = er.getLocationUri("United States"))
for art in iter.execQuery(er):
    print(art)


# get event info (title, summary, concepts, location, date, ...) about event with a particular uri
q = QueryEvent(eventUri)
q.setRequestedResult(RequestEventInfo(
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(lang = ["eng", "spa", "slv"]))))
eventRes = er.execQuery(q)

# get list of 10 articles about the event
q.setRequestedResult(RequestEventArticles(page = 1, count = 10))        # get 10 articles about the event (any language is ok) that are closest to the center of the event
eventRes = er.execQuery(q)

#
# OTHER AGGREGATES ABOUT THE EVENT
#

# get information about how reporting about the event was trending over time
q.setRequestedResult(RequestEventArticleTrend())
eventRes = er.execQuery(q)

# get the tag cloud of top words for the event
q.setRequestedResult(RequestEventKeywordAggr())
eventRes = er.execQuery(q)

# get information about the news sources that reported about the event
q.setRequestedResult(RequestEventSourceAggr())
eventRes = er.execQuery(q)

# return the
q.setRequestedResult(RequestEventSimilarEvents(
    conceptInfoList=[
        {"uri": er.getConceptUri("Trump"), "wgt": 100},
        {"uri": er.getConceptUri("Obama"), "wgt": 100},
        {"uri": er.getConceptUri("Richard Nixon"), "wgt": 30},
        {"uri": er.getConceptUri("republican party"), "wgt": 30},
        {"uri": er.getConceptUri("democrat party"), "wgt": 30}
    ]
))
eventRes = er.execQuery(q)

