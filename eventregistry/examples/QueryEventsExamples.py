"""
examples of how to search for events using different search criteria
"""
from eventregistry import *
import json

er = EventRegistry()

# get the concept URI that matches label "Barack Obama"
obamaConceptUri = er.getConceptUri("Obama")
print("Concept uri for 'Obama' is " + obamaConceptUri)

#
# USE OF ITERATOR
# example of using the QueryEventsIter to easily iterate through all results matching the search
#

# query for events related to Barack Obama. return the matching events sorted from the latest to oldest event
# use the iterator class and easily iterate over all matching events
# we specify maxItems to limit the results to maximum 300 results
q = QueryEventsIter(conceptUri = obamaConceptUri)
for event in q.execQuery(er, sortBy = "date", maxItems = 300):
    print(json.dumps(event, indent=2))


# make a query for events - specify each condition independently
# get events related to obama
q = QueryEvents(conceptUri = obamaConceptUri)
# return a list of event URIs (i.e. ["eng-234", "deu-234", ...])
q.setRequestedResult(RequestEventsUriList())
res = er.execQuery(q)


# use the previous query, but change the return details to return information about 30 events that are most related to Obama
q.setRequestedResult(RequestEventsInfo(count = 30, sortBy = "rel", sortByAsc = False,
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(lang = "deu", type = ["person", "wiki"]))))
res = er.execQuery(q)


# use the previous query, but this time compute most relevant concepts of type organization or location extracted from events about Obama
q.setRequestedResult(RequestEventsConceptAggr(conceptCount = 20,
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(type = ["org", "loc"]))))
res = er.execQuery(q)


# get the URI for the BBC news source
bbcSourceUri = er.getNewsSourceUri("BBC")
print("Source uri for 'BBC' is " + bbcSourceUri)

# query for events reported by BBC News
q = QueryEvents(sourceUri = bbcSourceUri)
# return details about 30 events that have been most recently reported by BBC
q.setRequestedResult(RequestEventsInfo(count = 30, sortBy = "date", sortByAsc = False))
res = er.execQuery(q)


# get the category URI that matches label "society issues"
issuesCategoryUri = er.getCategoryUri("society issues")
print("Category uri for 'society issues' is " + issuesCategoryUri)

# query for events related to issues in society
q = QueryEvents(categoryUri = issuesCategoryUri)
# return 30 events that were reported in the highest number of articles
q.setRequestedResult(RequestEventsInfo(count = 30, sortBy = "size", sortByAsc = False))
res = er.execQuery(q)


# find events that occured in Berlin between 2014-04-16 and 2014-04-28
# from the resulting events produce
# - the trending information about the top people involved in these events
# - info about the categories of these events
# - general information about the 20 most recent events in that time span
q = QueryEvents(
    locationUri = er.getLocationUri("Berlin"),
    dateStart = datetime.date(2015, 4, 16), dateEnd = datetime.date(2015, 4, 28))
q.setRequestedResult(RequestEventsConceptTrends(conceptCount = 40,
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(type = ["person"]))))
res = er.execQuery(q)

q.setRequestedResult(RequestEventsCategoryAggr())
res = er.execQuery(q)

q.setRequestedResult(RequestEventsInfo())
res = er.execQuery(q)

# query for events about Obama and produce the concept co-occurence graph - which concepts appear frequently together in the matching events
q = QueryEvents(conceptUri = er.getConceptUri("Obama"))
q.setRequestedResult(RequestEventsConceptGraph(conceptCount = 200, linkCount = 500, eventsSampleSize = 2000))
res = er.execQuery(q)

#
# COMPLEX QUERIES
# examples of complex queries that combine various OR and AND operators
#

# events that are occured between 2017-02-05 and 2017-02-05 and are not about business
businessUri = er.getCategoryUri("Business")
q = QueryEvents.initWithComplexQuery("""
{
    "$query": {
        "dateStart": "2017-02-05", "dateEnd": "2017-02-06",
        "$not": {
            "categoryUri": "%s"
        }
    }
}
""" % (businessUri))
res = er.execQuery(q)

# example of a complex query containing a combination of OR and AND parameters
# get events that happened on 2017-02-05 or are about trump or are about politics or are about Merkel and business
# # and did not happen on 2017-02-05 or are about Obama
trumpUri = er.getConceptUri("Trump")
obamaUri = er.getConceptUri("Obama")
politicsUri = er.getCategoryUri("politics")
merkelUri = er.getConceptUri("merkel")
businessUri = er.getCategoryUri("business")

qStr = """
{
    "$query": {
        "$or": [
            { "dateStart": "2017-02-05", "dateEnd": "2017-02-05" },
            { "conceptUri": "%s" },
            { "categoryUri": "%s" },
            {
                "$and": [
                    { "conceptUri": "%s" },
                    { "categoryUri": "%s" }
                ]
            }
        ],
        "$not": {
            "$or": [
                { "dateStart": "2017-02-04", "dateEnd": "2017-02-04" },
                { "conceptUri": "%s" }
            ]
        }
    }
}
    """ % (trumpUri, politicsUri, merkelUri, businessUri, obamaUri)
q1 = QueryEvents.initWithComplexQuery(qStr)
res = er.execQuery(q1)

cq = ComplexEventQuery(
    query = CombinedQuery.OR([
            BaseQuery(dateStart = "2017-02-04", dateEnd = "2017-02-05"),
            BaseQuery(conceptUri = trumpUri),
            BaseQuery(categoryUri = politicsUri)
        ],
        exclude = CombinedQuery.OR([
            BaseQuery(dateStart = "2017-02-04", dateEnd = "2017-02-04"),
            BaseQuery(conceptUri = obamaUri)]
        )))

retInfo = ReturnInfo(eventInfo = EventInfoFlags(concepts = True, categories = True, stories = True))

# example of an ITERATOR with a COMPLEX QUERY
iter = QueryEventsIter.initWithComplexQuery(cq)
for event in iter.execQuery(er, returnInfo =  retInfo, maxItems = 10):
    print(json.dumps(event, indent=2))
