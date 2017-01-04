from eventregistry import *

er = EventRegistry()

# search article by uri
q = QueryArticle("247634888")
q.addRequestedResult(RequestArticleInfo())                 # get all info about the specified article
res = er.execQuery(q)

# search article by url
artMapper = ArticleMapper(er)
#artUri = artMapper.getArticleUri("http://www.bbc.co.uk/news/world-europe-31763789#sa-ns_mchannel%3Drss%26ns_source%3DPublicRSS20-sa")
artUri = artMapper.getArticleUri("http://www.mynet.com/haber/guncel/share-2058597-1")
q = QueryArticle.queryByUri(artUri)
q.addRequestedResult(RequestArticleInfo())                 # get all info about the specified article
res = er.execQuery(q)

# first search for articles related to Apple
q = QueryArticles()
q.setDateLimit(datetime.datetime(2016, 12, 10, 3, 2, 1), datetime.datetime(2016, 12, 18))
#q.addKeyword("apple")
#q.addKeyword("iphone")
q.addConcept(er.getConceptUri("Apple"))
q.addRequestedResult(RequestArticlesInfo(count = 30,
    returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(duplicateList = True, concepts = True, originalArticle = True, categories = True, location = True, image = True))))
res = er.execQuery(q)

# take top 5 articles and for those articles only request detailed information (article info, original article, list of duplicated articles)
obj = createStructFromDict(res)
uris = [article.uri for article in obj.articles.results[:5]]
q = QueryArticle(uris)
q.addRequestedResult(RequestArticleInfo(returnInfo = ReturnInfo(
    articleInfo = ArticleInfoFlags(concepts = True, categories = True, location = True))))
q.addRequestedResult(RequestArticleOriginalArticle())
q.addRequestedResult(RequestArticleDuplicatedArticles())
res = er.execQuery(q)
obj = createStructFromDict(res)
