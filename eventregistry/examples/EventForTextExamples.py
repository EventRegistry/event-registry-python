"""
given some text that is related to some current event, this example demonstrates how to obtain
information which event is the text talking about
"""

from eventregistry import *

er = EventRegistry()

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