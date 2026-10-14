"""
examples showing how to obtain the feed of articles that were recently added to Event Registry

NOTE: the examples make a request and then sleep for a while, 10 times in a row, so they run for a long time
(from 10 minutes up to 100 minutes each)
"""
import os
import sys
import time

from eventregistry import (EventRegistry, GetRecentArticles, QueryArticles, QueryItems, RequestArticlesRecentActivity,
                           ReturnInfo, ArticleInfoFlags)


def fullStreamOfArticles(er):
    """
    get the full minute by minute stream of all articles added to Event Registry
    """
    # use the code below to obtain from ER the full minute by minute stream of articles added to the system

    recentQ = GetRecentArticles(er, returnInfo = ReturnInfo(ArticleInfoFlags(bodyLen = -1, concepts = True, categories = True)), recentActivityArticlesMaxArticleCount = 300)
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


def recentArticlesMatchingQuery(er):
    """
    every 10 minutes get the recently added articles that match a search query
    """
    # if you would like to obtain the list of articles recently added, but not necessarily the full feed of articles
    # then use the call as below. In this case you can filter the articles to a subset based on
    # keywords, concepts, categories, language, source, etc.
    # You can also request more than 100 articles per call.

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


def recentArticlesAboutCompanies(er):
    """
    get the recently added articles about several companies and check which company each article mentions
    """
    # similar example but in this case we will only consider articles that are related to Apple, Microsoft or Tesla
    # for each article we also want to receive the list of concepts so that we know to which company the article is related to
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


def recentArticlesUsingUpdatesAfterTm(er):
    """
    get the recently added articles using the time (instead of the uris) returned by the previous call
    """
    # similar example but uses the updatesAfterTm parameter value provided in the previous calls. This is less
    # ideal than using updatesAfter*Uri parameters since the data could be returned from multiple matchines which
    # might not have perfectly synced clocks.

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


# the examples in this file, in the order in which they are run when "all" is used
EXAMPLES = [
    fullStreamOfArticles,
    recentArticlesMatchingQuery,
    recentArticlesAboutCompanies,
    recentArticlesUsingUpdatesAfterTm,
]


def main():
    """
    run the examples that are named on the command line, for example:
        python FeedOfNewArticlesExamples.py fullStreamOfArticles
    Use "all" to run all of them. Without arguments we only list the available examples and make no requests
    """
    examples = {example.__name__: example for example in EXAMPLES}
    names = list(examples) if sys.argv[1:] == ["all"] else sys.argv[1:]
    unknown = [name for name in names if name not in examples]
    if unknown or not names:
        if unknown:
            print("Unknown example(s): %s\n" % ", ".join(unknown))
        print("Usage: python %s <example> [<example> ...] | all\n\nAvailable examples:" % os.path.basename(__file__))
        for name, example in examples.items():
            print("  %-33s %s" % (name, (example.__doc__ or "").strip().split("\n")[0]))
        sys.exit(1 if unknown else 0)

    # the API key is read from the EVENTREGISTRY_API_KEY environment variable or from the settings.json file
    # (see README.md in this folder). The examples make real requests, which use the tokens of your account
    er = EventRegistry()
    for name in names:
        print("\n===== %s =====" % name)
        examples[name](er)


if __name__ == "__main__":
    main()
