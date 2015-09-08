"""
this is a simple script that makes a query to ER to get the feed of events that were added or 
updated since the last query. For the received set of events it prints the basic event info
and then goes and also downloads the top 20 articles assigned to this event in any of the 
core languages (eng, deu, spa, zho, slv)
"""

from eventregistry import *
import time

er = EventRegistry("http://beta.eventregistry.org", verboseOutput = True)

recentQ = GetRecentEvents(maxEventCount = 200)

while True:
    ret = recentQ.getUpdates(er)
    if ret.has_key("eventInfo") and isinstance(ret["eventInfo"], dict):
        print "%d events updated since last call" % len(ret["activity"])
        
        # get URIs of the events that are new/updated
        uris = ret["eventInfo"].keys()
        
        
        size = 50
        for i in range(0, len(uris), size):
            uriChunk = uris[i:i+size]
            q = QueryEvent(uriChunk)
            # get the list of articles assigned to event
            q.addRequestedResult(RequestEventArticles(
                returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 0, title = False))))
            eventRet = er.execQuery(q)
            if eventRet != None and isinstance(eventRet, dict):
                print "obtained details about %d events" % len(eventRet)
            else:
                print "failed to obtain event information"
    time.sleep(20)
