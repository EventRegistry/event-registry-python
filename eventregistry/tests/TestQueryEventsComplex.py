import unittest
from eventregistry import *
from DataValidator import DataValidator

class TestQueryEventsComplex(DataValidator):

    def getQueryUriListForComplexQuery(self, cq):
        q = QueryEvents.initWithComplexQuery(cq)
        return self.getQueryUriListForQueryEvents(q)


    def getQueryUriListForQueryEvents(self, q):
        q.setRequestedResult(RequestEventsUriList(count = 50000))
        res = self.er.execQuery(q)
        assert "error" not in res, "Results included error: " + res.get("error", "")
        return res["uriList"]


    def testCompareSameResults1(self):
        cq1 = ComplexEventQuery(
            BaseQuery(
                conceptUri = QueryItems.AND([self.er.getConceptUri("obama"), self.er.getConceptUri("trump")]),
                exclude = BaseQuery(lang = QueryItems.OR(["eng", "deu"]))
            ))

        cq2 = ComplexEventQuery(
            query = CombinedQuery.AND([
                    BaseQuery(conceptUri = self.er.getConceptUri("obama")),
                    BaseQuery(conceptUri = self.er.getConceptUri("trump"))
                ],
                exclude = BaseQuery(lang = QueryItems.OR(["eng", "deu"]))))

        q = QueryEvents(conceptUri = QueryItems.AND([self.er.getConceptUri("obama"), self.er.getConceptUri("trump")]), ignoreLang = ["eng", "deu"])

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryEvents(q)
        self.assertEqual(listRes1["totalResults"], listRes2["totalResults"])
        self.assertEqual(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults2(self):
        cq1 = ComplexEventQuery(
            BaseQuery(
                sourceUri = QueryItems.OR([self.er.getNewsSourceUri("bbc"), self.er.getNewsSourceUri("associated press")]),
                exclude = BaseQuery(conceptUri = QueryItems.OR([self.er.getConceptUri("obama")]))))

        cq2 = ComplexEventQuery(
            CombinedQuery.OR([
                    BaseQuery(sourceUri = self.er.getNewsSourceUri("bbc")),
                    BaseQuery(sourceUri = self.er.getNewsSourceUri("associated press"))
                ],
                exclude = BaseQuery(conceptUri = QueryItems.OR([self.er.getConceptUri("obama")]))))

        q = QueryEvents(sourceUri = [self.er.getNewsSourceUri("bbc"), self.er.getNewsSourceUri("associated press")], ignoreConceptUri = self.er.getConceptUri("obama"))

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryEvents(q)
        self.assertEqual(listRes1["totalResults"], listRes2["totalResults"])
        self.assertEqual(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults3(self):
        cq1 = ComplexEventQuery(
            BaseQuery(dateStart = "2017-02-05", dateEnd = "2017-02-06",
                      exclude = BaseQuery(categoryUri = self.er.getCategoryUri("Business"))))

        cq2 = ComplexEventQuery(
            query = CombinedQuery.AND([
                    BaseQuery(dateStart = "2017-02-05"),
                    BaseQuery(dateEnd = "2017-02-06")
                ],
                exclude = BaseQuery(categoryUri = self.er.getCategoryUri("Business"))))

        q = QueryEvents(dateStart = "2017-02-05", dateEnd = "2017-02-06", ignoreCategoryUri = self.er.getCategoryUri("business"))

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryEvents(q)
        self.assertEqual(listRes1["totalResults"], listRes2["totalResults"])
        self.assertEqual(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults4(self):
        businessUri = categoryUri = self.er.getCategoryUri("Business")
        q1 = QueryEvents.initWithComplexQuery("""
        {
            "$query": {
                "dateStart": "2017-02-05", "dateEnd": "2017-02-06",
                "$not": {
                    "categoryUri": "%s"
                }
            }
        }
        """ % (businessUri))

        q = QueryEvents(dateStart = "2017-02-05", dateEnd = "2017-02-06", ignoreCategoryUri = self.er.getCategoryUri("business"))

        listRes1 = self.getQueryUriListForQueryEvents(q1)
        # compare with old approach
        listRes2 = self.getQueryUriListForQueryEvents(q)
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
        q1 = QueryEvents.initWithComplexQuery(qStr)

        cq2 = ComplexEventQuery(
            query = CombinedQuery.OR([
                    BaseQuery(dateStart = "2017-02-04", dateEnd = "2017-02-05"),
                    BaseQuery(conceptUri = trumpUri),
                    BaseQuery(categoryUri = politicsUri)
                ],
                exclude = CombinedQuery.OR([
                    BaseQuery(dateStart = "2017-02-04", dateEnd = "2017-02-04"),
                    BaseQuery(conceptUri = obamaUri)]
                )))

        listRes1 = self.getQueryUriListForQueryEvents(q1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        self.assertEqual(listRes1["totalResults"], listRes2["totalResults"])


    def testGetValidContent(self):
        trumpUri = self.er.getConceptUri("Trump")
        obamaUri = self.er.getConceptUri("Obama")
        politicsUri = self.er.getCategoryUri("politics")
        cq = ComplexEventQuery(
            query = CombinedQuery.OR([
                    BaseQuery(dateStart = "2017-02-04", dateEnd = "2017-02-05"),
                    BaseQuery(conceptUri = trumpUri),
                    BaseQuery(categoryUri = politicsUri)
                ],
                exclude = CombinedQuery.OR([
                    BaseQuery(dateStart = "2017-02-04", dateEnd = "2017-02-04"),
                    BaseQuery(conceptUri = obamaUri)]
                )))

        retInfo = ReturnInfo(eventInfo = EventInfoFlags(concepts = True, categories = True, stories = True))

        iter = QueryEventsIter.initWithComplexQuery(cq)
        for event in iter.execQuery(self.er, returnInfo =  retInfo):
            foundTrump = False
            validDate = False
            foundCategory =  False
            for c in event.get("concepts", []):
                if c["uri"] == trumpUri: foundTrump = True
            for c in event.get("categories", []):
                if c["uri"].find(politicsUri) == 0: foundCategory = True
            if event.get("eventDate", "") == "2017-02-05": validDate = True

            if not (foundTrump or validDate or foundCategory):
                self.assertTrue(False, "invalid event that should not be in the results")

            self.assertTrue(event.get("eventDate", "") != "2017-02-04", "event contained invalid date")
            for c in event.get("concepts", []):
                self.assertTrue(c["uri"] != obamaUri, "event contained obama")




if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryEventsComplex)
    unittest.TextTestRunner(verbosity=3).run(suite)
