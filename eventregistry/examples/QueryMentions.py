"""
examples that illustrate how to query for mentions using different search options
"""
from eventregistry import *

er = EventRegistry(allowUseOfArchive=False)

#
# Find mentions of stock price change event types related to companies in the transportation industry that occured in April 2023.
#
iter = QueryMentionsIter(
    eventTypeUri = "et/business/stock-prices/stock-price",
    industryUri= "sectors/Transportation",
    dateStart = "2023-04-01",
    dateEnd = "2023-04-30"
)
# iterate over first 100 mentions. Increase maxItems or remove it completely to get more/all results
for m in iter.execQuery(er, sortBy = "date", maxItems = 100):
    print(m)

# alternatively, the same query using the complex query language
q = {
    "$query": {
        "eventTypeUri": "et/business/stock-prices/stock-price",
        "industryUri": "sectors/Transportation",
        "dateStart": "2023-04-01",
        "dateEnd": "2023-04-30"
    }
}
iter = QueryMentionsIter.initWithComplexQuery(q)
for m in iter.execQuery(er, sortBy = "date", maxItems = 100):
    print(m)


#
# Find mentions of event types related to products and services which are related to companies Microsoft, Open AI or Google.
#
microsoftUri = er.getConceptUri("Microsoft")
openaiUri = er.getConceptUri("OpenAI")
googleUri = er.getConceptUri("Google")
iter = QueryMentionsIter(
    eventTypeUri = "et/business/products-services",
    conceptUri = QueryItems.OR([microsoftUri, openaiUri, googleUri])
)
# iterate over first 100 mentions. Increase maxItems or remove it completely to get more/all results
for m in iter.execQuery(er, sortBy = "date", maxItems = 100):
    print(m)

# alternatively, the same query using the complex query language
q = {
    "$query": {
        "$and": [
            {
                "eventTypeUri": "et/business/products-services",
            },
            {
                "conceptUri": {
                    "$or": [
                        "http://en.wikipedia.org/wiki/Microsoft",
                        "http://en.wikipedia.org/wiki/OpenAI",
                        "http://en.wikipedia.org/wiki/Google"
                    ]
                }
            }
        ]
    }
}
iter = QueryMentionsIter.initWithComplexQuery(q)
for m in iter.execQuery(er, sortBy = "date", maxItems = 100):
    print(m)


#
# get time distribution of the events related to acquisitions and mergers
#
q = QueryMentions(eventTypeUri="et/business/acquisitions-mergers")
q.setRequestedResult(RequestMentionsTimeAggr())
res = er.execQuery(q)
for obj in res.get("timeAggr", {}).get("results", []):
    print("%s: %d" % (obj["date"], obj["count"]))

#
# get 10.000 uris of mentions that are related to mergers and acquisitions
#
q = QueryMentions(eventTypeUri="et/business/acquisitions-mergers")
q.setRequestedResult(RequestMentionsUriWgtList())
res = er.execQuery(q)
uriList = er.getUriFromUriWgt(res.get("uriWgtList", {}).get("results", []))
print("Retrieved %d uris" % len(uriList))


#
# get mentions related to labor issues and print first 100 of them
#
q = QueryMentions(eventTypeUri="et/business/labor-issues")
res = er.execQuery(q)
for m in res.get("mentions", {}).get("results", []):
    print(m)
