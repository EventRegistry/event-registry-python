from eventregistry import *


er = EventRegistry()

iter = QueryEventArticlesIter("eng-2940883")
for art in iter.execQuery(er, lang = "eng"):
    print art

# get info about event with a particular uri
q = QueryEvent("eng-88")
q.setRequestedResult(RequestEventInfo(
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(lang = ["eng", "spa", "slv"]))))
eventRes = er.execQuery(q)

q.setRequestedResult(RequestEventArticles(page = 1, count = 10))        # get 10 articles about the event (any language is ok) that are closest to the center of the event
eventRes = er.execQuery(q)

q.setRequestedResult(RequestEventArticleTrend())
eventRes = er.execQuery(q)

q.setRequestedResult(RequestEventKeywordAggr())
eventRes = er.execQuery(q)

# obtain in one call information about events with uris 234, 212 and 423
q = QueryEvent(["spa-32", "spa-45"])
q.setRequestedResult(RequestEventArticles(page =1, count = 200))
res = er.execQuery(q)
obj = createStructFromDict(res)


