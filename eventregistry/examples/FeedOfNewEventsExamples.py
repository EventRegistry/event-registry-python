"""
this is a simple script that makes a query to ER to get the feed of events that were added or
updated in the last minute.

For the received set of events, the script prints the basic event info and then goes and
also downloads the top 20 articles assigned to this event in any of the languages
"""

from eventregistry import *
import time

er = EventRegistry()

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

