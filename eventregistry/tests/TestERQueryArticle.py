﻿import unittest
from eventregistry import *
from eventregistry.tests.DataValidator import DataValidator

class TestQueryArticle(DataValidator):

    def createQuery(self):
        q = QueryArticles(conceptUri = self.er.getConceptUri("Obama"))
        q.setRequestedResult(RequestArticlesUriWgtList(count = 100))
        res = self.er.execQuery(q)
        q = QueryArticle([uri for uri in EventRegistry.getUriFromUriWgt(res["uriWgtList"]["results"]) if uri.endswith("TEMP") == False][:10])
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
            urls = mapper.getArticleUri(url)
            if urls:
                mappedUris.append(urls)
        if mappedUris == []:
            return
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
