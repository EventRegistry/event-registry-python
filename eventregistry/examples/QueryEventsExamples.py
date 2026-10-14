"""
examples of how to search for events using different search criteria
"""
import datetime
import json
import os
import sys

from eventregistry import (EventRegistry, QueryEvents, QueryEventsIter, QueryItems, BaseQuery, CombinedQuery,
                           ComplexEventQuery, ReturnInfo, EventInfoFlags, ConceptInfoFlags,
                           RequestEventsInfo, RequestEventsConceptAggr, RequestEventsLocAggr, RequestEventsTimeAggr,
                           RequestEventsConceptTrends, RequestEventsCategoryAggr, RequestEventsKeywordAggr,
                           RequestEventsLocTimeAggr, RequestEventsConceptMatrix, RequestEventsSourceAggr,
                           RequestEventsDateMentionAggr, RequestEventsConceptGraph)

# max events to return - change for your use case
MAX_RESULTS = 50


#
# USE OF ITERATOR
# example of using the QueryEventsIter to easily iterate through all results matching the search
#


def iterateOverEvents(er):
    """
    use QueryEventsIter to iterate over the events that are related to a concept
    """
    # get the concept URI that matches label "Barack Obama"
    obamaUri = er.getConceptUri("Obama")
    print("Concept uri for 'Obama' is " + obamaUri)

    # query for events related to Barack Obama. return the matching events sorted from the latest to oldest event
    # use the iterator class and easily iterate over all matching events
    # we specify maxItems to limit the results to maximum MAX_RESULTS results
    q = QueryEventsIter(conceptUri = obamaUri)
    for event in q.execQuery(er, sortBy = "date", maxItems = MAX_RESULTS):
        # print(json.dumps(event, indent=2))
        print(event["uri"])


def eventsByConceptDateAndSource(er):
    """
    events about a concept, from a date range, covered by a selected source, sorted by the social score
    """
    obamaUri = er.getConceptUri("Obama")

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
    # return the details about the events, sorted by the number of articles that reported about them
    q.setRequestedResult(RequestEventsInfo(sortBy = "size"))
    res = er.execQuery(q)
    print(er.format(res))


def eventsByKeywordsAndSourceLocation(er):
    """
    events by keywords and a source location - with the default results, with custom details and with a concept aggregate
    """
    someDaysAgo = datetime.datetime.now() - datetime.timedelta(days=20)

    # find events that:
    # * contain articles that mention words Apple, Google and Samsung
    # * contain at least one article from a news source that is located in Italy
    q = QueryEvents(
        keywords=QueryItems.AND(["Apple", "Google", "Samsung"]),
        dateStart = someDaysAgo,
        sourceLocationUri=er.getLocationUri("Italy"))
    res = er.execQuery(q)
    print(er.format(res))

    # use the previous query, but change the return details to return information about 30 events sorted from latest to oldest
    # when providing the concept information include the labels of the concept in German language
    q.setRequestedResult(RequestEventsInfo(count = 30, sortBy = "date", sortByAsc = False,
        returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(lang = "deu", type = ["person", "wiki"]))))
    res = er.execQuery(q)
    print(er.format(res))

    # use the previous query, but this time compute most relevant concepts of type organization or location extracted from events matching the search
    q.setRequestedResult(RequestEventsConceptAggr(conceptCount = 20,
        returnInfo = ReturnInfo(eventInfo=EventInfoFlags(imageCount=5))))
    res = er.execQuery(q)
    print(er.format(res))


def eventsReportedBySource(er):
    """
    the events that were most recently reported by a selected news source
    """
    # get the URI for the BBC news source
    bbcSourceUri = er.getNewsSourceUri("BBC")
    print("Source uri for 'BBC' is " + bbcSourceUri)

    # query for events that were reported by BBC News
    q = QueryEvents(sourceUri = bbcSourceUri)
    # return details about 30 events that have been most recently reported by BBC
    q.setRequestedResult(RequestEventsInfo(count = 30, sortBy = "date", sortByAsc = False))
    res = er.execQuery(q)
    print(er.format(res))


def eventsInCategory(er):
    """
    the events from a category that were reported in the highest number of articles
    """
    # get the category URI that matches label "society issues"
    issuesCategoryUri = er.getCategoryUri("society issues")
    print("Category uri for 'society issues' is " + issuesCategoryUri)

    # query for events related to issues in society
    q = QueryEvents(categoryUri = issuesCategoryUri)
    # return 30 events that were reported in the highest number of articles
    q.setRequestedResult(RequestEventsInfo(count = 30, sortBy = "size", sortByAsc = False))
    res = er.execQuery(q)
    print(er.format(res))


#
# OTHER AGGREGATES (INSTEAD OF OBTAINING EVENTS)
# each aggregate is computed over the events that match the query. Below each example is a shortened
# version of the returned result so that you can see the structure of the output.
# When the query matches a large number of events, the aggregate is computed on a sample of the events -
# in that case the result also contains a "warning" and "usedResults" (sample size) next to "totalResults".
#


def _eventsInGermany(er):
    """
    the query that is used in the examples of the aggregates below
    """
    # find events that occurred in Germany between 2017-12-16 and 2018-01-28
    q = QueryEvents(
        locationUri = er.getLocationUri("Germany"),
        dateStart=datetime.date(2017, 12, 16), dateEnd=datetime.date(2018, 1, 28))
    return q


def conceptAggr(er):
    """
    get the top concepts of the matching events
    """
    q = _eventsInGermany(er)

    # get the list of top concepts about the events that match criteria
    q.setRequestedResult(RequestEventsConceptAggr())
    res = er.execQuery(q)
    print(er.format(res))
    # {
    #     "conceptAggr": {
    #         "usedResults": 4854,
    #         "totalResults": 4854,
    #         "results": [
    #             {"uri": "http://en.wikipedia.org/wiki/Berlin", "type": "loc", "label": {"eng": "Berlin"}, "location": {"type": "place", "label": {"eng": "Berlin"}, "country": {"type": "country", "label": {"eng": "Germany"}}}, "score": 100},
    #             {"uri": "http://en.wikipedia.org/wiki/Deutsche_Presse-Agentur", "type": "org", "label": {"eng": "Deutsche Presse-Agentur"}, "score": 66.2},
    #             ...
    #         ]
    #     }
    # }


def locAggr(er):
    """
    get the locations where the matching events occurred
    """
    q = _eventsInGermany(er)

    # find where the events occurred geographically
    q.setRequestedResult(RequestEventsLocAggr())
    res = er.execQuery(q)
    print(er.format(res))
    # {
    #     "locAggr": {
    #         "usedResults": 3464,
    #         "totalResults": 3464,
    #         "results": [
    #             {"count": 636, "concept": {"uri": "http://en.wikipedia.org/wiki/Berlin", "type": "loc", "label": {"eng": "Berlin"}, "location": {"type": "place", "wikiUri": "http://en.wikipedia.org/wiki/Berlin", "label": {"eng": "Berlin"}, "lat": 52.5, "long": 13.42, "country": {"type": "country", "wikiUri": "http://en.wikipedia.org/wiki/Germany", "label": {"eng": "Germany"}, "lat": 51.5, "long": 10.5}}}},
    #             {"count": 230, "concept": {"uri": "http://en.wikipedia.org/wiki/Munich", "type": "loc", "label": {"eng": "Munich"}, "location": {...}}},
    #             ...
    #         ]
    #     }
    # }


def timeAggr(er):
    """
    get the number of matching events on each day
    """
    q = _eventsInGermany(er)

    # find when the events matching the criteria occurred
    q.setRequestedResult(RequestEventsTimeAggr())
    res = er.execQuery(q)
    print(er.format(res))
    # {
    #     "timeAggr": {
    #         "usedResults": 4854,
    #         "totalResults": 4854,
    #         "results": [
    #             {"date": "2017-12-28", "count": 109},
    #             {"date": "2018-01-01", "count": 117},
    #             ...
    #         ]
    #     }
    # }


def conceptTrends(er):
    """
    get the trending information about the top people involved in the matching events
    """
    q = _eventsInGermany(er)

    # the trending information about the top people involved in these events
    # conceptFreq[i] in each trend item is the number of articles on that date that mention conceptInfo[i]
    # totArts is the total number of all articles published on that date (can be used to normalize the frequencies)
    q.setRequestedResult(RequestEventsConceptTrends(conceptCount = 40,
        returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(type = ["person"]))))
    res = er.execQuery(q)
    print(er.format(res))
    # {
    #     "conceptTrends": {
    #         "usedResults": 4854,
    #         "totalResults": 4854,
    #         "conceptInfo": [
    #             {"uri": "http://en.wikipedia.org/wiki/Pierre-Emerick_Aubameyang", "type": "person", "score": 1, "label": {"eng": "Pierre-Emerick Aubameyang"}},
    #             {"uri": "http://en.wikipedia.org/wiki/Martin_Schulz", "type": "person", "score": 1, "label": {"eng": "Martin Schulz"}},
    #             ...
    #         ],
    #         "trends": [
    #             {"date": "2017-12-16", "conceptFreq": [0, 0, 204], "totArts": 127130},
    #             {"date": "2017-12-17", "conceptFreq": [0, 0, 256], "totArts": 123591},
    #             ...
    #         ]
    #     }
    # }


def categoryAggr(er):
    """
    get the top categories of the matching events
    """
    q = _eventsInGermany(er)

    # get the top categories about the same events
    q.setRequestedResult(RequestEventsCategoryAggr())
    res = er.execQuery(q)
    print(er.format(res))
    # {
    #     "categoryAggr": {
    #         "usedResults": 4854,
    #         "totalResults": 4854,
    #         "results": [
    #             {"uri": "news/Sports", "label": "news/Sports", "count": 1056},
    #             {"uri": "news/Politics", "label": "news/Politics", "count": 904},
    #             ...
    #         ]
    #     }
    # }


def keywordAggr(er):
    """
    get the top keywords that summarize the matching events
    """
    q = _eventsInGermany(er)

    # get the top keywords that summarize the matching events
    q.setRequestedResult(RequestEventsKeywordAggr())
    res = er.execQuery(q)
    print(er.format(res))
    # {
    #     "keywordAggr": {
    #         "usedResults": 4854,
    #         "totalResults": 4854,
    #         "results": [
    #             {"keyword": "spd", "weight": 0.184},
    #             {"keyword": "sagte", "weight": 0.161},
    #             ...
    #         ]
    #     }
    # }


def locTimeAggr(er):
    """
    get the locations of the matching events together with the time distribution of the events at each location
    """
    q = _eventsInGermany(er)

    # get the locations where the events occurred together with the time distribution of the events at each location
    q.setRequestedResult(RequestEventsLocTimeAggr())
    res = er.execQuery(q)
    print(er.format(res))
    # {
    #     "locTimeAggr": {
    #         "usedResults": 4854,
    #         "totalResults": 4854,
    #         "results": [
    #             {"concept": {"uri": "http://en.wikipedia.org/wiki/Bavaria", "type": "loc", "label": {"eng": "Bavaria"}, "location": {...}}, "counts": [{"date": "2017-12-16", "count": 3}, {"date": "2017-12-17", "count": 2}, ...]},
    #             {"concept": {"uri": "http://en.wikipedia.org/wiki/Berlin", "type": "loc", "label": {"eng": "Berlin"}, "location": {...}}, "counts": [{"date": "2017-12-16", "count": 9}, {"date": "2017-12-17", "count": 19}, ...]},
    #             ...
    #         ]
    #     }
    # }


def conceptMatrix(er):
    """
    get the co-occurrence matrix of the top concepts in the matching events
    """
    q = _eventsInGermany(er)

    # obtain the concept matrix - co-occurrence of the top concepts in the matching events
    # freqMatrix[i][j] is the number of events that mention both concepts[i] and concepts[j] (the diagonal is the frequency of the concept itself)
    # scoreMatrix[i][j] is the "interestingness" of the pair, computed with the selected measure (pmi by default)
    q.setRequestedResult(RequestEventsConceptMatrix())
    res = er.execQuery(q)
    print(er.format(res))
    # {
    #     "conceptMatrix": {
    #         "usedResults": 3464,
    #         "totalResults": 3464,
    #         "concepts": [
    #             {"uri": "http://en.wikipedia.org/wiki/Police", "type": "wiki", "label": {"eng": "Police"}},
    #             {"uri": "http://en.wikipedia.org/wiki/Association_football", "type": "wiki", "label": {"eng": "Association football"}},
    #             ...
    #         ],
    #         "freqMatrix": [
    #             [560, 7, ...],
    #             [7, 351, ...],
    #             ...
    #         ],
    #         "scoreMatrix": [
    #             [0, -2.09, ...],
    #             [-2.09, 0, ...],
    #             ...
    #         ]
    #     }
    # }


def sourceAggr(er):
    """
    get the top news sources that reported about the matching events
    """
    q = _eventsInGermany(er)

    # obtain the top news sources that reported about the matching events
    # "counts.frequency" is the number of articles about the matching events published by the source
    q.setRequestedResult(RequestEventsSourceAggr())
    res = er.execQuery(q)
    print(er.format(res))
    # {
    #     "sourceAggr": {
    #         "usedResults": 4854,
    #         "totalResults": 4854,
    #         "countsPerSource": [
    #             {"source": {"uri": "t-online.de", "dataType": "news", "title": "T-online.de"}, "counts": {"frequency": 2315, "total": 4854}},
    #             {"source": {"uri": "stern.de", "dataType": "news", "title": "stern.de"}, "counts": {"frequency": 1288, "total": 4854}},
    #             ...
    #         ],
    #         "countsPerCountry": [
    #             {"uri": "http://en.wikipedia.org/wiki/Germany", "type": "loc", "label": {"eng": "Germany"}, "location": {"type": "country", "wikiUri": "http://en.wikipedia.org/wiki/Germany", "label": {"eng": "Germany"}, "lat": 51.5, "long": 10.5}, "frequency": 45182, "sources": null},
    #             {"uri": "http://en.wikipedia.org/wiki/Austria", "type": "loc", "label": {"eng": "Austria"}, "location": {...}, "frequency": 3215, "sources": null},
    #             ...
    #         ]
    #     }
    # }


def dateMentionAggr(er):
    """
    get the dates that are mentioned in the articles about the matching events
    """
    q = _eventsInGermany(er)

    # obtain the dates that are mentioned in the text of the articles about the matching events (not the event dates)
    q.setRequestedResult(RequestEventsDateMentionAggr())
    res = er.execQuery(q)
    print(er.format(res))
    # {
    #     "dateMentionAggr": {
    #         "usedResults": 4854,
    #         "totalResults": 4854,
    #         "results": [
    #             {"date": "2000-07-27", "count": 5},
    #             {"date": "2001-09-11", "count": 5},
    #             ...
    #         ]
    #     }
    # }


def conceptGraph(er):
    """
    get the graph of the concepts that frequently appear together in the matching events
    """
    # query for events about Obama and produce the concept co-occurrence graph - which concepts appear frequently together in the matching events
    q = QueryEvents(conceptUri = er.getConceptUri("Obama"))
    q.setRequestedResult(RequestEventsConceptGraph(conceptCount = 200, linkCount = 500, eventsSampleSize = 2000))
    res = er.execQuery(q)
    print(er.format(res))
    # {
    #     "conceptGraph": {
    #         "usedResults": 26000,
    #         "totalResults": 341019,
    #         "concepts": [
    #             {"uri": "http://en.wikipedia.org/wiki/United_States", "type": "loc", "score": 1318.4, "label": {"eng": "United States"}, "location": {"type": "country", "label": {"eng": "United States"}}},
    #             {"uri": "http://en.wikipedia.org/wiki/Donald_Trump", "type": "person", "score": 1122.9, "label": {"eng": "Donald Trump"}},
    #             ...
    #         ],
    #         "links": [
    #             {"uri1": "http://en.wikipedia.org/wiki/United_States", "uri2": "http://en.wikipedia.org/wiki/Donald_Trump", "score": 812.5},
    #             {"uri1": "http://en.wikipedia.org/wiki/United_States", "uri2": "http://en.wikipedia.org/wiki/White_House", "score": 576.6},
    #             ...
    #         ]
    #     }
    # }


#
# COMPLEX QUERIES
# examples of complex queries that combine various OR and AND operators
#


def complexQueryWithNot(er):
    """
    a complex query, provided as a python dict, where a part of the results is excluded
    """
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
    print(er.format(res))


def complexQueryAsDict(er):
    """
    a complex query with a combination of the OR, AND and NOT operators, provided as a python dict
    """
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
    print(er.format(res))


def complexQueryIterator(er):
    """
    a complex query built with ComplexEventQuery, CombinedQuery and BaseQuery classes, used with an iterator
    """
    trumpUri = er.getConceptUri("Trump")
    obamaUri = er.getConceptUri("Obama")
    politicsUri = er.getCategoryUri("politics")

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
    q = QueryEventsIter.initWithComplexQuery(cq)
    for event in q.execQuery(er, returnInfo =  retInfo, maxItems = MAX_RESULTS):
        print(json.dumps(event, indent=2))


#
# use of EXACT search mode when using keywords
# NOTE: You don’t have to write AND, OR, NOT in uppercase — we will use uppercase just to make examples more readable.
#


def exactSearchModeAndOrNot(er):
    """
    exact keyword search mode: the AND, OR and NOT operators
    """
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
    q = QueryEventsIter.initWithComplexQuery(q)
    for ev in q.execQuery(er, maxItems = MAX_RESULTS):
        print(ev)


def exactSearchModeNear(er):
    """
    exact keyword search mode: the NEAR operator
    """
    # use of operator NEAR
    # find English events that mention siemens and sustainability or ecology or renewable energy, but at most 15 words apart (forward or backward)
    q = {
        "$query": {
            "keyword": "Siemens NEAR/15 (sustainability or ecology or renewable energy)",
            "keywordSearchMode": "exact",
            "lang": "eng"
        }
    }
    q = QueryEventsIter.initWithComplexQuery(q)
    for ev in q.execQuery(er, maxItems = MAX_RESULTS):
        print(ev)


def exactSearchModeNext(er):
    """
    exact keyword search mode: the NEXT operator
    """
    # use of operator NEXT
    # find English events that mention sustainability or ecology or renewable energy at most 15 words after siemens is mentioned
    q = {
        "$query": {
            "keyword": "Siemens NEXT/15 (sustainability or ecology or renewable energy)",
            "keywordSearchMode": "exact",
            "lang": "eng"
        }
    }
    q = QueryEventsIter.initWithComplexQuery(q)
    for ev in q.execQuery(er, maxItems = MAX_RESULTS):
        print(ev)


#
# use of SIMPLE search mode when using keywords
#


def simpleSearchMode(er):
    """
    simple keyword search mode - with the complex query language and without it
    """
    # find events that at least some of the specified keywords and phrases and that belong to the AI category
    q = {
        "$query": {
            "keyword": "AI \\\"deep learning\\\" \\\"machine learning\\\" latest developments",
            "keywordSearchMode": "simple",
            "categoryUri": "dmoz/Computers/Artificial_Intelligence"
        }
    }
    q = QueryEventsIter.initWithComplexQuery(q)
    for ev in q.execQuery(er, sortBy = "rel", maxItems = MAX_RESULTS):
        print(ev)

    # the same query, but without using the complex query language
    q = QueryEventsIter(keywords = "AI \\\"deep learning\\\" \\\"machine learning\\\" latest developments", keywordSearchMode="simple")
    for ev in q.execQuery(er, sortBy = "rel", maxItems = MAX_RESULTS):
        print(ev)


#
# use of PHRASE search mode when using keywords
# phrase search mode is used by default, so in this case, you don't even need to specify the "keywordSearchMode" parameter
#


def phraseSearchMode(er):
    """
    phrase keyword search mode (the default mode)
    """
    # search for events that mention the phrase "Apple iPhone" or "Microsoft Store"
    query = {
        "$query": {
            "$or": [
                { "keyword": "Apple iPhone" },
                { "keyword": "Microsoft Store" }
            ]
        }
    }
    q = QueryEventsIter.initWithComplexQuery(query)
    for ev in q.execQuery(er, maxItems = MAX_RESULTS):
        print(ev)


# the examples in this file, in the order in which they are run when "all" is used
EXAMPLES = [
    iterateOverEvents,
    eventsByConceptDateAndSource,
    eventsByKeywordsAndSourceLocation,
    eventsReportedBySource,
    eventsInCategory,
    conceptAggr,
    locAggr,
    timeAggr,
    conceptTrends,
    categoryAggr,
    keywordAggr,
    locTimeAggr,
    conceptMatrix,
    sourceAggr,
    dateMentionAggr,
    conceptGraph,
    complexQueryWithNot,
    complexQueryAsDict,
    complexQueryIterator,
    exactSearchModeAndOrNot,
    exactSearchModeNear,
    exactSearchModeNext,
    simpleSearchMode,
    phraseSearchMode,
]


def main():
    """
    run the examples that are named on the command line, for example:
        python QueryEventsExamples.py iterateOverEvents
    Use "all" to run all of them. Without arguments we only list the available examples and make no requests
    """
    examples = {example.__name__: example for example in EXAMPLES}
    names = list(examples) if sys.argv[1:] == ["all"] else sys.argv[1:]
    unknown = [name for name in names if name not in examples]
    if unknown or not names:
        if unknown:
            print("Unknown example(s): %s\n" % ", ".join(unknown))
        print("Usage: python %s <example> [<example> ...] | all\n\nAvailable examples:" % os.path.basename(__file__))
        for name, example in examples.items():
            print("  %-33s %s" % (name, (example.__doc__ or "").strip().split("\n")[0]))
        sys.exit(1 if unknown else 0)

    # the API key is read from the EVENTREGISTRY_API_KEY environment variable or from the settings.json file
    # (see README.md in this folder). The examples make real requests, which use the tokens of your account
    er = EventRegistry()
    for name in names:
        print("\n===== %s =====" % name)
        examples[name](er)


if __name__ == "__main__":
    main()
