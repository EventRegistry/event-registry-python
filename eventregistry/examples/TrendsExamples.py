"""
examples that illustrate how to obtain the currently top trending concepts or categories
The trends can be computed based on the number of mentions in the news or based on the shares on social media
"""
import os
import sys

from eventregistry import (EventRegistry, GetTrendingConcepts, GetTrendingConceptGroups, GetTrendingCategories,
                           ReturnInfo, ConceptInfoFlags, CategoryInfoFlags)


def trendingConcepts(er):
    """
    get the top 10 trending concepts in the news
    """
    # top 10 top trending concepts in the news
    q = GetTrendingConcepts(source = "news", count = 10,
        returnInfo = ReturnInfo(
            conceptInfo = ConceptInfoFlags(includeConceptTrendingHistory = True)))
    ret = er.execQuery(q)
    print(er.format(ret))
    # example of the returned output (shortened). "trendingHistory.news" contains the number of mentions
    # of the concept in the news for each of the last days
    # [
    #     {
    #         "uri": "http://en.wikipedia.org/wiki/Grand_Canyon_Village,_Arizona",
    #         "type": "loc",
    #         "label": {"eng": "Grand Canyon Village, Arizona"},
    #         "trendingScore": {"news": {"score": 446.65, "testPopFq": 552, "nullPopFq": 14}},
    #         "trendingHistory": {"latestArticleTimestamp": "2026-09-01T08:35:46", "news": [2, 1, ...]},
    #         "location": {"type": "place", "label": {"eng": "Grand Canyon Village, Arizona"}, "country": {"type": "country", "label": {"eng": "United States"}}}
    #     },
    #     {
    #         "uri": "http://en.wikipedia.org/wiki/Paul_Goldstein_(tennis)",
    #         "type": "person",
    #         "label": {"eng": "Paul Goldstein (tennis)"},
    #         "trendingScore": {"news": {"score": 403.12, "testPopFq": 266, "nullPopFq": 4}},
    #         "trendingHistory": {"latestArticleTimestamp": "2026-09-01T08:35:46", "news": [1, 0, ...]}
    #     },
    #     ...
    # ]


def trendingConceptGroups(er):
    """
    get the most trending concepts for each entity type (people, locations, organizations)
    """
    # get 20 most trending concept for each entity type
    q = GetTrendingConceptGroups(source = "news")
    # get top trends for individual concept groups - people, locations and organizations
    q.getConceptTypeGroups()
    ret = er.execQuery(q)
    print(er.format(ret))
    # example of the returned output (shortened) - a dict with one key per entity type:
    # {
    #     "person": {
    #         "label": "Person",
    #         "type": "person",
    #         "trendingConcepts": [
    #             {"uri": "http://en.wikipedia.org/wiki/Paul_Goldstein_(tennis)", "type": "person", "label": {"eng": "Paul Goldstein (tennis)"}, "trendingScore": {"news": {"score": 404.13, "testPopFq": 265, "nullPopFq": 4}}},
    #             ...
    #         ]
    #     },
    #     "org": {
    #         "label": "Organization",
    #         "type": "org",
    #         "trendingConcepts": [
    #             {"uri": "http://en.wikipedia.org/wiki/Invest_in_Canada", "type": "org", "label": {"eng": "Invest in Canada"}, "trendingScore": {"news": {"score": 152.91, "testPopFq": 71, "nullPopFq": 2}}},
    #             ...
    #         ]
    #     },
    #     "loc": {
    #         "label": "Location",
    #         "type": "loc",
    #         "trendingConcepts": [
    #             {"uri": "http://en.wikipedia.org/wiki/Grand_Canyon_Village,_Arizona", "type": "loc", "label": {"eng": "Grand Canyon Village, Arizona"}, "trendingScore": {"news": {"score": 448.66, "testPopFq": 551, "nullPopFq": 14}}, "location": {...}},
    #             ...
    #         ]
    #     }
    # }


def trendingConceptsInSocialMedia(er):
    """
    get the top 20 trending concepts in the social media
    """
    # top 20 trending concepts in the social media
    q = GetTrendingConcepts(source = "social", count = 20,
        returnInfo = ReturnInfo(
            conceptInfo = ConceptInfoFlags(includeConceptTrendingHistory = True)))
    ret = er.execQuery(q)
    print(er.format(ret))
    # NOTE: social media trends are currently not computed, so the call returns an error:
    # {
    #     "error": "Trends with the given parameters were not computed."
    # }
    # when available, the structure of the results is the same as for the "news" source above


def trendingCategories(er):
    """
    get the top 10 trending categories in the news
    """
    # top 10 trending categories in the news
    q = GetTrendingCategories(source = "news", count = 10,
        returnInfo = ReturnInfo(
            categoryInfo = CategoryInfoFlags(includeCategoryParentUri = True, includeCategoryChildrenUris = True, includeCategoryTrendingHistory = True)))
    ret = er.execQuery(q)
    print(er.format(ret))
    # example of the returned output (shortened):
    # [
    #     {"uri": "dmoz/Sports/Soccer/CONMEBOL", "label": "dmoz/Sports/Soccer/CONMEBOL", "trendingScore": {"news": {"score": 112.81, "testPopFq": 595, "nullPopFq": 238}}},
    #     {"uri": "dmoz/Arts/Graphic_Design/Graphic_Designers", "label": "dmoz/Arts/Graphic Design/Graphic Designers", "trendingScore": {"news": {"score": 76.7, "testPopFq": 355, "nullPopFq": 179}}},
    #     ...
    # ]


# the examples in this file, in the order in which they are run when "all" is used
EXAMPLES = [
    trendingConcepts,
    trendingConceptGroups,
    trendingConceptsInSocialMedia,
    trendingCategories,
]


def main():
    """
    run the examples that are named on the command line, for example:
        python TrendsExamples.py trendingConcepts
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
            print("  %-29s %s" % (name, (example.__doc__ or "").strip().split("\n")[0]))
        sys.exit(1 if unknown else 0)

    # the API key is read from the EVENTREGISTRY_API_KEY environment variable or from the settings.json file
    # (see README.md in this folder). The examples make real requests, which use the tokens of your account
    er = EventRegistry()
    for name in names:
        print("\n===== %s =====" % name)
        examples[name](er)


if __name__ == "__main__":
    main()
