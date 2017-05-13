"""
examples to obtain information what are the top fb shared articles on a particular day or
what are the events, for which the articles were shared the most
"""

from eventregistry import *

er = EventRegistry()

# get top shared articles for a date
q = GetTopSharedArticles(date = "2015-05-23", count = 30)
ret = er.execQuery(q)
print(er.format(ret))

# get top shared events for a date
q = GetTopSharedEvents(date = "2015-05-23", count = 30)
ret = er.execQuery(q)
print(er.format(ret))


# get social shared information for resulting articles
q = QueryArticles(conceptUri = er.getConceptUri("Apple"))
q.setRequestedResult(RequestArticlesInfo(
    count = 5,
    sortBy = "socialScore",
    returnInfo = ReturnInfo(
        articleInfo = ArticleInfoFlags(socialScore = True))))
ret = er.execQuery(q)
print(er.format(ret))


# get social shared information for resulting events
q = QueryEvents(conceptUri = er.getConceptUri("Apple"))
q.setRequestedResult(RequestEventsInfo(
    count = 5,
    sortBy = "socialScore",
    returnInfo = ReturnInfo(
        eventInfo = EventInfoFlags(socialScore = True))))
ret = er.execQuery(q)
print(er.format(ret))