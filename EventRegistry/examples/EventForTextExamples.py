from eventregistry import *

er = EventRegistry()

q = GetEventForText(er)
res = q.compute("Croatian leaders put the army on alert after chaos erupted on the border with Serbia, where thousands of asylum-seekers poured into the country. It is understood all traffic has been banned on roads heading towards seven crossings into Serbia. Some were trampling each other in a rush to get on the few available buses and trains, and dozens were injured in the mayhem.")

print("Most similar info:\n" + er.format(res))
if res != None and len(res) > 0:
    eventUris = [info["eventUri"] for info in res]
    q = QueryEvent(eventUris)
    q.addRequestedResult(RequestEventInfo())
    res = er.execQuery(q)
    print("Event info:\n" + er.format(res))