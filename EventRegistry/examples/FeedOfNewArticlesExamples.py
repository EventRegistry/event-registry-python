"""
this is a simple script that makes a query to ER to get the feed of articles that were added
since the last query.
"""

from eventregistry import *
import time

er = EventRegistry()

recentQ = GetRecentArticles(maxArticleCount = 200)

while True:
    articleList = recentQ.getUpdates(er)
    print("=======\n%d articles were added since the last call" % len(articleList))

    # do whatever you need to with the articleList
    for article in articleList:
        print("Added article %s: %s" % (article["uri"], article["title"].encode("ascii", "ignore")))

    # wait a bit for new content to be added to Event Registry
    print("sleeping for 20 seconds...")
    time.sleep(20)