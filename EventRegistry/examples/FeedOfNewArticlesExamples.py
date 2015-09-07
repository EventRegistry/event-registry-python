"""
this is a simple script that makes a query to ER to get the feed of articles that were added
since the last query.
"""

from eventregistry import *
import time

#er = EventRegistry()
er = EventRegistry("http://beta.eventregistry.org", verboseOutput = True)

recentQ = GetRecentArticles(maxArticleCount = 200)

while True:
    articleList = recentQ.getUpdates(er)
    print "%d articles were added since the last call" % len(articleList)
    
    # do whatever you need to with the articleList        
    time.sleep(20)     