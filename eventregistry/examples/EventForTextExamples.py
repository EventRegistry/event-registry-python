"""
given some text that is related to some current event, this example demonstrates how to obtain
information which event is the text talking about
"""
import os
import sys

from eventregistry import EventRegistry, GetEventForText, QueryEvent, RequestEventInfo


def eventForText(er):
    """
    find the events that are the most related to the given text and get the details about them
    """
    q = GetEventForText(er)
    res = q.compute("Croatian leaders put the army on alert after chaos erupted on the border with Serbia, where thousands of asylum-seekers poured into the country. It is understood all traffic has been banned on roads heading towards seven crossings into Serbia. Some were trampling each other in a rush to get on the few available buses and trains, and dozens were injured in the mayhem.")

    print("Most similar info:\n" + er.format(res))
    if res != None and len(res) > 0:
        # get the events ids that are most related to the given text
        eventUris = [info["eventUri"] for info in res]
        # obtain information about those events
        q = QueryEvent(eventUris)
        q.setRequestedResult(RequestEventInfo())
        res = er.execQuery(q)
        print("Event info:\n" + er.format(res))


# the examples in this file, in the order in which they are run when "all" is used
EXAMPLES = [
    eventForText,
]


def main():
    """
    run the examples that are named on the command line, for example:
        python EventForTextExamples.py eventForText
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
            print("  %-12s %s" % (name, (example.__doc__ or "").strip().split("\n")[0]))
        sys.exit(1 if unknown else 0)

    # the API key is read from the EVENTREGISTRY_API_KEY environment variable or from the settings.json file
    # (see README.md in this folder). The examples make real requests, which use the tokens of your account
    er = EventRegistry()
    for name in names:
        print("\n===== %s =====" % name)
        examples[name](er)


if __name__ == "__main__":
    main()
