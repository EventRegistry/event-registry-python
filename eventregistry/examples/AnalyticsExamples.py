"""
Examples of usage of the analytics endpoints
"""
import os
import sys

from eventregistry import EventRegistry, Analytics


def sentimentOfText(er):
    """
    compute the sentiment of the given text - of the whole text and of the individual sentences
    """
    analytics = Analytics(er)
    res = analytics.sentiment("""
    Residents and tourists enjoy holiday weekend even as waves start to pound; beaches remain closed due to dangerous rip currents.
    Despite a state of emergency declared by the governor and warnings about dangerous surf and the possibility of significant coastal flooding, residents and visitors to the Jersey Shore spent Saturday making the most of the calm before the storm.
    Cloudy skies in the morning gave way to sunshine in the afternoon, and despite winds that already were kicking up sand and carving the beach, people flocked to the boardwalk in both Seaside Heights and Point Pleasant Beach, where children rode amusement rides and teens enjoyed ice cream cones.
""")

    print(f"Average sentiment: {res['avgSent']}")
    for text, sent in zip(res["sentences"], res["sentimentPerSent"]):
        print(f"Sentence: '{text}' has sentiment {sent}")


# the examples in this file, in the order in which they are run when "all" is used
EXAMPLES = [
    sentimentOfText,
]


def main():
    """
    run the examples that are named on the command line, for example:
        python AnalyticsExamples.py sentimentOfText
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
            print("  %-15s %s" % (name, (example.__doc__ or "").strip().split("\n")[0]))
        sys.exit(1 if unknown else 0)

    # the API key is read from the EVENTREGISTRY_API_KEY environment variable or from the settings.json file
    # (see README.md in this folder). The examples make real requests, which use the tokens of your account
    er = EventRegistry()
    for name in names:
        print("\n===== %s =====" % name)
        examples[name](er)


if __name__ == "__main__":
    main()
