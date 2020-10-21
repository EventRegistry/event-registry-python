import unittest, math
from eventregistry import *
from eventregistry.tests.DataValidator import DataValidator


class TestTopicPage(DataValidator):

    def createTopicPage(self):
        q = TopicPage(self.er)
        q.loadTopicPageFromER("5aa6837b-d23d-4a71-bc80-7aad676e1905")
        return q


    def testGetArticlesForTopicPage(self):
        q = self.createTopicPage()
        uriSet = set()
        for page in range(1, 20):
            res = q.getArticles(page=page, dataType=["news", "blog"], sortBy="rel")
            rel = sys.maxsize
            for art in res.get("articles", {}).get("results", []):
                assert art.get("wgt") <= rel
                rel = art.get("wgt")
                assert art.get("uri") not in uriSet
                uriSet.add(art.get("uri"))


    def testGetEventsForTopicPage(self):
        q = self.createTopicPage()
        uriSet = set()
        for page in range(1, 20):
            res = q.getEvents(page=page, sortBy="rel")
            rel = sys.maxsize
            for event in res.get("events", {}).get("results", []):
                assert event.get("wgt") <= rel
                rel = event.get("wgt")
                assert event.get("uri") not in uriSet
                uriSet.add(event.get("uri"))


    def testCreateTopicPage(self):
        topic = TopicPage(self.er)
        appleUri = self.er.getConceptUri("apple")
        msoftUri = self.er.getConceptUri("microsoft")
        iphoneUri = self.er.getConceptUri("iphone")
        businessUri = self.er.getCategoryUri("business")
        topic.addConcept(appleUri, 50, required = False)
        topic.addConcept(msoftUri, 50, required = True)
        topic.addConcept(iphoneUri, 50, excluded = True)
        topic.addCategory(businessUri, 50, required=True)
        for page in range(1, 10):
            res = topic.getArticles(page = page, returnInfo = ReturnInfo(articleInfo=ArticleInfoFlags(concepts=True, categories=True, maxConceptsPerType=100)))
            for art in res.get("articles").get("results"):
                foundConcept = False
                foundCategory = False
                for conceptObj in art.get("concepts", []):
                    assert iphoneUri != conceptObj["uri"], "Found iphone in the article"
                    if msoftUri == conceptObj["uri"]:
                        foundConcept = True
                for categoryObj in art.get("categories", []):
                    if categoryObj["uri"].startswith(businessUri):
                        foundCategory = True
                assert foundConcept, "Article did not have a required concept"
                assert foundCategory, "Article did not have a required category"


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTopicPage)
    # suite = unittest.TestSuite()
    # suite.addTest(TestQueryArticles("testQuery2"))
    unittest.TextTestRunner(verbosity=3).run(suite)
