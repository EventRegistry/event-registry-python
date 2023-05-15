from eventregistry import *
import time, datetime

er = EventRegistry()

#
# use the code below to obtain from ER the full minute by minute stream of articles added to the system
#


recentQ = GetRecentArticles(er, returnInfo = ReturnInfo(ArticleInfoFlags(bodyLen = -1, concepts = True, categories = True)), recentActivityArticlesMaxArticleCount = 300)
starttime = time.time()
# while True:
for i in range(10):
    articleList = recentQ.getUpdates()
    print("=======\n%d articles were added since the last call" % len(articleList))

    # TODO: do here whatever you need to with the articleList
    for article in articleList:
        print("Added article %s: %s" % (article["uri"], article["title"]))
    print("Received %d articles" % len(articleList))

    # wait a minute until next batch of new content is ready
    # you can also sleep for longer, but if more than recentActivityArticlesMaxArticleCount articles are collected in that time,
    # you will only receive the number specified by recentActivityArticlesMaxArticleCount parameter (by default 100)
    print("sleeping for 60 seconds...")
    time.sleep(60.0)


#
# if you would like to obtain the list of articles recently added, but not necessarily the full feed of articles
# then use the call as below. In this case you can filter the articles to a subset based on
# keywords, concepts, categories, language, source, etc.
# You can also request more than 100 articles per call.
#

starttime = time.time()
updatesAfterNewsUri = None
updatesafterBlogUri = None
updatesAfterPrUri = None
# while True:
for i in range(10):
    q = QueryArticles(
        keywords="Trump",
        sourceLocationUri=er.getLocationUri("United States"))
    q.setRequestedResult(
        RequestArticlesRecentActivity(
            # download at most 2000 articles. if less of matching articles were added in last 10 minutes, less will be returned
            maxArticleCount=2000,
            # consider articles that were published after the provided uris
            updatesAfterNewsUri = updatesAfterNewsUri,
            updatesafterBlogUri = updatesafterBlogUri,
            updatesAfterPrUri = updatesAfterPrUri
        ))

    res = er.execQuery(q)
    for article in res.get("recentActivityArticles", {}).get("activity", []):
        print("Added article %s: %s" % (article["uri"], article["title"]))

    # remember what are the latest uris of the individual data items returned
    updatesAfterNewsUri = res.get("recentActivityArticles", {}).get("newestUri", {}).get("news")
    updatesafterBlogUri = res.get("recentActivityArticles", {}).get("newestUri", {}).get("blog")
    updatesAfterPrUri = res.get("recentActivityArticles", {}).get("newestUri", {}).get("pr")

    # wait for 10 minutes until next batch of new content is ready
    print("sleeping for 10 minutes...")
    time.sleep(10 * 60.0)


#
# similar example but in this case we will only consider articles that are related to Apple, Microsoft or Tesla
# for each article we also want to receive the list of concepts so that we know to which company the article is related to
#
concepts = [er.getConceptUri("Apple"), er.getConceptUri("Microsoft"), er.getConceptUri("tesla")]
appleConceptUri = er.getConceptUri("Apple")

updatesAfterNewsUri = None
updatesafterBlogUri = None
updatesAfterPrUri = None
# while True:
for i in range(10):
    q = QueryArticles(conceptUri=QueryItems.OR(concepts))
    q.setRequestedResult(
        RequestArticlesRecentActivity(
            # download at most 2000 articles. if less of matching articles were added in last 10 minutes, less will be returned
            maxArticleCount=2000,
            # consider articles that were published after the provided uris
            updatesAfterNewsUri = updatesAfterNewsUri,
            updatesafterBlogUri = updatesafterBlogUri,
            updatesAfterPrUri = updatesAfterPrUri,
            returnInfo = ReturnInfo(ArticleInfoFlags(bodyLen = -1, concepts = True, categories = True))
        ))

    res = er.execQuery(q)
    for article in res.get("recentActivityArticles", {}).get("activity", []):
        print("Added article %s: %s" % (article["uri"], article["title"]))
        conceptUris = [concept["uri"] for concept in article.get("concepts", [])]
        if appleConceptUri in conceptUris:
            print("Apple is mentioned in this article")

    # remember what are the latest uris of the individual data items returned
    updatesAfterNewsUri = res.get("recentActivityArticles", {}).get("newestUri", {}).get("news")
    updatesafterBlogUri = res.get("recentActivityArticles", {}).get("newestUri", {}).get("blog")
    updatesAfterPrUri = res.get("recentActivityArticles", {}).get("newestUri", {}).get("pr")

    # wait for 10 minutes until next batch of new content is ready
    print("sleeping for 5 minutes...")
    time.sleep(5 * 60.0)

#
# similar example but uses the updatesAfterTm parameter value provided in the previous calls. This is less
# ideal than using updatesAfter*Uri parameters since the data could be returned from multiple matchines which
# might not have perfectly synced clocks.
#

starttime = time.time()
updatesAfterTm = None
# while True:
for i in range(10):
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