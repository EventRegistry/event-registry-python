from eventregistry import *

er = EventRegistry()

#
# query for events related to Barack Obama
#

q = QueryEventsIter(conceptUri = er.getConceptUri("Obama"))
for event in q.execQuery(er, sortBy = "date"):
    print event


# get the concept URI that matches label "Barack Obama"
obamaConceptUri = er.getConceptUri("Obama")
print("Concept uri for 'Obama' is " + obamaConceptUri)

# make a query for events
q = QueryEvents()
q.addConcept(obamaConceptUri)                 # get events related to obama
# return a list of event URIs
q.setRequestedResult(RequestEventsUriList())
res = er.execQuery(q)

# return details about 30 events that are most related to Obama
q.setRequestedResult(RequestEventsInfo(count = 30, sortBy = "rel", sortByAsc = False,
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(lang = "deu", type = ["person", "wiki"]))))
res = er.execQuery(q)

# compute most relevant concepts of type organization or location extracted from events about Obama
q.setRequestedResult(RequestEventsConceptAggr(conceptCount = 20,
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(type = ["org", "loc"]))))
res = er.execQuery(q)


#
# query for events reported by BBC News
#

# get the news source URI that matches label "BBC"
bbcSourceUri = er.getNewsSourceUri("BBC")
print("Source uri for 'BBC' is " + bbcSourceUri)

# make a query for events
q = QueryEvents()
q.addNewsSource(bbcSourceUri)
# return details about 30 events that have been most recently reported by BBC
q.setRequestedResult(RequestEventsInfo(count = 30, sortBy = "date", sortByAsc = False))
res = er.execQuery(q)


#
# query for events related to issues in society
#

# get the category URI that matches label "society issues"
issuesCategoryUri = er.getCategoryUri("society issues")
print("Category uri for 'society issues' is " + issuesCategoryUri)

# make a query for events
q = QueryEvents()
q.addCategory(issuesCategoryUri)
# return 30 events that were reported in the highest number of articles
q.setRequestedResult(RequestEventsInfo(count = 30, sortBy = "size", sortByAsc = False))
res = er.execQuery(q)


## use OR operator between concepts
## find events where either Sandra Bullock or Gerge Clooney are relevant. since we use OR, res3 should have more results than res1 and res2
#res1 = er.execQuery(QueryEvents(conceptUri = er.getConceptUri("sandra bullock"), requestedResult = RequestEventsInfo(count = 0)))
#res2 = er.execQuery(QueryEvents(conceptUri = er.getConceptUri("george clooney"), requestedResult = RequestEventsInfo(count = 0)))
#res3 = er.execQuery(QueryEvents(conceptUri = [er.getConceptUri("sandra bullock"), er.getConceptUri("george clooney")],
#                                conceptOper = "OR",
#                                requestedResult = RequestEventsInfo(count = 0)))
#c1 = res1["events"]["totalResults"]
#c2 = res2["events"]["totalResults"]
#c3 = res3["events"]["totalResults"]
#assert c3 > c1
#assert c3 > c2

# find events that occured in Berlin between 2014-04-16 and 2014-04-28
# from the resulting events produce
# - the trending information about the top people involved in these events
# - info about the categories of these events
# - general information about the 20 most recent events in that time span
q = QueryEvents()
q.addLocation(er.getLocationUri("Berlin"))
q.setDateLimit(datetime.date(2015, 4, 16), datetime.date(2015, 4, 28))
q.setRequestedResult(RequestEventsConceptTrends(conceptCount = 40,
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(type = ["person"]))))
res = er.execQuery(q)

q.setRequestedResult(RequestEventsCategoryAggr())
res = er.execQuery(q)

q.setRequestedResult(RequestEventsInfo())
res = er.execQuery(q)

q = QueryEvents()
q.addConcept(er.getConceptUri("Obama"))                 # get events related to obama
q.setRequestedResult(RequestEventsConceptGraph(conceptCount = 200, linkCount = 500, eventsSampleSize = 2000))
res = er.execQuery(q)

# get recent events related to Obama
q = QueryEvents()
q.addConcept(er.getConceptUri("Obama"))
q.setRequestedResult(RequestEventsRecentActivity())     # get most recently updated events related to obama
res = er.execQuery(q)
obj = createStructFromDict(res)
