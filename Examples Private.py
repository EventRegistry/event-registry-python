from EventRegistry import *

er = EventRegistry(host = "http://beta.eventregistry.org", logging = True)
#er = EventRegistry(host = "http://localhost:8090", logging = True)

ret = er.getRecentArticles()

ret = er.getRecentEvents(
    returnInfo = ReturnInfo(eventInfo = EventInfoFlags(concepts = True, imageCount = 1, stories = True)))

q = QueryEvents()
q.addConcept(er.getConceptUri("Obama"))                 # get events related to obama
q.addRequestedResult(RequestEventsConceptGraph(conceptCount = 2000, linkCount = 5000, eventsSampleSize = 2000))
res = er.execQuery(q)