from eventregistry import *

er = EventRegistry()

# get the list of all breaking events
params = {
    "includeEventSocialScore": True,
    "includeEventLocation": True,
    "includeLocationGeoLocation": True
}

res = er.jsonRequest("/api-c/v1/event/getBreakingEvents", paramDict=params)
print(res)


q = QueryEvents(
    categoryUri="news/Business",
    lang="eng")
q.setRequestedResult(RequestEventsBreakingEvents())

res = er.execQuery(q)
print(res)
