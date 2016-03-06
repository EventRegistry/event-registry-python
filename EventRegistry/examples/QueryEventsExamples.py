from eventregistry import *

er = EventRegistry()

# query for events related to Barack obama
q = QueryEvents()
q.addConcept(er.getConceptUri("Obama"))                 # get events related to obama
#q.addCategory(er.getCategoryUri("society issues"))      # and are related to issues in society
#q.addNewsSource(er.getNewsSourceUri("bbc"))             # and have been reported by BBC
q.addRequestedResult(RequestEventsUriList())            # return uris of all events
q.addRequestedResult(RequestEventsInfo(page = 0, count = 30, sortBy = "size", sortByAsc = True, 
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(lang = "deu", type = ["person", "wiki"]))))   # return event details for first 30 events
q.addRequestedResult(RequestEventsConceptAggr(conceptCount = 5, 
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(type = ["org", "loc"]))))        # compute concept aggregate on the events
res = er.execQuery(q)
obj = createStructFromDict(res)

# use OR operator between concepts
# find events where either Sandra Bullock or Gerge Clooney are relevant. since we use OR, res3 should have more results than res1 and res2
res1 = er.execQuery(QueryEvents(conceptUri = er.getConceptUri("sandra bullock"), requestedResult = RequestEventsInfo(count = 0)))
res2 = er.execQuery(QueryEvents(conceptUri = er.getConceptUri("george clooney"), requestedResult = RequestEventsInfo(count = 0)))
res3 = er.execQuery(QueryEvents(conceptUri = [er.getConceptUri("sandra bullock"), er.getConceptUri("george clooney")], 
                                conceptOper = "OR", 
                                requestedResult = RequestEventsInfo(count = 0)))
c1 = res1["events"]["resultCount"]
c2 = res2["events"]["resultCount"]
c3 = res3["events"]["resultCount"]
assert c3 > c1
assert c3 > c2

# find events that occured in Berlin between 2014-04-16 and 2014-04-28
# from the resulting events produce
# - the trending information about the top people involved in these events
# - info about the categories of these events
# - general information about the 20 most recent events in that time span
q = QueryEvents()
q.addLocation(er.getLocationUri("Berlin"))
q.setDateLimit(datetime.date(2014, 4, 16), datetime.date(2014, 4, 28))
q.addRequestedResult(RequestEventsConceptTrends(conceptCount = 40, 
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(type = ["person"]))))
q.addRequestedResult(RequestEventsCategoryAggr())
q.addRequestedResult(RequestEventsInfo())
res = er.execQuery(q)

q = QueryEvents()
q.addConcept(er.getConceptUri("Obama"))                 # get events related to obama
q.addRequestedResult(RequestEventsConceptGraph(conceptCount = 200, linkCount = 500, eventsSampleSize = 2000))
res = er.execQuery(q)

# get recent events related to Obama
q = QueryEvents()
q.addConcept(er.getConceptUri("Obama"))
q.addRequestedResult(RequestEventsRecentActivity())     # get most recently updated events related to obama
res = er.execQuery(q)
obj = createStructFromDict(res)
