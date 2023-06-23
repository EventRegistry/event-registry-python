"""
examples of how to search for events using different search criteria
"""
from eventregistry import *
import json, datetime

er = EventRegistry()

# max events to return - change for your use case
MAX_RESULTS = 50


# get the concept URI that matches label "Barack Obama"
obamaUri = er.getConceptUri("Obama")
print("Concept uri for 'Obama' is " + obamaUri)

someDaysAgo = datetime.datetime.now() - datetime.timedelta(days=20)

#
# USE OF ITERATOR
# example of using the QueryEventsIter to easily iterate through all results matching the search
#

# query for events related to Barack Obama. return the matching events sorted from the latest to oldest event
# use the iterator class and easily iterate over all matching events
# we specify maxItems to limit the results to maximum MAX_RESULTS results
q = QueryEventsIter(conceptUri = obamaUri)
for event in q.execQuery(er, sortBy = "date", maxItems = MAX_RESULTS):
    # print(json.dumps(event, indent=2))
    print(event["uri"])


# find events that:
# * are about Barack Obama
# * that were covered also by New York Times
# * that occurred in 2015
# * return events sorted by how much were articles in the event shared on social media (instead of relevance, which is default)
q = QueryEvents(
    conceptUri = obamaUri,
    dateStart = "2015-01-01",
    dateEnd = "2015-12-31",
    sourceUri = er.getSourceUri("new york times"))
# return a list of event URIs (i.e. ["eng-234", "deu-234", ...])
q.setRequestedResult(RequestEventsInfo(sortBy = "socialScore"))
res = er.execQuery(q)

# find events that:
# * contain articles that mention words Apple, Google and Samsung
# * contain at least one article from a news source that is located in Italy
q = QueryEvents(
    keywords=QueryItems.AND(["Apple", "Google", "Samsung"]),
    dateStart = someDaysAgo,
    sourceLocationUri=er.getLocationUri("Italy"))
res = er.execQuery(q)


# use the previous query, but change the return details to return information about 30 events sorted from latest to oldest
# when providing the concept information include the labels of the concept in German language
q.setRequestedResult(RequestEventsInfo(count = 30, sortBy = "date", sortByAsc = False,
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(lang = "deu", type = ["person", "wiki"]))))
res = er.execQuery(q)


# use the previous query, but this time compute most relevant concepts of type organization or location extracted from events matching the search
q.setRequestedResult(RequestEventsConceptAggr(conceptCount = 20,
    returnInfo = ReturnInfo(eventInfo=EventInfoFlags(imageCount=5))))
res = er.execQuery(q)


# get the URI for the BBC news source
bbcSourceUri = er.getNewsSourceUri("BBC")
print("Source uri for 'BBC' is " + bbcSourceUri)

# query for events that were reported by BBC News
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

#
# OTHER AGGREGATES (INSTEAD OF OBTAINING EVENTS)
#

# find events that occurred in Germany between 2014-04-16 and 2014-04-28
# from the resulting events produce:
q = QueryEvents(
    locationUri = er.getLocationUri("Germany"),
    dateStart=datetime.date(2017, 12, 16), dateEnd=datetime.date(2018, 1, 28))

# get the list of top concepts about the events that match criteria
q.setRequestedResult(RequestEventsConceptAggr())
res = er.execQuery(q)

# find where the events occurred geographically
q.setRequestedResult(RequestEventsLocAggr())
res = er.execQuery(q)

# find when the events matching the criteria occurred
q.setRequestedResult(RequestEventsTimeAggr())
res = er.execQuery(q)

# the trending information about the top people involved in these events
q.setRequestedResult(RequestEventsConceptTrends(conceptCount = 40,
    returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(type = ["person"]))))
res = er.execQuery(q)

# get the top categories about the same events
q.setRequestedResult(RequestEventsCategoryAggr())
res = er.execQuery(q)


# query for events about Obama and produce the concept co-occurrence graph - which concepts appear frequently together in the matching events
q = QueryEvents(conceptUri = er.getConceptUri("Obama"))
q.setRequestedResult(RequestEventsConceptGraph(conceptCount = 200, linkCount = 500, eventsSampleSize = 2000))
res = er.execQuery(q)

#
# COMPLEX QUERIES
# examples of complex queries that combine various OR and AND operators
#

# events that are occurred between 2017-02-05 and 2017-02-06 and are not about business
businessUri = er.getCategoryUri("Business")
query = QueryEvents.initWithComplexQuery({
    "$query": {
        "dateStart": "2017-02-05", "dateEnd": "2017-02-06",
        "$not": {
            "categoryUri": businessUri
        }
    }
})
res = er.execQuery(query)

# example of a complex query containing a combination of OR and AND parameters
# get events that:
# * happened on 2017-02-05
# * are about trump, or
# * are about politics, or
# * are about Merkel and business
# and did not happen on 2017-02-04 or are about Obama
trumpUri = er.getConceptUri("Trump")
obamaUri = er.getConceptUri("Obama")
politicsUri = er.getCategoryUri("politics")
merkelUri = er.getConceptUri("merkel")
businessUri = er.getCategoryUri("business")

q = {
    "$query": {
        "$or": [
            { "dateStart": "2017-02-05", "dateEnd": "2017-02-05" },
            { "conceptUri": trumpUri },
            { "categoryUri": politicsUri },
            {
                "$and": [
                    { "conceptUri": merkelUri },
                    { "categoryUri": businessUri }
                ]
            }
        ],
        "$not": {
            "$or": [
                { "dateStart": "2017-02-04", "dateEnd": "2017-02-04" },
                { "conceptUri": obamaUri }
            ]
        }
    }
}
query = QueryEvents.initWithComplexQuery(q)
res = er.execQuery(query)

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
for event in iter.execQuery(er, returnInfo =  retInfo, maxItems = MAX_RESULTS):
    print(json.dumps(event, indent=2))



#
# use of EXACT search mode when using keywords
# NOTE: You don’t have to write AND, OR, NOT in uppercase — we will use uppercase just to make examples more readable.
#

# USE OF AND, OR and NOT operators
# find events from Jan 2013 that mention samsung and tv and either led or lcd or plasma but not smartphone or phone
q = {
    "$query": {
        "keyword": "Samsung AND TV AND (LED OR LCD OR Plasma) NOT (smartphone OR phone)",
        "keywordSearchMode": "exact",
        "dateStart": "2023-01-01",
        "dateEnd": "2023-01-31"
    }
}
iter = QueryEventsIter.initWithComplexQuery(q)
for ev in iter.execQuery(er, maxItems = MAX_RESULTS):
    print(ev)


# use of operator NEAR
# find English events that mention siemens and sustainability or ecology or renewable energy, but at most 15 words apart (forward or backward)
q = {
    "$query": {
        "keyword": "Siemens NEAR/15 (sustainability or ecology or renewable energy)",
        "keywordSearchMode": "exact",
        "lang": "eng"
    }
}
iter = QueryEventsIter.initWithComplexQuery(q)
for ev in iter.execQuery(er, maxItems = MAX_RESULTS):
    print(ev)


# use of operator NEXT
# find English events that mention sustainability or ecology or renewable energy at most 15 words after siemens is mentioned
q = {
    "$query": {
        "keyword": "Siemens NEXT/15 (sustainability or ecology or renewable energy)",
        "keywordSearchMode": "exact",
        "lang": "eng"
    }
}
iter = QueryEventsIter.initWithComplexQuery(q)
for ev in iter.execQuery(er, maxItems = MAX_RESULTS):
    print(ev)


#
# use of SIMPLE search mode when using keywords
#

# find events that at least some of the specified keywords and phrases and that belong to the AI category
q = {
    "$query": {
        "keyword": "AI \\\"deep learning\\\" \\\"machine learning\\\" latest developments",
        "keywordSearchMode": "simple",
        "categoryUri": "dmoz/Computers/Artificial_Intelligence"
    }
}
iter = QueryEventsIter.initWithComplexQuery(q)
for ev in iter.execQuery(er, sortBy = "rel", maxItems = MAX_RESULTS):
    print(ev)

# the same query, but without using the complex query language
iter = QueryEventsIter(keywords = "AI \\\"deep learning\\\" \\\"machine learning\\\" latest developments", keywordSearchMode="simple")
for ev in iter.execQuery(er, sortBy = "rel", maxItems = MAX_RESULTS):
    print(ev)


#
# use of PHRASE search mode when using keywords
# phrase search mode is used by default, so in this case, you don't even need to specify the "keywordSearchMode" parameter
#

# search for events that mention the phrase "Apple iPhone" or "Microsoft Store"
qStr = {
    "$query": {
        "$or": [
            { "keyword": "Apple iPhone" },
            { "keyword": "Microsoft Store" }
        ]
    }
}
q = QueryEventsIter.initWithComplexQuery(qStr)
