import unittest
from eventregistry import *
from DataValidator import DataValidator

class TestInvalidQueries(DataValidator):

    def testInvalidQueries(self):
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
        q = QueryArticles.initWithComplexQuery(qStr)
        res = self.er.execQuery(q)

        qStr = """
        {
            "$query": {
                "$or": [
                    { "conceptUri": "%s" },
                    { "categoryUri": "%s" }
                ],
                "$not": {
                    "$or": [
                    ]
                }
            }
        }
            """ % (trumpUri, politicsUri)
        q = QueryArticles()
        q._setVal("query", qStr)
        res = self.er.execQuery(q)

        qStr = """
        {
            "$query": {
                "$or": [
                    { "conceptUri": "%s" },
                    { "categoryUri": "%s" }
                ],
                "$not": {
                }
            }
        }
            """ % (trumpUri, politicsUri)
        q = QueryArticles()
        q._setVal("query", qStr)
        res = self.er.execQuery(q)

        qStr = """
        {
            "$query": {
                "$aaaaor": [
                    { "conceptUri": "%s" },
                    { "categoryUri": "%s" }
                ],
                "$not": {
                }
            }
        }
            """ % (trumpUri, politicsUri)
        q = QueryArticles()
        q._setVal("query", qStr)
        res = self.er.execQuery(q)

        qStr = """
        {
            "$query": {
                "$and": [
                ],
                "$not": {
                }
            }
        }"""
        q = QueryArticles()
        q._setVal("query", qStr)
        res = self.er.execQuery(q)

        qStr = """
        {
            "$query": {
                "$and": [
                ]
            }
        }"""
        q = QueryArticles()
        q._setVal("query", qStr)
        res = self.er.execQuery(q)

        qStr = """
        {
            "$query": {
                "$and": {}
            }
        }"""
        q = QueryArticles()
        q._setVal("query", qStr)
        res = self.er.execQuery(q)

        qStr = """
        {
            "$query": {
            }
        }"""
        q = QueryArticles()
        q._setVal("query", qStr)
        res = self.er.execQuery(q)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInvalidQueries)
    unittest.TextTestRunner(verbosity=3).run(suite)
