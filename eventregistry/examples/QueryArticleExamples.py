"""
examples that download information about the individual news articles
"""
import os
import sys

from eventregistry import (EventRegistry, ArticleMapper, QueryArticle, QueryArticles, RequestArticleInfo,
                           RequestArticlesUriWgtList, ReturnInfo, ArticleInfoFlags)


def articleByUri(er):
    """
    get the information about the article with the given URI
    """
    # search article by uri
    q = QueryArticle("247634888")
    res = er.execQuery(q)
    print(er.format(res))


def articleByUrl(er):
    """
    get the information about the article with the given URL (web address)
    """
    # search article by url

    # use ArticleMapper to map article URL to the URI (id) that is used by ER internally
    artMapper = ArticleMapper(er)
    artUri = artMapper.getArticleUri("http://www.bbc.co.uk/news/world-europe-31763789#sa-ns_mchannel%3Drss%26ns_source%3DPublicRSS20-sa")
    q = QueryArticle.queryByUri(artUri)
    # get all info about the specified article
    q.setRequestedResult(RequestArticleInfo())
    res = er.execQuery(q)
    print(er.format(res))


def detailsOfArticlesFromSearch(er):
    """
    search for articles, get the URIs of the matching articles and then ask for the details about some of them
    """
    # do regular article search, obtain a list of resulting article URIs and then ask for details about these articles

    # first search for articles related to Apple
    q = QueryArticles(conceptUri = er.getConceptUri("Apple"))
    q.setRequestedResult(RequestArticlesUriWgtList())
    res = er.execQuery(q)
    # take the list of article URIs that match the search criteria (i.e. ['641565713', '641559021', '641551446', '641025492', '641548675', ...])
    articleUriWgtList = res.get("uriWgtList", {}).get("results", [])

    # take first 5 article URIs and ask for all details about these articles
    queryUris = EventRegistry.getUriFromUriWgt(articleUriWgtList[:5])
    q = QueryArticle(queryUris)
    q.setRequestedResult(RequestArticleInfo(returnInfo = ReturnInfo(
        articleInfo = ArticleInfoFlags(concepts = True, categories = True, location = True))))
    res = er.execQuery(q)
    print(er.format(res))


# the examples in this file, in the order in which they are run when "all" is used
EXAMPLES = [
    articleByUri,
    articleByUrl,
    detailsOfArticlesFromSearch,
]


def main():
    """
    run the examples that are named on the command line, for example:
        python QueryArticleExamples.py articleByUri
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
            print("  %-27s %s" % (name, (example.__doc__ or "").strip().split("\n")[0]))
        sys.exit(1 if unknown else 0)

    # the API key is read from the EVENTREGISTRY_API_KEY environment variable or from the settings.json file
    # (see README.md in this folder). The examples make real requests, which use the tokens of your account
    er = EventRegistry()
    for name in names:
        print("\n===== %s =====" % name)
        examples[name](er)


if __name__ == "__main__":
    main()
