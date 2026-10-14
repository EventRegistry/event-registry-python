"""
Offline tests that validate the exact request payload the SDK generates.

Instead of executing queries against the live API, the HTTP layer is mocked and the
tests verify that the JSON body that WOULD be sent in the POST request contains the
expected endpoint path, parameters and values.

Run with:
    python -m unittest eventregistry.tests.TestRequestPayloads -v
"""
import datetime
import json
import unittest
from unittest import mock

from eventregistry import *
from eventregistry.tests.TestOfflineUnit import FakeResponse, makeER


class PayloadCaptureTestCase(unittest.TestCase):
    """base class that captures the url and json body of every POST the SDK would make"""

    def setUp(self):
        self.er = makeER()
        self.requests = []
        def fakePost(url, json = None, timeout = None):
            self.requests.append({"url": url, "json": json})
            return FakeResponse(data = {})
        self.er._reqSession.post = fakePost

    def execPayload(self, query):
        """execute the query and return (endpoint path, sent json body)"""
        self.er.execQuery(query)
        sent = self.requests[-1]
        path = sent["url"].replace(self.er.getHost(), "")
        return path, sent["json"]

    def lastRequest(self):
        sent = self.requests[-1]
        path = sent["url"].replace(self.er.getHost(), "").replace(self.er._hostAnalytics, "")
        return path, sent["json"]


class TestArticleQueryPayload(PayloadCaptureTestCase):

    def testDefaultPayload(self):
        path, body = self.execPayload(QueryArticles(keywords = "obama"))
        self.assertEqual(path, "/api/v1/article")
        self.assertEqual(body["action"], "getArticles")
        self.assertEqual(body["keyword"], "obama")
        self.assertEqual(body["apiKey"], "TESTKEY")
        # default result type is the article list, first page, 100 items, sorted by date desc
        self.assertEqual(body["resultType"], ["articles"])
        self.assertEqual(body["articlesPage"], 1)
        self.assertEqual(body["articlesCount"], 100)
        self.assertEqual(body["articlesSortBy"], "date")
        self.assertEqual(body["articlesSortByAsc"], False)

    def testConditionsPayload(self):
        q = QueryArticles(
            keywords = QueryItems.OR(["ai", "machine learning"]),
            conceptUri = QueryItems.AND(["conceptA", "conceptB"]),
            categoryUri = "dmoz/Business",
            sourceUri = "nytimes.com",
            lang = ["eng", "deu"],
            dateStart = "2024-01-01",
            dateEnd = datetime.date(2024, 1, 31),
            keywordsLoc = "title",
            keywordSearchMode = "exact",
            ignoreKeywords = "spam",
            ignoreLang = "ita",
            isDuplicateFilter = "skipDuplicates",
            minSentiment = -0.3,
            dataType = ["news", "pr"])
        path, body = self.execPayload(q)
        self.assertEqual(body["keyword"], ["ai", "machine learning"])
        self.assertEqual(body["keywordOper"], "or")
        self.assertEqual(body["conceptUri"], ["conceptA", "conceptB"])
        self.assertEqual(body["conceptOper"], "and")
        self.assertEqual(body["categoryUri"], "dmoz/Business")
        self.assertEqual(body["sourceUri"], "nytimes.com")
        self.assertEqual(body["lang"], ["eng", "deu"])
        self.assertEqual(body["dateStart"], "2024-01-01")
        self.assertEqual(body["dateEnd"], "2024-01-31")
        self.assertEqual(body["keywordLoc"], "title")
        self.assertEqual(body["keywordSearchMode"], "exact")
        self.assertEqual(body["ignoreKeyword"], "spam")
        self.assertEqual(body["ignoreLang"], "ita")
        self.assertEqual(body["isDuplicateFilter"], "skipDuplicates")
        self.assertEqual(body["minSentiment"], -0.3)
        self.assertEqual(body["dataType"], ["news", "pr"])

    def testReturnInfoFlagsInPayload(self):
        q = QueryArticles(keywords = "x", requestedResult = RequestArticlesInfo(
            page = 3, count = 25, sortBy = "socialScore", sortByAsc = True,
            returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 0, concepts = True, image = False),
                                    sourceInfo = SourceInfoFlags(ranking = True))))
        path, body = self.execPayload(q)
        self.assertEqual(body["articlesPage"], 3)
        self.assertEqual(body["articlesCount"], 25)
        self.assertEqual(body["articlesSortBy"], "socialScore")
        self.assertEqual(body["articlesSortByAsc"], True)
        self.assertEqual(body["articleBodyLen"], 0)
        self.assertEqual(body["includeArticleConcepts"], True)
        self.assertEqual(body["includeArticleImage"], False)
        self.assertEqual(body["includeSourceRanking"], True)

    def testAggregateResultTypes(self):
        q = QueryArticles(keywords = "x")
        q.setRequestedResult(RequestArticlesConceptAggr(conceptCount = 40, articlesSampleSize = 5000))
        path, body = self.execPayload(q)
        self.assertEqual(body["resultType"], ["conceptAggr"])
        self.assertEqual(body["conceptAggrConceptCount"], 40)
        self.assertEqual(body["conceptAggrSampleSize"], 5000)

        q.setRequestedResult(RequestArticlesUriWgtList(page = 2, count = 20000))
        path, body = self.execPayload(q)
        self.assertEqual(body["resultType"], ["uriWgtList"])
        self.assertEqual(body["uriWgtListPage"], 2)
        self.assertEqual(body["uriWgtListCount"], 20000)

    def testComplexQueryPayload(self):
        cq = ComplexArticleQuery(
            CombinedQuery.OR([BaseQuery(keyword = "ai"), BaseQuery(conceptUri = "c1")],
                             exclude = BaseQuery(lang = "ita")),
            minSentiment = 0.2)
        q = QueryArticles.initWithComplexQuery(cq)
        path, body = self.execPayload(q)
        sentQuery = json.loads(body["query"])
        self.assertEqual(sentQuery["$query"], {"$or": [{"keyword": "ai"}, {"conceptUri": "c1"}], "$not": {"lang": "ita"}})
        self.assertEqual(sentQuery["$filter"], {"minSentiment": 0.2})

    def testArchiveFlagInPayload(self):
        er = makeER(allowUseOfArchive = False)
        er._reqSession.post = mock.Mock(return_value = FakeResponse(data = {}))
        er.execQuery(QueryArticles(keywords = "x"))
        self.assertEqual(er._reqSession.post.call_args.kwargs["json"]["forceMaxDataTimeWindow"], 31)


class TestEventQueryPayload(PayloadCaptureTestCase):

    def testDefaultPayload(self):
        path, body = self.execPayload(QueryEvents(keywords = "earthquake"))
        self.assertEqual(path, "/api/v1/event")
        self.assertEqual(body["action"], "getEvents")
        self.assertEqual(body["keyword"], "earthquake")
        self.assertEqual(body["resultType"], ["events"])
        self.assertEqual(body["eventsPage"], 1)
        self.assertEqual(body["eventsCount"], 50)
        self.assertEqual(body["eventsSortBy"], "rel")

    def testEventSpecificConditions(self):
        q = QueryEvents(conceptUri = "c1",
                        minArticlesInEvent = 10, maxArticlesInEvent = 500,
                        reportingDateStart = "2024-02-01", reportingDateEnd = "2024-02-28",
                        lang = "eng")
        path, body = self.execPayload(q)
        self.assertEqual(body["minArticlesInEvent"], 10)
        self.assertEqual(body["maxArticlesInEvent"], 500)
        self.assertEqual(body["reportingDateStart"], "2024-02-01")
        self.assertEqual(body["reportingDateEnd"], "2024-02-28")
        self.assertEqual(body["lang"], "eng")

    def testUriListPayload(self):
        q = QueryEvents.initWithEventUriList(["eng-1", "eng-2"])
        path, body = self.execPayload(q)
        self.assertEqual(body["eventUriList"], "eng-1,eng-2")
        self.assertEqual(body["resultType"], ["events"])


class TestSingleEventAndArticlePayload(PayloadCaptureTestCase):

    def testEventInfoPayload(self):
        path, body = self.execPayload(QueryEvent("eng-123"))
        self.assertEqual(path, "/api/v1/event")
        self.assertEqual(body["action"], "getEvent")
        self.assertEqual(body["eventUri"], "eng-123")
        self.assertEqual(body["resultType"], ["info"])

    def testEventArticlesPayload(self):
        q = QueryEvent("eng-123", requestedResult = RequestEventArticles(
            page = 2, count = 50, keywords = "tesla", lang = "eng", sortBy = "date"))
        path, body = self.execPayload(q)
        self.assertEqual(body["resultType"], ["articles"])
        self.assertEqual(body["articlesPage"], 2)
        self.assertEqual(body["articlesCount"], 50)
        self.assertEqual(body["articlesSortBy"], "date")
        self.assertEqual(body["keyword"], "tesla")
        self.assertEqual(body["lang"], "eng")

    def testArticleInfoPayload(self):
        path, body = self.execPayload(QueryArticle(["uri1", "uri2"]))
        self.assertEqual(path, "/api/v1/article")
        self.assertEqual(body["action"], "getArticle")
        self.assertEqual(body["articleUri"], ["uri1", "uri2"])
        self.assertEqual(body["resultType"], ["info"])

    def testStoryPayload(self):
        q = QueryStory("story-uri-1")
        q.setRequestedResult(RequestStoryArticles(page = 2, count = 50, sortBy = "date"))
        path, body = self.execPayload(q)
        self.assertEqual(path, "/api/v1/story")
        self.assertEqual(body["action"], "getStory")
        self.assertEqual(body["storyUri"], "story-uri-1")
        self.assertEqual(body["resultType"], ["articles"])
        self.assertEqual(body["articlesPage"], 2)
        self.assertEqual(body["articlesCount"], 50)
        self.assertEqual(body["articlesSortBy"], "date")

    def testStoryWithoutResultTypeRaises(self):
        # QueryStory does not set a default result type - executing it must fail with a clear error
        self.assertRaises(ValueError, self.er.execQuery, QueryStory("story-uri-1"))


class TestMentionsQueryPayload(PayloadCaptureTestCase):

    def testDefaultPayload(self):
        path, body = self.execPayload(QueryMentions(keywords = "acquisition"))
        self.assertEqual(path, "/api/v1/eventType/mention")
        self.assertEqual(body["action"], "getMentions")
        self.assertEqual(body["keyword"], "acquisition")
        self.assertEqual(body["resultType"], ["mentions"])
        self.assertEqual(body["mentionsPage"], 1)
        self.assertEqual(body["mentionsCount"], 100)

    def testMentionSpecificConditions(self):
        q = QueryMentions(eventTypeUri = QueryItems.OR(["et/business/acquisitions-mergers", "et/business/investments"]),
                          industryUri = "industry-1",
                          sdgUri = "sdg/goal-7",
                          esgUri = QueryItems.OR(["esg/environment"]),
                          minSentenceIndex = 0, maxSentenceIndex = 3,
                          showDuplicates = True)
        path, body = self.execPayload(q)
        self.assertEqual(body["eventTypeUri"], ["et/business/acquisitions-mergers", "et/business/investments"])
        self.assertEqual(body["industryUri"], "industry-1")
        self.assertEqual(body["sdgUri"], "sdg/goal-7")
        self.assertEqual(body["esgUri"], ["esg/environment"])
        self.assertEqual(body["maxSentenceIndex"], 3)
        self.assertEqual(body["showDuplicates"], True)
        # minSentenceIndex of 0 must still be included (0 is a valid, non-None value)
        self.assertEqual(body["minSentenceIndex"], 0)


class TestOtherEndpointPayloads(PayloadCaptureTestCase):

    def testGetCounts(self):
        path, body = self.execPayload(GetCounts(["uri1", "uri2"], type = "concept"))
        self.assertEqual(path, "/api/v1/counters")
        self.assertEqual(body["action"], "getCounts")
        self.assertEqual(body["type"], "concept")
        self.assertEqual(body["uri"], ["uri1", "uri2"])

    def testGetCountsEx(self):
        path, body = self.execPayload(GetCountsEx("uri1", type = "category"))
        self.assertEqual(body["action"], "getCountsEx")
        self.assertEqual(body["type"], "category")

    def testTrendingConcepts(self):
        path, body = self.execPayload(GetTrendingConcepts(source = "news", count = 10, conceptType = ["person"]))
        self.assertEqual(path, "/api/v1/trends")
        self.assertEqual(body["action"], "getTrendingConcepts")
        self.assertEqual(body["source"], "news")
        self.assertEqual(body["dataType"], "news")
        self.assertEqual(body["conceptCount"], 10)
        self.assertEqual(body["conceptType"], ["person"])

    def testTrendingCategories(self):
        path, body = self.execPayload(GetTrendingCategories(source = "social", count = 15))
        self.assertEqual(body["action"], "getTrendingCategories")
        self.assertEqual(body["source"], "social")
        # for the "social" source no dataType parameter should be sent
        self.assertNotIn("dataType", body)
        self.assertEqual(body["categoryCount"], 15)

    def testSourceInfo(self):
        path, body = self.execPayload(GetSourceInfo("bbc.com"))
        self.assertEqual(path, "/api/v1/source")
        self.assertEqual(body["action"], "getInfo")
        self.assertEqual(body["uri"], "bbc.com")

    def testCategoryInfo(self):
        path, body = self.execPayload(GetCategoryInfo("dmoz/Business"))
        self.assertEqual(path, "/api/v1/category")
        self.assertEqual(body["uri"], "dmoz/Business")

    def testRecentEvents(self):
        gre = GetRecentEvents(self.er, mandatoryLang = "eng", mandatoryLocation = False)
        ret = gre.getUpdates()
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/minuteStreamEvents")
        self.assertEqual(body["recentActivityEventsMandatoryLocation"], False)
        self.assertEqual(body["recentActivityEventsMandatoryLang"], "eng")
        self.assertEqual(ret, {})

    def testRecentArticles(self):
        gra = GetRecentArticles(self.er, articleLang = "eng")
        ret = gra.getUpdates()
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/minuteStreamArticles")
        self.assertEqual(body["recentActivityArticlesLang"], "eng")
        self.assertEqual(ret, [])

    def testEventForText(self):
        gef = GetEventForText(self.er, nrOfEventsToReturn = 3)
        gef.compute("some event text", lang = "deu")
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/getEventForText/getEventForText")
        self.assertEqual(body["text"], "some event text")
        self.assertEqual(body["lang"], "deu")
        self.assertEqual(body["topClustersCount"], 3)


class TestTopicPagePayload(PayloadCaptureTestCase):

    def _makeTopicPage(self):
        tp = TopicPage(self.er)
        tp.addKeyword("solar energy", 30)
        tp.addConcept("http://en.wikipedia.org/wiki/Solar_power", 50, required = True)
        tp.setLanguages(["eng"])
        return tp

    def testGetArticlesPayload(self):
        tp = self._makeTopicPage()
        tp.getArticles(page = 2, count = 30, sortBy = "date")
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/article")
        self.assertEqual(body["action"], "getArticlesForTopicPage")
        self.assertEqual(body["resultType"], "articles")
        self.assertEqual(body["articlesPage"], 2)
        self.assertEqual(body["articlesCount"], 30)
        self.assertEqual(body["articlesSortBy"], "date")
        # the topic page definition is sent as a json string
        definition = json.loads(body["topicPage"])
        self.assertEqual(definition["keywords"], [{"keyword": "solar energy", "wgt": 30, "required": False, "excluded": False}])
        self.assertEqual(definition["concepts"][0]["uri"], "http://en.wikipedia.org/wiki/Solar_power")
        self.assertTrue(definition["concepts"][0]["required"])
        self.assertEqual(definition["langs"], ["eng"])

    def testGetEventsPayload(self):
        tp = self._makeTopicPage()
        tp.getEvents(page = 1, count = 20, sortBy = "size")
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/event")
        self.assertEqual(body["action"], "getEventsForTopicPage")
        self.assertEqual(body["resultType"], "events")
        self.assertEqual(body["eventsCount"], 20)
        self.assertEqual(body["eventsSortBy"], "size")


class TestSuggestPayloads(PayloadCaptureTestCase):

    def testSuggestConcepts(self):
        self.er.suggestConcepts("Oba", lang = "deu", page = 2, count = 10)
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/suggestConceptsFast")
        self.assertEqual(body["prefix"], "Oba")
        self.assertEqual(body["source"], ["concepts"])
        self.assertEqual(body["lang"], "deu")
        self.assertEqual(body["page"], 2)
        self.assertEqual(body["count"], 10)

    def testSuggestCategories(self):
        self.er.suggestCategories("busi")
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/suggestCategoriesFast")
        self.assertEqual(body["prefix"], "busi")

    def testSuggestNewsSources(self):
        self.er.suggestNewsSources("bbc", dataType = "news")
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/suggestSourcesFast")
        self.assertEqual(body["dataType"], "news")
        # default dataType covers all types
        self.er.suggestNewsSources("bbc")
        path, body = self.lastRequest()
        self.assertEqual(body["dataType"], ["news", "pr", "blog"])

    def testSuggestLocationsWithDistanceSort(self):
        self.er.suggestLocations("Lju", sortByDistanceTo = (46.05, 14.5))
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/suggestLocationsFast")
        self.assertEqual(body["closeToLat"], 46.05)
        self.assertEqual(body["closeToLon"], 14.5)
        self.assertEqual(body["source"], ["place", "country"])

    def testSuggestLocationsAtCoordinate(self):
        self.er.suggestLocationsAtCoordinate(38.9, -77.0, 300, limitToCities = True)
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/suggestLocationsFast")
        self.assertEqual(body["action"], "getLocationsAtCoordinate")
        self.assertEqual(body["lat"], 38.9)
        self.assertEqual(body["lon"], -77.0)
        self.assertEqual(body["radius"], 300)
        self.assertEqual(body["limitToCities"], True)

    def testSuggestEventTypesAndIndustries(self):
        self.er.suggestEventTypes("acqui")
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/eventType/suggestEventTypes")
        self.er.suggestIndustries("bank")
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/eventType/suggestIndustries")

    def testSdgAndSasbUris(self):
        self.er.getSdgUris()
        self.assertEqual(self.lastRequest()[0], "/api/v1/eventType/sdg/getItems")
        self.er.getSasbUris()
        self.assertEqual(self.lastRequest()[0], "/api/v1/eventType/sasb/getItems")

    def testUsageInfo(self):
        self.er.getUsageInfo()
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/usage")
        self.assertEqual(body["apiKey"], "TESTKEY")


class TestAnalyticsPayloads(PayloadCaptureTestCase):

    def setUp(self):
        super().setUp()
        self.an = Analytics(self.er)

    def testCategorize(self):
        self.an.categorize("some text", taxonomy = "news", concepts = ["c1", "c2"])
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/categorize")
        self.assertEqual(body["text"], "some text")
        self.assertEqual(body["taxonomy"], "news")
        self.assertEqual(body["concepts"], ["c1", "c2"])
        self.assertEqual(body["apiKey"], "TESTKEY")

    def testDetectLanguage(self):
        self.an.detectLanguage("bonjour tout le monde")
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/detectLanguage")
        self.assertEqual(body["text"], "bonjour tout le monde")

    def testSemanticSimilarity(self):
        self.an.semanticSimilarity("text one", "text two", distanceMeasure = "jaccard")
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/semanticSimilarity")
        self.assertEqual(body["text1"], "text one")
        self.assertEqual(body["text2"], "text two")
        self.assertEqual(body["distanceMeasure"], "jaccard")

    def testNer(self):
        self.an.ner("Barack Obama visited Berlin.")
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/ner")
        self.assertEqual(body["text"], "Barack Obama visited Berlin.")

    def testSentimentDefaults(self):
        self.an.sentiment("some text")
        path, body = self.lastRequest()
        self.assertEqual(path, "/api/v1/sentiment")
        self.assertEqual(body["method"], "vocabulary")
        self.assertEqual(body["sentences"], 10)
        self.assertEqual(body["returnSentences"], True)


if __name__ == "__main__":
    unittest.main(verbosity = 2)
