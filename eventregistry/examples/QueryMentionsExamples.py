"""
examples that illustrate how to query for mentions using different search options
"""
import os
import sys

from eventregistry import (EventRegistry, QueryMentions, QueryMentionsIter, QueryItems, RequestMentionsTimeAggr,
                           RequestMentionsUriWgtList)


def mentionsByEventTypeAndIndustry(er):
    """
    find the mentions of an event type, related to the companies from a given industry, in a time period
    """
    # Find mentions of stock price change event types related to companies in the transportation industry that occured in April 2023.
    q = QueryMentionsIter(
        eventTypeUri = "et/business/stock-prices/stock-price",
        industryUri= "sectors/Transportation",
        dateStart = "2023-04-01",
        dateEnd = "2023-04-30"
    )
    # iterate over first 100 mentions. Increase maxItems or remove it completely to get more/all results
    for m in q.execQuery(er, sortBy = "date", maxItems = 100):
        print(m)


def mentionsByEventTypeAndIndustryComplexQuery(er):
    """
    the same search as in mentionsByEventTypeAndIndustry, written in the complex query language
    """
    # alternatively, the same query using the complex query language
    q = {
        "$query": {
            "eventTypeUri": "et/business/stock-prices/stock-price",
            "industryUri": "sectors/Transportation",
            "dateStart": "2023-04-01",
            "dateEnd": "2023-04-30"
        }
    }
    q = QueryMentionsIter.initWithComplexQuery(q)
    for m in q.execQuery(er, sortBy = "date", maxItems = 100):
        print(m)


def mentionsByEventTypeAndConcepts(er):
    """
    find the mentions of an event type that are related to any of the given companies
    """
    # Find mentions of event types related to products and services which are related to companies Microsoft, Open AI or Google.
    microsoftUri = er.getConceptUri("Microsoft")
    openaiUri = er.getConceptUri("OpenAI")
    googleUri = er.getConceptUri("Google")
    q = QueryMentionsIter(
        eventTypeUri = "et/business/products-services",
        conceptUri = QueryItems.OR([microsoftUri, openaiUri, googleUri])
    )
    # iterate over first 100 mentions. Increase maxItems or remove it completely to get more/all results
    for m in q.execQuery(er, sortBy = "date", maxItems = 100):
        print(m)


def mentionsByEventTypeAndConceptsComplexQuery(er):
    """
    the same search as in mentionsByEventTypeAndConcepts, written in the complex query language
    """
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
    q = QueryMentionsIter.initWithComplexQuery(q)
    for m in q.execQuery(er, sortBy = "date", maxItems = 100):
        print(m)


def mentionsTimeAggr(er):
    """
    get the time distribution of the mentions of an event type
    """
    # get time distribution of the events related to acquisitions and mergers
    q = QueryMentions(eventTypeUri="et/business/acquisitions-mergers")
    q.setRequestedResult(RequestMentionsTimeAggr())
    res = er.execQuery(q)
    for obj in res.get("timeAggr", {}).get("results", []):
        print("%s: %d" % (obj["date"], obj["count"]))


def mentionsUriList(er):
    """
    get the list of URIs of the mentions of an event type
    """
    # get 10.000 uris of mentions that are related to mergers and acquisitions
    q = QueryMentions(eventTypeUri="et/business/acquisitions-mergers")
    q.setRequestedResult(RequestMentionsUriWgtList())
    res = er.execQuery(q)
    uriList = er.getUriFromUriWgt(res.get("uriWgtList", {}).get("results", []))
    print("Retrieved %d uris" % len(uriList))


def mentionsOfEventType(er):
    """
    get the first page of the mentions of an event type
    """
    # get mentions related to labor issues and print first 100 of them
    q = QueryMentions(eventTypeUri="et/business/labor-issues")
    res = er.execQuery(q)
    for m in res.get("mentions", {}).get("results", []):
        print(m)


# the examples in this file, in the order in which they are run when "all" is used
EXAMPLES = [
    mentionsByEventTypeAndIndustry,
    mentionsByEventTypeAndIndustryComplexQuery,
    mentionsByEventTypeAndConcepts,
    mentionsByEventTypeAndConceptsComplexQuery,
    mentionsTimeAggr,
    mentionsUriList,
    mentionsOfEventType,
]


def main():
    """
    run the examples that are named on the command line, for example:
        python QueryMentionsExamples.py mentionsByEventTypeAndIndustry
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
            print("  %-42s %s" % (name, (example.__doc__ or "").strip().split("\n")[0]))
        sys.exit(1 if unknown else 0)

    # the API key is read from the EVENTREGISTRY_API_KEY environment variable or from the settings.json file
    # (see README.md in this folder). The examples make real requests, which use the tokens of your account
    er = EventRegistry()
    for name in names:
        print("\n===== %s =====" % name)
        examples[name](er)


if __name__ == "__main__":
    main()
