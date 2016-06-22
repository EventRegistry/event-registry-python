"""
this is a simple script that makes a query to ER to get the feed of events that were added or 
updated since the last query. For the received set of events it prints the basic event info
and then goes and also downloads the top 20 articles assigned to this event in any of the 
core languages (eng, deu, spa, zho, slv)
"""

from eventregistry import *
import time

er = EventRegistry("http://eventregistry.org", verboseOutput = True)

recentQ = GetRecentEvents(maxEventCount = 200)

while True:
    ret = recentQ.getUpdates(er)
    if ret.has_key("eventInfo") and isinstance(ret["eventInfo"], dict):
        print "==========\n%d events updated since last call" % len(ret["eventInfo"])
        
        # get the list of event URIs, sorted from the most recently changed backwards
        activity = ret["activity"]
        # for each updated event print the URI and the title
        # NOTE: the same event can appear multiple times in the activity array - this means that more than one article
        # about it was recently written about it
        for eventUri in activity:
            event = ret["eventInfo"][eventUri]
            print u"Event %s ('%s') was changed" % (eventUri, event["title"][event["title"].keys()[0]].encode("ascii", "ignore"))
    
    # wait a bit for new content to be added to Event Registry
    print "sleeping for 20 seconds..."
    time.sleep(20)

