import unittest
from eventregistry import *
from DataValidator import DataValidator

class TestQueryArticle(DataValidator):

    def createQuery(self):
        q = QueryArticles(conceptUri = self.er.getConceptUri("Obama"))
        q.setRequestedResult(RequestArticlesUriList(count = 10))
        res = self.er.execQuery(q)
        q = QueryArticle(res["uriList"]["results"])
        return q


    def testArticleList(self):
        q = self.createQuery()
        q.setRequestedResult(RequestArticleInfo(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertEqual(len(res), 10, "Expected to get a list of 10 articles")
        for article in list(res.values()):
            self.ensureValidArticle(article["info"], "articleList")

        uris = [article.get("info").get("uri") for article in list(res.values())]
        urls = [article.get("info").get("url") for article in list(res.values())]
        uniqueUrls = list(set(urls))

        mapper = ArticleMapper(self.er)
        mappedUris = []
        for url in uniqueUrls:
            # getArticleUri returns a list, so we extend the list of items
            mappedUris.extend(mapper.getArticleUri(url))
        q = QueryArticle.queryByUri(mappedUris)
        q.setRequestedResult(RequestArticleInfo(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        for article in list(res.values()):
            # it's possible that the article was removed from ER
            if "error" in article:
                continue
            self.ensureValidArticle(article["info"], "articleList")

        q = QueryArticle.queryByUri(uris)
        q.setRequestedResult(RequestArticleInfo(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.assertEqual(len(res), 10, "Expected to get a list of 10 articles when searching by uris")
        for article in list(res.values()):
            self.ensureValidArticle(article["info"], "articleList")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryArticle)
    unittest.TextTestRunner(verbosity=3).run(suite)
