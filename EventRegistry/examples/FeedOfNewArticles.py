"""
this is a simple script that makes a query to ER to get the feed of articles that were added
since the last query.
"""

from eventregistry import *
import json, time, datetime

er = EventRegistry()

lastArticleActivityId = 0
while True:
    print "last activity id: ", lastArticleActivityId
    ret = er.getRecentArticles(200, lastActivityId = lastArticleActivityId)
    if ret != None and ret.has_key("recentActivity") and ret["recentActivity"].has_key("articles") and ret["recentActivity"]["articles"].has_key("activity") and isinstance(ret["recentActivity"]["articles"]["activity"], list):
        # update the last activity id (used for the next request)
        lastArticleActivityId = ret["recentActivity"]["articles"].get("lastActivityId", 0)

        articleList = ret["recentActivity"]["articles"]["activity"]
        print "%d articles were added since the last call" % len(articleList)
        
        # do whatever you need to with the articleList

        
    time.sleep(20)     