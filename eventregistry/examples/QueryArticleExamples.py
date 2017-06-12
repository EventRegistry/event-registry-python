"""
examples that download information about the individual news articles
"""
from eventregistry import *

er = EventRegistry()

#
# search article by uri
q = QueryArticle("247634888")
res = er.execQuery(q)

#
# search article by url
#

# use ArticleMapper to map article URL to the URI (id) that is used by ER internally
artMapper = ArticleMapper(er)
#artUri = artMapper.getArticleUri("http://www.bbc.co.uk/news/world-europe-31763789#sa-ns_mchannel%3Drss%26ns_source%3DPublicRSS20-sa")
artUri = artMapper.getArticleUri("http://www.mynet.com/haber/guncel/share-2058597-1")
q = QueryArticle.queryByUri(artUri)
# get all info about the specified article
q.setRequestedResult(RequestArticleInfo())
res = er.execQuery(q)


#
# do regular article search, obtain a list of resulting article URIs and then ask for details about these articles
#

# first search for articles related to Apple
q = QueryArticles(conceptUri = er.getConceptUri("Apple"))
q.setRequestedResult(RequestArticlesUriList())
res = er.execQuery(q)
# take the list of article URIs that match the search criteria (i.e. ['641565713', '641559021', '641551446', '641025492', '641548675', ...])
articleUriList = res.get("uriList", {}).get("results", [])

# take first 5 article URIs and ask for all details about these articles
queryUris = articleUriList[:5]
q = QueryArticle(queryUris)
q.setRequestedResult(RequestArticleInfo(returnInfo = ReturnInfo(
    articleInfo = ArticleInfoFlags(concepts = True, categories = True, location = True))))
res = er.execQuery(q)
