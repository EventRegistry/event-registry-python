"""
examples showing how to obtain the list of currently breaking events
"""
import os
import sys

from eventregistry import EventRegistry, QueryEvents, RequestEventsBreakingEvents


def allBreakingEvents(er):
    """
    get the list of all currently breaking events by calling the API endpoint directly
    """
    # get the list of all breaking events
    params = {
        "includeEventSocialScore": True,
        "includeEventLocation": True,
        "includeLocationGeoLocation": True
    }

    res = er.jsonRequest("/api-c/v1/event/getBreakingEvents", paramDict=params)
    print(res)
    # example of the returned output (shortened):
    # {
    #     "breakingEvents": {
    #         "results": [
    #             {
    #                 "uri": "eng-11966764",
    #                 "eventDate": "2026-08-31",
    #                 "totalArticleCount": 314,
    #                 "articleCounts": {"eng": 314},
    #                 "title": {"eng": "At the Tupac Trial, Old Rumors Still Trail Sean Combs"},
    #                 "summary": {"eng": "Duane Davis, who is charged in the murder of the rapper Tupac Shakur, repeatedly accused ..."},
    #                 "concepts": [
    #                     {"uri": "http://en.wikipedia.org/wiki/Tupac_Shakur", "type": "person", "score": 100, "label": {"eng": "Tupac Shakur"}},
    #                     {"uri": "http://en.wikipedia.org/wiki/Murder", "type": "wiki", "score": 88, "label": {"eng": "Murder"}},
    #                     ...
    #                 ],
    #                 "categories": [
    #                     {"uri": "dmoz/Society/Crime/Murder", "label": "dmoz/Society/Crime/Murder", "wgt": 25},
    #                     ...
    #                 ],
    #                 "location": {"type": "place", "label": {"eng": "Las Vegas"}, "lat": 36.17, "long": -115.14, "country": {"type": "country", "label": {"eng": "United States"}, "lat": 39.76, "long": -98.5}},
    #                 "socialScore": 0,
    #                 "sentiment": -0.4,
    #                 "breakingScore": 2.29
    #             },
    #             ...
    #         ]
    #     }
    # }


def breakingEventsMatchingQuery(er):
    """
    get the breaking events that match a search query (business events in English)
    """
    q = QueryEvents(
        categoryUri="news/Business",
        lang="eng")
    q.setRequestedResult(RequestEventsBreakingEvents())

    res = er.execQuery(q)
    print(res)
    # the returned events have the same structure as in the example above, this time under the "breakingEvents" key
    # of the standard execQuery result. Example (shortened):
    # {
    #     "breakingEvents": {
    #         "results": [
    #             {
    #                 "uri": "eng-11970620",
    #                 "eventDate": "2026-09-01",
    #                 "totalArticleCount": 20,
    #                 "articleCounts": {"eng": 20},
    #                 "title": {"eng": "Investors gear up for new GoG 4-year bond"},
    #                 "summary": {"eng": "Ghana's financial portfolio investment community - and their counterparts abroad ..."},
    #                 "concepts": [{"uri": "http://en.wikipedia.org/wiki/Stock", "type": "wiki", "score": 100, "label": {"eng": "Stock"}}, ...],
    #                 "categories": [{"uri": "dmoz/Business/Investing/Stocks_and_Bonds", "label": "dmoz/Business/Investing/Stocks and Bonds", "wgt": 19}, ...],
    #                 "location": {"type": "place", "label": {"eng": "Seoul"}, "country": {"type": "country", "label": {"eng": "South Korea"}}},
    #                 "sentiment": 0.06,
    #                 "breakingScore": 1.09
    #             },
    #             ...
    #         ]
    #     }
    # }


# the examples in this file, in the order in which they are run when "all" is used
EXAMPLES = [
    allBreakingEvents,
    breakingEventsMatchingQuery,
]


def main():
    """
    run the examples that are named on the command line, for example:
        python BreakingEvents.py allBreakingEvents
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
            print("  %-27s %s" % (name, (example.__doc__ or "").strip().split("\n")[0]))
        sys.exit(1 if unknown else 0)

    # the API key is read from the EVENTREGISTRY_API_KEY environment variable or from the settings.json file
    # (see README.md in this folder). The examples make real requests, which use the tokens of your account
    er = EventRegistry()
    for name in names:
        print("\n===== %s =====" % name)
        examples[name](er)


if __name__ == "__main__":
    main()
