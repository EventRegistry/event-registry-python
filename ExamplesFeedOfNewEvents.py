"""
this is a simple script that makes a query to ER to get the feed of events that were added or 
updated since the last query. For the received set of events it prints the basic event info
and then goes and also downloads the top 20 articles assigned to this event in any of the 
core languages (eng, deu, spa, zho, slv)
"""
from EventRegistry import *
import json, time, datetime

er = EventRegistry(host = "http://eventregistry.org", logging = True)
lastEventActivityId = 0;
while True:
    print "last activity id: ", lastEventActivityId
    ret = er.getRecentEvents(200, lastActivityId = lastEventActivityId)
    if ret != None and ret.has_key("recentActivity") and ret["recentActivity"].has_key("events") and ret["recentActivity"]["events"].has_key("eventInfo") and isinstance(ret["recentActivity"]["events"]["eventInfo"], dict):
        print "%d events updated since last call" % len(ret["recentActivity"]["events"]["activity"])
        uris = [uri for uri in ret["recentActivity"]["events"]["eventInfo"]]
        size = 50
        for i in range(0, len(uris), size):
            uriChunk = uris[i:i+size]
            q = QueryEvent(uriChunk);
            # get the list of articles assigned to event
            q.addRequestedResult(RequestEventArticles(includeArticleBody = False, includeArticleTitle = False));
            eventRet = er.execQuery(q);
            if eventRet != None and isinstance(eventRet, dict):
                print "obtained details about %d events" % len(eventRet)
            else:
                print "failed to obtain event information"
        lastEventActivityId = ret["recentActivity"]["events"]["lastActivityId"];
    time.sleep(20);
