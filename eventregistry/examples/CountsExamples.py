"""
examples showing how to obtain information how frequently a particular concept is mentioined in
the news articles, or an article is about a particular category
"""
import os
import sys

from eventregistry import EventRegistry, GetCounts, GetCountsEx


def conceptMentionCounts(er):
    """
    get the number of articles that mention the given concepts on each day
    """
    trumpUri = er.getConceptUri("Trump")
    ebolaUri = er.getConceptUri("ebola")

    q = GetCounts([trumpUri, ebolaUri])
    ret = er.execQuery(q)
    print(er.format(ret))
    # example of the returned output (shortened) - for each provided uri you get the number of mentioning
    # articles per day. Note that days that are older than the date range covered by your subscription plan
    # will be reported with a count of 0
    # {
    #     "http://en.wikipedia.org/wiki/Donald_Trump": [
    #         {"date": "2026-07-31", "count": 26598},
    #         {"date": "2026-08-01", "count": 17940},
    #         ...
    #         {"date": "2026-09-01", "count": 8825}
    #     ],
    #     "http://en.wikipedia.org/wiki/Ebola": [
    #         {"date": "2026-07-31", "count": 343},
    #         {"date": "2026-08-01", "count": 486},
    #         ...
    #         {"date": "2026-09-01", "count": 65}
    #     ]
    # }


def categoryCountsWithDetails(er):
    """
    get the daily number of articles in a category, together with the details about the category
    """
    q = GetCountsEx([er.getCategoryUri("business")], type="category")
    ret = er.execQuery(q)
    print(er.format(ret))
    # example of the returned output (shortened) - the details of the provided uris are listed in
    # "categoryInfo" and each item in "counts" contains the number of matching articles per day for each uri
    # {
    #     "categoryInfo": [
    #         {"uri": "dmoz/Business", "label": "dmoz/Business"}
    #     ],
    #     "counts": [
    #         {"date": "2026-07-31", "dmoz/Business": 1564},
    #         {"date": "2026-08-01", "dmoz/Business": 626},
    #         ...
    #     ]
    # }


# the examples in this file, in the order in which they are run when "all" is used
EXAMPLES = [
    conceptMentionCounts,
    categoryCountsWithDetails,
]


def main():
    """
    run the examples that are named on the command line, for example:
        python CountsExamples.py conceptMentionCounts
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
            print("  %-25s %s" % (name, (example.__doc__ or "").strip().split("\n")[0]))
        sys.exit(1 if unknown else 0)

    # the API key is read from the EVENTREGISTRY_API_KEY environment variable or from the settings.json file
    # (see README.md in this folder). The examples make real requests, which use the tokens of your account
    er = EventRegistry()
    for name in names:
        print("\n===== %s =====" % name)
        examples[name](er)


if __name__ == "__main__":
    main()
