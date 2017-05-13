"""
this is a simple script that makes a query to ER to get the feed of articles that were added
in the last minute (from the first to the last second of the minute).
Note: In order to get all the data you have to make the query each minute
"""

from eventregistry import *
import time, datetime

er = EventRegistry(logging = True)

recentQ = GetRecentArticles(er, returnInfo = ReturnInfo(ArticleInfoFlags(bodyLen = -1, concepts = True, categories = True)))

starttime = time.time()

while True:
    articleList = recentQ.getUpdates()
    print("=======\n%d articles were added since the last call" % len(articleList))

    # TODO: do here whatever you need to with the articleList
    for article in articleList:
        print("Added article %s: %s" % (article["uri"], article["title"].encode("ascii", "ignore")))

    # wait exactly a minute until next batch of new content is ready
    print("sleeping for 60 seconds...")
    time.sleep(60.0 - ((time.time() - starttime) % 60.0))