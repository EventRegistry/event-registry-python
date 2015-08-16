from EventRegistry import *

er = EventRegistry(host = "http://beta.eventregistry.org", logging = True)
#er = EventRegistry(host = "http://localhost:8090", logging = True)

ret = er.getRecentArticles(includeArticleConcepts = True)

ret = er.getRecentEvents(includeEventConcepts = True, includeEventImages = True, includeEventStories = True)

q = QueryEvents();
q.addConcept(er.getConceptUri("Obama"))                 # get events related to obama
q.addRequestedResult(RequestEventsConceptGraph(conceptCount = 2000, linkCount = 5000, eventsSampleSize = 2000))
res = er.execQuery(q)