from eventregistry import *

er = EventRegistry()

# get info about event with a particular uri
q = QueryEvent("eng-88")
q.addRequestedResult(RequestEventInfo(
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(lang = ["eng", "spa", "slv"]))))
q.addRequestedResult(RequestEventArticles(page = 1, count = 10))        # get 10 articles about the event (any language is ok) that are closest to the center of the event
q.addRequestedResult(RequestEventArticleTrend())
q.addRequestedResult(RequestEventKeywordAggr())
eventRes = er.execQuery(q)

# obtain in one call information about events with uris 234, 212 and 423
q = QueryEvent(["spa-32", "spa-45"])
q.addRequestedResult(RequestEventArticles(page =1, count = 200))
res = er.execQuery(q)
obj = createStructFromDict(res)


