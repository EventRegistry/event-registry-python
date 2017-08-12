import unittest
from eventregistry import *
from DataValidator import DataValidator

class TestQueryArticlesComplex(DataValidator):

    def getQueryUriListForComplexQuery(self, cq):
        q = QueryArticles.initWithComplexQuery(cq)
        return self.getQueryUriListForQueryArticles(q)


    def getQueryUriListForQueryArticles(self, q):
        q.setRequestedResult(RequestArticlesUriList(count = 50000))
        res = self.er.execQuery(q)
        assert "error" not in res, "Results included error: " + res.get("error", "")
        return res["uriList"]


    def testKw1(self):
        cq1 = ComplexArticleQuery(BaseQuery(keyword = "obama", keywordLoc = "title"))
        artIter = QueryArticlesIter.initWithComplexQuery(cq1)
        for art in artIter.execQuery(self.er):
            self.assertTrue(art["title"].lower().find("obama") >= 0)


    def testKw2(self):
        qStr = """
        {
            "$query": {
                "keyword": "obama", "keywordLoc": "title"
            }
        }
        """
        qiter = QueryArticlesIter.initWithComplexQuery(qStr)
        for art in qiter.execQuery(self.er):
            self.assertTrue(art["title"].lower().find("obama") >= 0)


    def testKw3(self):
        cq1 = ComplexArticleQuery(BaseQuery(keyword = "home", keywordLoc = "body"))
        artIter = QueryArticlesIter.initWithComplexQuery(cq1)
        for art in artIter.execQuery(self.er):
            self.assertTrue(art["body"].lower().find("home") >= 0)


    def testCompareSameResultsKw1(self):
        cq1 = ComplexArticleQuery(
            BaseQuery(keyword =  QueryItems.AND(["obama", "trump"]),
                exclude = BaseQuery(lang = QueryItems.OR(["eng", "deu"]))))

        cq2 = ComplexArticleQuery(
            query = CombinedQuery.AND([
                BaseQuery(keyword = "obama"),
                BaseQuery(keyword = "trump") ],
                exclude = BaseQuery(lang = QueryItems.OR(["eng", "deu"]))))

        q = QueryArticles(keywords = QueryItems.AND(["obama", "trump"]), ignoreLang = ["eng", "deu"])

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryArticles(q)
        self.assertEqual(listRes1["totalResults"], listRes2["totalResults"])
        self.assertEqual(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults1(self):
        cq1 = ComplexArticleQuery(
            BaseQuery(conceptUri = QueryItems.AND([self.er.getConceptUri("obama"), self.er.getConceptUri("trump")]),
                exclude = BaseQuery(lang = QueryItems.OR(["eng", "deu"]))))

        cq2 = ComplexArticleQuery(
            query = CombinedQuery.AND([
                BaseQuery(conceptUri = self.er.getConceptUri("obama")),
                BaseQuery(conceptUri = self.er.getConceptUri("trump")) ],
                exclude = BaseQuery(lang = QueryItems.OR(["eng", "deu"]))))

        q = QueryArticles(conceptUri = QueryItems.AND([self.er.getConceptUri("obama"), self.er.getConceptUri("trump")]), ignoreLang = ["eng", "deu"])

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryArticles(q)
        self.assertEqual(listRes1["totalResults"], listRes2["totalResults"])
        self.assertEqual(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults2(self):
        cq1 = ComplexArticleQuery(
            query = BaseQuery(sourceUri = QueryItems.OR([self.er.getNewsSourceUri("bbc"), self.er.getNewsSourceUri("associated press")]),
                exclude = BaseQuery(conceptUri = QueryItems.OR([self.er.getConceptUri("obama")]))))

        cq2 = ComplexArticleQuery(
            query = CombinedQuery.OR([
                BaseQuery(sourceUri = self.er.getNewsSourceUri("bbc")),
                BaseQuery(sourceUri = self.er.getNewsSourceUri("associated press"))],
                exclude = BaseQuery(conceptUri = QueryItems.OR([self.er.getConceptUri("obama")]))))

        q = QueryArticles(sourceUri = [self.er.getNewsSourceUri("bbc"), self.er.getNewsSourceUri("associated press")], ignoreConceptUri = self.er.getConceptUri("obama"))

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryArticles(q)
        self.assertEqual(listRes1["totalResults"], listRes2["totalResults"])
        self.assertEqual(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults3(self):
        cq1 = ComplexArticleQuery(
            query = BaseQuery(dateStart = "2017-02-05", dateEnd = "2017-02-06",
                exclude = BaseQuery(categoryUri = self.er.getCategoryUri("Business"))))

        cq2 = ComplexArticleQuery(
            query = CombinedQuery.AND([
                BaseQuery(dateStart = "2017-02-05"),
                BaseQuery(dateEnd = "2017-02-06")],
                exclude = BaseQuery(categoryUri = self.er.getCategoryUri("Business"))))

        q = QueryArticles(dateStart = "2017-02-05", dateEnd = "2017-02-06", ignoreCategoryUri = self.er.getCategoryUri("business"))

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryArticles(q)
        self.assertEqual(listRes1["totalResults"], listRes2["totalResults"])
        self.assertEqual(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults4(self):
        businessUri = categoryUri = self.er.getCategoryUri("Business")
        q1 = QueryArticles.initWithComplexQuery("""
        {
            "$query": {
                "dateStart": "2017-02-05", "dateEnd": "2017-02-06",
                "$not": {
                    "categoryUri": "%s"
                }
            }
        }
        """ % (businessUri))

        q = QueryArticles(dateStart = "2017-02-05", dateEnd = "2017-02-06", ignoreCategoryUri = self.er.getCategoryUri("business"))

        listRes1 = self.getQueryUriListForQueryArticles(q1)
        # compare with old approach
        listRes2 = self.getQueryUriListForQueryArticles(q)
        self.assertEqual(listRes1["totalResults"], listRes2["totalResults"])


    def testCompareSameResults5(self):
        trumpUri = self.er.getConceptUri("Trump")
        obamaUri = self.er.getConceptUri("Obama")
        politicsUri = self.er.getCategoryUri("politics")
        qStr = """
        {
            "$query": {
                "$or": [
                    { "dateStart": "2017-02-05", "dateEnd": "2017-02-05" },
                    { "conceptUri": "%s" },
                    { "categoryUri": "%s" }
                ],
                "$not": {
                    "$or": [
                        { "dateStart": "2017-02-04", "dateEnd": "2017-02-04" },
                        { "conceptUri": "%s" }
                    ]
                }
            }
        }
            """ % (trumpUri, politicsUri, obamaUri)
        q1 = QueryArticles.initWithComplexQuery(qStr)

        cq2 = ComplexArticleQuery(
            query = CombinedQuery.OR([
                    BaseQuery(dateStart = "2017-02-04", dateEnd = "2017-02-05"),
                    BaseQuery(conceptUri = trumpUri),
                    BaseQuery(categoryUri = politicsUri)
                ],
                exclude = CombinedQuery.OR([
                    BaseQuery(dateStart = "2017-02-04", dateEnd = "2017-02-04"),
                    BaseQuery(conceptUri = obamaUri)]
                )))

        listRes1 = self.getQueryUriListForQueryArticles(q1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        self.assertEqual(listRes1["totalResults"], listRes2["totalResults"])


    def testCompareSameResults6(self):
        trumpUri = self.er.getConceptUri("Trump")
        obamaUri = self.er.getConceptUri("Obama")
        politicsUri = self.er.getCategoryUri("politics")
        merkelUri = self.er.getConceptUri("merkel")
        businessUri = self.er.getCategoryUri("business")

        qStr = """
        {
            "$query": {
                "$or": [
                    { "dateStart": "2017-02-05", "dateEnd": "2017-02-05" },
                    { "dateStart": "2017-02-04", "dateEnd": "2017-02-04" },
                    { "conceptUri": "%s" },
                    { "categoryUri": "%s" },
                    {
                        "$and": [
                            { "conceptUri": "%s" },
                            { "categoryUri": "%s" }
                        ]
                    }
                ],
                "$not": {
                    "$or": [
                        { "dateStart": "2017-02-04", "dateEnd": "2017-02-04" },
                        { "conceptUri": "%s" }
                    ]
                }
            }
        }
            """ % (trumpUri, politicsUri, merkelUri, businessUri, obamaUri)
        q1 = QueryArticles.initWithComplexQuery(qStr)

        cq2 = ComplexArticleQuery(
            query = CombinedQuery.OR([
                    BaseQuery(dateStart = "2017-02-04", dateEnd = "2017-02-05"),
                    BaseQuery(conceptUri = trumpUri),
                    BaseQuery(categoryUri = politicsUri),
                    CombinedQuery.AND([
                        BaseQuery(conceptUri = merkelUri),
                        BaseQuery(categoryUri = businessUri)
                        ])
                ],
                exclude = CombinedQuery.OR([
                    BaseQuery(dateStart = "2017-02-04", dateEnd = "2017-02-04"),
                    BaseQuery(conceptUri = obamaUri)]
                )))

        listRes1 = self.getQueryUriListForQueryArticles(q1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        self.assertEqual(listRes1["totalResults"], listRes2["totalResults"])


    def _testGetValidContent(self):
        trumpUri = self.er.getConceptUri("Trump")
        obamaUri = self.er.getConceptUri("Obama")
        politicsUri = self.er.getCategoryUri("politics")
        cq = ComplexArticleQuery(
            query = CombinedQuery.OR([
                    BaseQuery(dateStart = "2017-02-04", dateEnd = "2017-02-05"),
                    BaseQuery(conceptUri = trumpUri),
                    BaseQuery(categoryUri = politicsUri)
                ],
                exclude = CombinedQuery.OR([
                    BaseQuery(dateStart = "2017-02-04", dateEnd = "2017-02-04"),
                    BaseQuery(conceptUri = obamaUri)]
                )))

        retInfo = ReturnInfo(articleInfo = ArticleInfoFlags(concepts = True, categories = True))

        iter = QueryArticlesIter.initWithComplexQuery(cq)
        for art in iter.execQuery(self.er, returnInfo =  retInfo):
            foundTrump = False
            validDate = False
            foundCategory =  False
            for c in art.get("concepts", []):
                if c["uri"] == trumpUri: foundTrump = True
            for c in art.get("categories", []):
                if c["uri"].find(politicsUri) == 0: foundCategory = True
            if art["date"] == "2017-02-05": validDate = True

            if not (foundTrump or validDate or foundCategory):
                self.assertTrue(False, "invalid article that should not be in the results")

            self.assertTrue(art["date"] != "2017-02-04", "article contained invalid date")
            for c in art.get("concepts", []):
                self.assertTrue(c["uri"] != obamaUri, "article contained obama")




if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryArticlesComplex)
    unittest.TextTestRunner(verbosity=3).run(suite)
