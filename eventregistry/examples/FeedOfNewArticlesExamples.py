from eventregistry import *
import time, datetime

er = EventRegistry(logging = True)

#
# use the code below to obtain from ER the full minute by minute stream of articles added to the system
# (from the first to the last second of the minute).
# Note: In order to get all the data you have to make the query each minute
#

recentQ = GetRecentArticles(er, returnInfo = ReturnInfo(ArticleInfoFlags(bodyLen = -1, concepts = True, categories = True)), recentActivityArticlesMaxArticleCount = 300)
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


#
# if you would like to obtain the list of articles recently added, but not necessarily the full feed of articles
# then use the call as below. In this case you can filter the articles to a subset based on
# keywords, concepts, categories, language, source, etc.
# You can also request more than 100 articles per call.
#

starttime = time.time()
while True:
    q = QueryArticles(
        keywords="Trump",
        sourceLocationUri=er.getLocationUri("United States"))
    q.setRequestedResult(
        RequestArticlesRecentActivity(
            # download at most 2000 articles. if less of matching articles were added in last 10 minutes, less will be returned
            maxArticleCount=2000,
            # consider articles that were published at most 10 minutes ago
            updatesAfterMinsAgo = 10
        ))

    res = er.execQuery(q)
    for article in res.get("recentActivityArticles", {}).get("activity", []):
        print("Added article %s: %s" % (article["uri"], article["title"].encode("ascii", "ignore")))


    # wait exactly a minute until next batch of new content is ready
    print("sleeping for 10 minutes...")
    time.sleep(10 * 60.0 - ((time.time() - starttime) % 60.0))



#
# similar example but uses the updatesAfterTm parameter value provided in the previous calls
#
starttime = time.time()
updatesAfterTm = None
while True:
    # q = QueryArticles(keywords="strike", keywordsLoc="title")
    q = QueryArticles(keywords="Trump")
    q.setRequestedResult(
        RequestArticlesRecentActivity(
            # download at most 2000 articles. if less of matching articles were added in last 10 minutes, less will be returned
            maxArticleCount=100,
            # specify the last time that was used when making the request - only articles added after that will be potentially returned
            updatesAfterTm = updatesAfterTm
        ))

    res = er.execQuery(q)
    for article in res.get("recentActivityArticles", {}).get("activity", []):
        print("Added article %s: %s" % (article["uri"], article["title"]))


    # wait for some time - the next request will return results published after the last request
    print("sleeping for 10 minutes...")
    time.sleep(10 * 60.0)
    updatesAfterTm = res["recentActivityArticles"]["currTime"]