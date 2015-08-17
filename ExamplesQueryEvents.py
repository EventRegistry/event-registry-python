from EventRegistry import *

#er = EventRegistry(host = "http://eventregistry.org", logging = True)
er = EventRegistry(host = "http://localhost:8090", logging = True)

# query for events related to Barack obama
q = QueryEvents()
q.addConcept(er.getConceptUri("Obama"))                 # get events related to obama
#q.addCategory(er.getCategoryUri("society issues"))      # and are related to issues in society
#q.addNewsSource(er.getNewsSourceUri("bbc"))             # and have been reported by BBC
q.addRequestedResult(RequestEventsUriList())            # return uris of all events
q.addRequestedResult(RequestEventsInfo(page = 0, count = 30, sortBy = "size", sortByAsc = True, 
                                       returnInfo = ReturnInfo(conceptLang = "deu", conceptType = ["person", "wiki"])))   # return event details for first 30 events
q.addRequestedResult(RequestEventsConceptAggr(conceptCount = 5, 
                                              returnInfo = ReturnInfo(conceptType = ["org", "loc"])))        # compute concept aggregate on the events
res = er.execQuery(q)
obj = createStructFromDict(res)

# find events that occured in Berlin between 2014-04-16 and 2014-04-28
# from the resulting events produce
# - the trending information about the top people involved in these events
# - info about the categories of these events
# - general information about the 20 most recent events in that time span
q = QueryEvents()
q.addLocation(er.getLocationUri("Berlin"))
q.setDateLimit(datetime.date(2014, 4, 16), datetime.date(2014, 4, 28))
q.addRequestedResult(RequestEventsConceptTrends(conceptCount = 40, 
                                                returnInfo = ReturnInfo(conceptType=["person"])))
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
