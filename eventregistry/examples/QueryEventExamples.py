"""
examples that show how to obtain information about an individual event
"""
import os
import sys

from eventregistry import (EventRegistry, QueryEvent, QueryEventArticlesIter, RequestEventInfo, RequestEventArticles,
                           RequestEventArticleTrend, RequestEventKeywordAggr, RequestEventSourceAggr,
                           RequestEventSimilarEvents, ReturnInfo, ConceptInfoFlags)

#
# NOTE: if you don't have access to historical data, you have to change the event URI
# to some recent event that you can access in order to run the examples
#
EVENT_URI = "eng-2940883"


def eventArticles(er):
    """
    iterate over all articles that belong to the event
    """
    # iterate over all articles that belong to a particular event with a given URI
    q = QueryEventArticlesIter(EVENT_URI)
    for art in q.execQuery(er):
        print(art)


def eventArticlesWithKeywordInTitle(er):
    """
    iterate over the articles in the event that mention a keyword in the title
    """
    # iterate over the articles in the event, but only return those that mention Obama in the title
    q = QueryEventArticlesIter(EVENT_URI,
        keywords = "Obama",
        keywordsLoc = "title")
    for art in q.execQuery(er):
        print(art)


def eventArticlesInLanguages(er):
    """
    iterate over the articles in the event that are in the selected languages
    """
    # iterate over the articles in the event, but only select those that are in English or German language
    q = QueryEventArticlesIter(EVENT_URI,
        lang = ["eng", "deu"])
    for art in q.execQuery(er):
        print(art)


def eventArticlesFromSourceLocation(er):
    """
    iterate over the articles in the event that were published by sources from a given country
    """
    # iterate over the articles in the event, but only select those that are from sources located in United States
    q = QueryEventArticlesIter(EVENT_URI,
        sourceLocationUri = er.getLocationUri("United States"))
    for art in q.execQuery(er):
        print(art)


def eventInfo(er):
    """
    get the details about the event (title, summary, concepts, location, date, ...)
    """
    # get event info (title, summary, concepts, location, date, ...) about event with a particular uri
    q = QueryEvent(EVENT_URI)
    q.setRequestedResult(RequestEventInfo(
        returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(lang = ["eng", "spa", "slv"]))))
    eventRes = er.execQuery(q)
    print(er.format(eventRes))


def eventArticleList(er):
    """
    get a list of 10 articles about the event
    """
    q = QueryEvent(EVENT_URI)
    # get list of 10 articles about the event
    q.setRequestedResult(RequestEventArticles(page = 1, count = 10))        # get 10 articles about the event (any language is ok) that are closest to the center of the event
    eventRes = er.execQuery(q)
    print(er.format(eventRes))


def eventArticleTrend(er):
    """
    get how the reporting about the event was trending over time
    """
    q = QueryEvent(EVENT_URI)
    # get information about how reporting about the event was trending over time
    q.setRequestedResult(RequestEventArticleTrend())
    eventRes = er.execQuery(q)
    print(er.format(eventRes))


def eventKeywordAggr(er):
    """
    get the tag cloud of the top words for the event
    """
    q = QueryEvent(EVENT_URI)
    # get the tag cloud of top words for the event
    q.setRequestedResult(RequestEventKeywordAggr())
    eventRes = er.execQuery(q)
    print(er.format(eventRes))


def eventSourceAggr(er):
    """
    get the news sources that reported about the event
    """
    q = QueryEvent(EVENT_URI)
    # get information about the news sources that reported about the event
    q.setRequestedResult(RequestEventSourceAggr())
    eventRes = er.execQuery(q)
    print(er.format(eventRes))


def similarEvents(er):
    """
    get the events that are similar to the given list of weighted concepts
    """
    q = QueryEvent(EVENT_URI)
    # return the events that are the most similar to the provided list of concepts and their weights
    q.setRequestedResult(RequestEventSimilarEvents(
        conceptInfoList=[
            {"uri": er.getConceptUri("Trump"), "wgt": 100},
            {"uri": er.getConceptUri("Obama"), "wgt": 100},
            {"uri": er.getConceptUri("Richard Nixon"), "wgt": 30},
            {"uri": er.getConceptUri("republican party"), "wgt": 30},
            {"uri": er.getConceptUri("democrat party"), "wgt": 30}
        ]
    ))
    eventRes = er.execQuery(q)
    print(er.format(eventRes))


# the examples in this file, in the order in which they are run when "all" is used
EXAMPLES = [
    eventArticles,
    eventArticlesWithKeywordInTitle,
    eventArticlesInLanguages,
    eventArticlesFromSourceLocation,
    eventInfo,
    eventArticleList,
    eventArticleTrend,
    eventKeywordAggr,
    eventSourceAggr,
    similarEvents,
]


def main():
    """
    run the examples that are named on the command line, for example:
        python QueryEventExamples.py eventArticles
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
            print("  %-31s %s" % (name, (example.__doc__ or "").strip().split("\n")[0]))
        sys.exit(1 if unknown else 0)

    # the API key is read from the EVENTREGISTRY_API_KEY environment variable or from the settings.json file
    # (see README.md in this folder). The examples make real requests, which use the tokens of your account
    er = EventRegistry()
    for name in names:
        print("\n===== %s =====" % name)
        examples[name](er)


if __name__ == "__main__":
    main()
