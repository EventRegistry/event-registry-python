import unittest, math
from eventregistry import *
from eventregistry.tests.DataValidator import DataValidator


class TestERTrends(DataValidator):

    def testGetTrendingConcepts(self):
        q = GetTrendingConcepts(source = "news", count = 10)
        ret = self.er.execQuery(q)
        self.assertTrue(isinstance(ret, list))
        self.assertTrue(len(ret) == 10)
        for item in ret:
            self.assertTrue("uri" in item)
            self.assertTrue("label" in item)
            self.assertTrue("trendingScore" in item)


    def testGetTrendingConceptGroups(self):
        q = GetTrendingConceptGroups(source = "news", count = 10)
        q.getConceptTypeGroups(["person", "org"])
        ret = self.er.execQuery(q)
        self.assertTrue(isinstance(ret, dict))
        self.assertTrue("person" in ret)
        self.assertTrue("org" in ret)
        for name in ["person", "org"]:
            arr = ret[name].get("trendingConcepts")
            self.assertTrue(len(arr) == 10)
            for item in arr:
                self.assertTrue("uri" in item)
                self.assertTrue("label" in item)
                self.assertTrue("trendingScore" in item)


    def testGetTrendingCategories(self):
        q = GetTrendingCategories(source = "news", count = 10)
        ret = self.er.execQuery(q)
        self.assertTrue(isinstance(ret, list))
        self.assertTrue(len(ret) == 10)
        for item in ret:
            self.assertTrue("uri" in item)
            self.assertTrue("label" in item)
            self.assertTrue("trendingScore" in item)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestERTrends)
    unittest.TextTestRunner(verbosity=3).run(suite)
