from eventregistry import *
import time

er = EventRegistry()

#
# this is a simple script that makes a query to ER to get the feed of events that were added or
# updated in the last minute.
# The script has to be called exactly once a minute to get all updated events
#

recentQ = GetRecentEvents(er)
starttime = time.time()
while True:
    ret = recentQ.getUpdates()
    if "eventInfo" in ret and isinstance(ret["eventInfo"], dict):
        print("==========\n%d events updated since last call" % len(ret["eventInfo"]))

        # get the list of event URIs, sorted from the most recently changed backwards
        activity = ret["activity"]
        # for each updated event print the URI and the title
        # NOTE: the same event can appear multiple times in the activity array - this means that more than one article
        # about it was recently written about it
        for eventUri in activity:
            event = ret["eventInfo"][eventUri]
            print("Event %s ('%s') was changed" % (eventUri, event["title"][list(event["title"].keys())[0]].encode("ascii", "ignore")))
            # event["concepts"] contains the list of relevant concepts for the event
            # event["categories"] contains the list of categories for the event

            #
            # TODO: here you can do the processing that decides if the event is relevant for you or not. if relevant, send the info to an external service

    # wait exactly a minute until next batch of new content is ready
    print("sleeping for 60 seconds...")
    time.sleep(60.0 - ((time.time() - starttime) % 60.0))



#
# Alternatively you can also ask for a feed of added/updated events, but instead of all of them, just
# obtain a subset of events that match certain conditions. The full stream of events can be filtered to
# a subset that matches certain keyword, concept, location, source or other available filters in QueryEvents
#


starttime = time.time()
while True:
    q = QueryEvents(
        keywords = "Apple",
        minArticlesInEvent = 30,
        sourceLocationUri = er.getLocationUri("United States"))
    q.setRequestedResult(
        RequestEventsRecentActivity(
            # download at most 2000 events. if less of matching events were added/updated in last 10 minutes, less will be returned
            maxEventCount=2000,
            # consider articles that were published at most 10 minutes ago
            updatesAfterMinsAgo = 10
        ))

    ret = er.execQuery(q)
    activity = ret.get("recentActivityEvents", {}).get("activity", [])
    eventInfoObj = ret.get("recentActivityEvents", {}).get("eventInfo", {})
    for eventUri in activity:
        event = eventInfoObj[eventUri]
        print("Event %s ('%s') was changed" % (eventUri, event["title"][list(event["title"].keys())[0]].encode("ascii", "ignore")))
        # event["concepts"] contains the list of relevant concepts for the event
        # event["categories"] contains the list of categories for the event

        #
        # TODO: here you can do the processing that decides if the event is relevant for you or not. if relevant, send the info to an external service


    # wait exactly a minute until next batch of new content is ready
    print("sleeping for 10 minutes...")
    time.sleep(10 * 60.0 - ((time.time() - starttime) % 60.0))