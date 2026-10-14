"""
Offline unit tests for the eventregistry package.
These tests do NOT make any network requests - the EventRegistry HTTP layer is mocked
where needed. They can therefore run without an API key and without internet access.

Run with:
    python -m unittest eventregistry.tests.TestOfflineUnit -v
"""
import datetime
import inspect
import json
import logging
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import requests

from eventregistry import *


class FakeResponse:
    """minimal stand-in for requests.Response"""
    def __init__(self, status_code = 200, data = None, headers = None, text = ""):
        self.status_code = status_code
        self._data = data if data is not None else {}
        self.headers = headers or {}
        self.text = text

    def json(self):
        return self._data


def makeER(**kwargs):
    """create an EventRegistry instance that never sleeps and never retries forever"""
    kwargs.setdefault("apiKey", "TESTKEY")
    kwargs.setdefault("minDelayBetweenRequests", 0)
    kwargs.setdefault("repeatFailedRequestCount", 0)
    # point to a settings file that does not exist so that the local settings.json is not picked up
    kwargs.setdefault("settingsFName", os.path.join(tempfile.gettempdir(), "er-no-such-settings.json"))
    return EventRegistry(**kwargs)


class TestBaseHelpers(unittest.TestCase):

    def testRemoveInvalidChars(self):
        self.assertEqual(removeInvalidChars("abc"), "abc")
        self.assertEqual(removeInvalidChars("a\x00b\x08c\x0bd\x1fe"), "abcde")
        # tab, newline and carriage return are valid and must be kept
        self.assertEqual(removeInvalidChars("a\tb\nc\rd"), "a\tb\nc\rd")

    def testTryParseInt(self):
        self.assertEqual(tryParseInt("42"), 42)
        self.assertEqual(tryParseInt("notanumber", val = -1), -1)
        self.assertEqual(tryParseInt("", val = -1), -1)

    def testStruct(self):
        s = createStructFromDict({"a": 1, "b": {"c": [1, 2, {"d": "x"}]}})
        self.assertEqual(s.a, 1)
        self.assertEqual(s.b.c[0], 1)
        self.assertEqual(s.b.c[2].d, "x")
        self.assertTrue(s.has("a"))
        self.assertFalse(s.has("nope"))
        lst = createStructFromDict([{"a": 1}, {"a": 2}])
        self.assertEqual([item.a for item in lst], [1, 2])

    def testQueryItems(self):
        andItems = QueryItems.AND(["a", "b"])
        self.assertEqual(andItems.getOper(), "$and")
        self.assertEqual(andItems.getItems(), ["a", "b"])
        orItems = QueryItems.OR(["c"])
        self.assertEqual(orItems.getOper(), "$or")

    def testEncodeDateInvalidValues(self):
        self.assertRaises(ValueError, QueryParamsBase.encodeDate, "01-01-2015")
        self.assertRaises(TypeError, QueryParamsBase.encodeDate, 20150101)
        self.assertRaises(ValueError, QueryParamsBase.encodeDateTime, "2015-01-01")

    def testEncodeDateTimeWithTimezone(self):
        # timezone-aware datetimes must be converted to UTC
        dt = datetime.datetime(2020, 6, 1, 14, 30, 0, tzinfo = datetime.timezone(datetime.timedelta(hours = 2)))
        self.assertTrue(QueryParamsBase.encodeDateTime(dt).startswith("2020-06-01T12:30:00"))


class TestQueryParamAssembly(unittest.TestCase):

    def testSetQueryArrValWithString(self):
        q = QueryParamsBase()
        q._setQueryArrVal("obama", "keyword", "keywordOper", "and")
        self.assertEqual(q.queryParams["keyword"], "obama")
        self.assertNotIn("keywordOper", q.queryParams)

    def testSetQueryArrValWithQueryItems(self):
        q = QueryParamsBase()
        q._setQueryArrVal(QueryItems.OR(["a", "b"]), "conceptUri", "conceptOper", "and")
        self.assertEqual(q.queryParams["conceptUri"], ["a", "b"])
        self.assertEqual(q.queryParams["conceptOper"], "or")

    def testSetQueryArrValWithList(self):
        q = QueryParamsBase()
        q._setQueryArrVal(["a", "b"], "conceptUri", "conceptOper", "and")
        self.assertEqual(q.queryParams["conceptUri"], ["a", "b"])
        self.assertEqual(q.queryParams["conceptOper"], "and")

    def testSetQueryArrValInvalidOperatorDoesNotMutate(self):
        q = QueryParamsBase()
        # "and" operator is invalid when only "or" is allowed (propOperName is None)
        self.assertRaises(ValueError, q._setQueryArrVal, QueryItems.AND(["a", "b"]), "sourceUri", None, "or")
        self.assertNotIn("sourceUri", q.queryParams)

    def testSetQueryArrValNoneAndEmptyIgnored(self):
        q = QueryParamsBase()
        q._setQueryArrVal(None, "keyword", None, "or")
        q._setQueryArrVal("", "keyword", None, "or")
        self.assertEqual(q.queryParams, {})

    def testCopyDoesNotShareState(self):
        q = QueryParamsBase()
        q._setVal("a", 1)
        q2 = QueryParamsBase.copy(q)
        q2._setVal("a", 2)
        self.assertEqual(q.queryParams["a"], 1)

    def testQueryRequiresResultType(self):
        q = Query()
        self.assertRaises(ValueError, q._getQueryParams)


class TestQueryArticlesConstruction(unittest.TestCase):

    def testBasicParams(self):
        q = QueryArticles(keywords = "obama", lang = "eng", dateStart = "2020-01-01", dateEnd = datetime.date(2020, 1, 31))
        params = q._getQueryParams()
        self.assertEqual(params["action"], "getArticles")
        self.assertEqual(params["keyword"], "obama")
        self.assertEqual(params["lang"], "eng")
        self.assertEqual(params["dateStart"], "2020-01-01")
        self.assertEqual(params["dateEnd"], "2020-01-31")
        self.assertEqual(params["resultType"], ["articles"])

    def testDefaultsAreNotSent(self):
        params = QueryArticles(keywords = "x")._getQueryParams()
        for prop in ["isDuplicateFilter", "hasDuplicateFilter", "eventFilter", "startSourceRankPercentile",
                     "endSourceRankPercentile", "minSentiment", "maxSentiment", "dataType", "keywordLoc"]:
            self.assertNotIn(prop, params, "property '%s' should not be included when default" % prop)

    def testNonDefaultsAreSent(self):
        q = QueryArticles(keywords = "x", isDuplicateFilter = "skipDuplicates", minSentiment = -0.5, maxSentiment = 0.5,
                          startSourceRankPercentile = 20, endSourceRankPercentile = 80, dataType = ["news", "pr"])
        params = q._getQueryParams()
        self.assertEqual(params["isDuplicateFilter"], "skipDuplicates")
        self.assertEqual(params["minSentiment"], -0.5)
        self.assertEqual(params["maxSentiment"], 0.5)
        self.assertEqual(params["startSourceRankPercentile"], 20)
        self.assertEqual(params["endSourceRankPercentile"], 80)
        self.assertEqual(params["dataType"], ["news", "pr"])

    def testInvalidPercentilesRejected(self):
        self.assertRaises(ValueError, QueryArticles, startSourceRankPercentile = 15)
        self.assertRaises(ValueError, QueryArticles, startSourceRankPercentile = 50, endSourceRankPercentile = 40)

    def testInitWithArticleUriList(self):
        q = QueryArticles.initWithArticleUriList(["uri1", "uri2"])
        self.assertEqual(q.queryParams["articleUri"], ["uri1", "uri2"])
        self.assertEqual(q.queryParams["dataType"], ["news", "blog", "pr"])
        self.assertRaises(TypeError, QueryArticles.initWithArticleUriList, 123)
        # the iterator gets the returnInfo in execQuery()
        self.assertEqual(QueryArticlesIter.initWithArticleUriList(["uri1"])._getQueryParams()["articleUri"], ["uri1"])
        self.assertRaises(TypeError, QueryArticlesIter.initWithArticleUriList, ["uri1"], returnInfo = ReturnInfo())

    def testInitWithArticleUriWgtList(self):
        q = QueryArticles.initWithArticleUriWgtList(["u1:10", "u2:20"])
        self.assertEqual(q.queryParams["articleUriWgtList"], "u1:10,u2:20")
        self.assertEqual(q.queryParams["dataType"], ["news", "blog", "pr"])
        q = QueryArticles.initWithArticleUriWgtList("u1:10,u2:20")
        self.assertEqual(q.queryParams["articleUriWgtList"], "u1:10,u2:20")

    def testInitWithComplexQuery(self):
        cq = ComplexArticleQuery(BaseQuery(keyword = "abc"))
        q = QueryArticles.initWithComplexQuery(cq)
        self.assertEqual(json.loads(q.queryParams["query"]), {"$query": {"keyword": "abc"}})
        # a valid json string is accepted
        q = QueryArticles.initWithComplexQuery('{"$query": {"keyword": "abc"}}')
        self.assertIn("query", q.queryParams)
        # a dict is accepted
        q = QueryArticles.initWithComplexQuery({"$query": {"keyword": "abc"}})
        self.assertIn("query", q.queryParams)
        # invalid json must raise ValueError
        self.assertRaises(ValueError, QueryArticles.initWithComplexQuery, "{not valid json")
        self.assertRaises(ValueError, QueryArticlesIter.initWithComplexQuery, "{not valid json")


class TestQueryEventsConstruction(unittest.TestCase):

    def testInitWithEventUriList(self):
        q = QueryEvents.initWithEventUriList(["eng-1", "eng-2"])
        self.assertEqual(q.queryParams["eventUriList"], "eng-1,eng-2")
        # a single string uri must NOT be split into characters
        q = QueryEvents.initWithEventUriList("eng-123")
        self.assertEqual(q.queryParams["eventUriList"], "eng-123")

    def testInitWithComplexQueryInvalidJson(self):
        self.assertRaises(ValueError, QueryEvents.initWithComplexQuery, "{bad json")
        self.assertRaises(ValueError, QueryEventsIter.initWithComplexQuery, "{bad json")

    def testRequestEventsInfoBounds(self):
        self.assertRaises(ValueError, RequestEventsInfo, page = 0)
        self.assertRaises(ValueError, RequestEventsInfo, count = 51)


class TestQueryMentionsConstruction(unittest.TestCase):

    def testBasicParams(self):
        q = QueryMentions(keywords = "acquisition", eventTypeUri = "et/business/acquisitions-mergers")
        params = q._getQueryParams()
        self.assertEqual(params["action"], "getMentions")
        self.assertEqual(params["keyword"], "acquisition")
        self.assertEqual(params["eventTypeUri"], "et/business/acquisitions-mergers")

    def testInitWithComplexQueryInvalidJson(self):
        self.assertRaises(ValueError, QueryMentions.initWithComplexQuery, "{bad json")
        self.assertRaises(ValueError, QueryMentionsIter.initWithComplexQuery, "{bad json")

    def testRequestMentionsInfoBounds(self):
        self.assertRaises(ValueError, RequestMentionsInfo, count = 101)


class TestComplexQueryConstruction(unittest.TestCase):

    def testBaseQuery(self):
        q = BaseQuery(keyword = QueryItems.AND(["a", "b"]), lang = "eng", dateStart = "2020-01-01",
                      exclude = BaseQuery(keyword = "spam"))
        obj = q.getQuery()
        self.assertEqual(obj["keyword"], {"$and": ["a", "b"]})
        self.assertEqual(obj["lang"], "eng")
        self.assertEqual(obj["dateStart"], "2020-01-01")
        self.assertEqual(obj["$not"], {"keyword": "spam"})

    def testCombinedQuery(self):
        q = CombinedQuery.OR([BaseQuery(keyword = "a"), BaseQuery(keyword = "b")], exclude = BaseQuery(lang = "deu"))
        obj = q.getQuery()
        self.assertEqual(obj["$or"], [{"keyword": "a"}, {"keyword": "b"}])
        self.assertEqual(obj["$not"], {"lang": "deu"})
        self.assertRaises(ValueError, CombinedQuery.AND, [])
        self.assertRaises(TypeError, CombinedQuery.AND, ["notaquery"])

    def testComplexArticleQueryFilters(self):
        cq = ComplexArticleQuery(BaseQuery(keyword = "x"), minSentiment = -0.4, isDuplicateFilter = "skipDuplicates",
                                 dataType = ["news", "blog"])
        obj = cq.getQuery()
        self.assertEqual(obj["$filter"], {"dataType": ["news", "blog"], "minSentiment": -0.4, "isDuplicate": "skipDuplicates"})
        # no filter key when everything is default
        self.assertNotIn("$filter", ComplexArticleQuery(BaseQuery(keyword = "x")).getQuery())


class TestReturnInfoFlags(unittest.TestCase):

    def testDefaultFlagsAreEmpty(self):
        # when all defaults are used, no flags need to be sent to the API
        self.assertEqual(ReturnInfo().getParams(), {})

    def testNonDefaultFlags(self):
        ri = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 200, concepts = True, image = False))
        params = ri.getParams()
        self.assertEqual(params["articleBodyLen"], 200)
        self.assertEqual(params["includeArticleConcepts"], True)
        self.assertEqual(params["includeArticleImage"], False)

    def testValsPrefixing(self):
        # without a prefix the first letter is lowercased, with a prefix it is uppercased and prepended
        flags = ArticleInfoFlags(bodyLen = 200)
        self.assertEqual(flags._getVals(), {"articleBodyLen": 200})
        self.assertEqual(flags._getVals("articles"), {"articlesArticleBodyLen": 200})

    def testInstancesDoNotShareState(self):
        r1 = ReturnInfo()
        r2 = ReturnInfo()
        self.assertIsNot(r1.articleInfo, r2.articleInfo)
        r1.articleInfo._setFlag("includeArticleConcepts", True, False)
        self.assertNotIn("includeArticleConcepts", r2.articleInfo._getFlags())

    def testKwdArgs(self):
        flags = ArticleInfoFlags(someCustomFlag = True, someCustomVal = 7)
        self.assertEqual(flags._getFlags().get("someCustomFlag"), True)
        self.assertEqual(flags._getVals().get("someCustomVal"), 7)

    def testGetConfUsesCorrectFlagObjects(self):
        ri = ReturnInfo(articleInfo = ArticleInfoFlags(concepts = True),
                        conceptFolderInfo = ConceptFolderInfoFlags(definition = True))
        conf = ri.getConf()
        self.assertIn("includeConceptFolderDefinition", conf["conceptFolderInfo"])
        self.assertNotIn("includeArticleConcepts", conf["conceptFolderInfo"])

    def testSaveAndLoadRoundTrip(self):
        ri = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 100, concepts = True),
                        conceptInfo = ConceptInfoFlags(lang = "spa"))
        fd, fname = tempfile.mkstemp(suffix = ".json")
        os.close(fd)
        try:
            with open(fname, "w", encoding = "utf-8") as f:
                json.dump(ri.getConf(), f)
            loaded = ReturnInfo.loadFromFile(fname)
            self.assertEqual(loaded.getParams(), ri.getParams())
        finally:
            os.remove(fname)


class TestEventRegistryRequests(unittest.TestCase):

    def testCallerParamsNotMutated(self):
        er = makeER()
        er._reqSession.post = mock.Mock(return_value = FakeResponse(data = {"ok": True}))
        params = {"q": "test"}
        ret = er.jsonRequest("/api/v1/test", params)
        self.assertEqual(ret, {"ok": True})
        self.assertEqual(params, {"q": "test"}, "the caller's parameter dict must not be modified")
        # but the api key must be included in the actual request
        sentJson = er._reqSession.post.call_args.kwargs["json"]
        self.assertEqual(sentJson["apiKey"], "TESTKEY")

    def testAnalyticsCallerParamsNotMutated(self):
        er = makeER()
        er._reqSession.post = mock.Mock(return_value = FakeResponse(data = {"ok": True}))
        params = {"text": "hello"}
        er.jsonRequestAnalytics("/api/v1/annotate", params)
        self.assertEqual(params, {"text": "hello"})

    def testArchiveFlag(self):
        er = makeER(allowUseOfArchive = False)
        er._reqSession.post = mock.Mock(return_value = FakeResponse(data = {}))
        er.jsonRequest("/api/v1/test", {})
        self.assertEqual(er._reqSession.post.call_args.kwargs["json"]["forceMaxDataTimeWindow"], 31)
        # per-request override wins
        er.jsonRequest("/api/v1/test", {}, allowUseOfArchive = True)
        self.assertNotIn("forceMaxDataTimeWindow", er._reqSession.post.call_args.kwargs["json"])

    def testFailedRequestRaisesAndReleasesLock(self):
        er = makeER()
        er._reqSession.post = mock.Mock(return_value = FakeResponse(status_code = 400, text = "bad request"))
        self.assertRaises(Exception, er.jsonRequest, "/api/v1/test", {})
        # the lock must be free again after the failure
        self.assertTrue(er._lock.acquire(timeout = 1), "lock was not released after a failed request")
        er._lock.release()

    def testStopStatusCodesDoNotRetry(self):
        er = makeER(repeatFailedRequestCount = 5)
        er._reqSession.post = mock.Mock(return_value = FakeResponse(status_code = 401, text = "limit"))
        self.assertRaises(Exception, er.jsonRequest, "/api/v1/test", {})
        self.assertEqual(er._reqSession.post.call_count, 1, "401 responses must not be retried")

    def testAllStopStatusCodesDoNotRetry(self):
        for code in [204, 400, 401, 403]:
            er = makeER(repeatFailedRequestCount = 5)
            er._reqSession.post = mock.Mock(return_value = FakeResponse(status_code = code, text = "err"))
            with mock.patch("eventregistry.EventRegistry.time.sleep"):
                self.assertRaises(Exception, er.jsonRequest, "/api/v1/test", {})
            self.assertEqual(er._reqSession.post.call_count, 1, "%d responses must not be retried" % code)

    def testTemporaryStatusCodesAreRetried(self):
        for code in [429, 500, 503]:
            er = makeER(repeatFailedRequestCount = 3)
            er._reqSession.post = mock.Mock(side_effect = [FakeResponse(status_code = code, text = "err"), FakeResponse(data = {"ok": 1})])
            with mock.patch("eventregistry.EventRegistry.time.sleep") as sleep:
                self.assertEqual(er.jsonRequest("/api/v1/test", {}), {"ok": 1})
            self.assertEqual(er._reqSession.post.call_count, 2, "%d responses should be retried" % code)
            self.assertTrue(sleep.called, "the request should be repeated only after a delay")

    def testAnalyticsTemporaryStatusCodeIsRetried(self):
        er = makeER(repeatFailedRequestCount = 3)
        er._reqSession.post = mock.Mock(side_effect = [FakeResponse(status_code = 503, text = "down"), FakeResponse(data = {"ok": 1})])
        with mock.patch("eventregistry.EventRegistry.time.sleep"):
            self.assertEqual(er.jsonRequestAnalytics("/api/v1/test", {}), {"ok": 1})
        self.assertEqual(er._reqSession.post.call_count, 2)

    def testErrorMessageContainsStatusCodeAndMeaning(self):
        er = makeER()
        er._reqSession.post = mock.Mock(return_value = FakeResponse(status_code = 503, text = "maintenance"))
        with mock.patch("eventregistry.EventRegistry.time.sleep"):
            with self.assertRaises(Exception) as ctx:
                er.jsonRequest("/api/v1/test", {})
        msg = str(ctx.exception)
        self.assertIn("503", msg)
        self.assertIn("Service unavailable", msg)
        self.assertIn("maintenance", msg)

    def testRateLimitHeadersParsed(self):
        er = makeER()
        headers = {"x-ratelimit-limit": "5000", "x-ratelimit-remaining": "1234"}
        er._reqSession.post = mock.Mock(return_value = FakeResponse(data = {}, headers = headers))
        er.jsonRequest("/api/v1/test", {})
        self.assertEqual(er.getDailyAvailableRequests(), 5000)
        self.assertEqual(er.getRemainingAvailableRequests(), 1234)
        self.assertEqual(er.getLastHeader("x-ratelimit-limit"), "5000")

    def testExtraParams(self):
        er = makeER()
        er.setExtraParams({"custom": "val"})
        er._reqSession.post = mock.Mock(return_value = FakeResponse(data = {}))
        er.jsonRequest("/api/v1/test", {})
        self.assertEqual(er._reqSession.post.call_args.kwargs["json"]["custom"], "val")

    def testGetUrl(self):
        er = makeER()
        url = er.getUrl(QueryArticles(keywords = "obama"))
        self.assertTrue(url.startswith("https://eventregistry.org/api/v1/article?"))
        self.assertIn("keyword=obama", url)

    def testGetUriFromUriWgt(self):
        self.assertEqual(EventRegistry.getUriFromUriWgt(["uri1:100", "uri2:50"]), ["uri1", "uri2"])
        self.assertRaises(TypeError, EventRegistry.getUriFromUriWgt, "uri1:100")

    def testRequestLogDefaultsToUserFolder(self):
        er = makeER()
        self.assertEqual(er._requestLogFName, os.path.join(os.path.expanduser("~"), ".eventregistry", "requests_log.txt"))

    def testExecQueryRequiresQueryObject(self):
        er = makeER()
        self.assertRaises(TypeError, er.execQuery, {"not": "a query"})

    def testGetArticleUrisAcceptsOnlySingleUrl(self):
        er = makeER()
        er.jsonRequest = mock.Mock(return_value = {"http://x.com/1": "uri-1"})
        self.assertEqual(er.getArticleUris("http://x.com/1"), {"http://x.com/1": "uri-1"})
        er.jsonRequest.assert_called_once_with("/api/v1/articleMapper", {"articleUrl": "http://x.com/1"})
        self.assertRaises(TypeError, er.getArticleUris, ["http://x.com/1", "http://x.com/2"])

    def testArticleMapperCachesResults(self):
        er = makeER()
        er.getArticleUris = mock.Mock(return_value = {"http://x.com/1": "uri-1"})
        mapper = ArticleMapper(er)
        self.assertEqual(mapper.getArticleUri("http://x.com/1"), "uri-1")
        self.assertEqual(mapper.getArticleUri("http://x.com/1"), "uri-1")
        self.assertEqual(er.getArticleUris.call_count, 1, "repeated lookups should be served from the cache")


class TestIterators(unittest.TestCase):

    def _makeArticlePage(self, uris, pages):
        return {"articles": {"results": [{"uri": u} for u in uris], "pages": pages, "totalResults": len(uris)}}

    def testArticleIteratorPagesThroughResults(self):
        er = makeER()
        responses = [self._makeArticlePage(["a1", "a2"], 2), self._makeArticlePage(["a3"], 2)]
        er.execQuery = mock.Mock(side_effect = responses)
        it = QueryArticlesIter(keywords = "x").execQuery(er)
        self.assertEqual([a["uri"] for a in it], ["a1", "a2", "a3"])
        self.assertEqual(er.execQuery.call_count, 2)

    def testArticleIteratorMaxItems(self):
        er = makeER()
        er.execQuery = mock.Mock(return_value = self._makeArticlePage(["a1", "a2", "a3"], 1))
        it = QueryArticlesIter(keywords = "x").execQuery(er, maxItems = 2)
        self.assertEqual([a["uri"] for a in it], ["a1", "a2"])

    def testIteratorsRaiseErrorReturnedByServer(self):
        # an error returned by the server must not look like a query without results
        for query in [QueryArticlesIter(keywords = "x"), QueryEventsIter(keywords = "x"), QueryMentionsIter(keywords = "x"), QueryEventArticlesIter("eng-1")]:
            er = makeER()
            er.execQuery = mock.Mock(return_value = {"error": "something went wrong"})
            with self.assertRaises(QueryError) as ctx:
                list(query.execQuery(er))
            self.assertIn("something went wrong", str(ctx.exception))
            self.assertIsInstance(ctx.exception, EventRegistryError)
            self.assertRaises(QueryError, query.count, er)

    def testExecQueryRaiseOnError(self):
        er = makeER()
        er._reqSession.post = mock.Mock(return_value = FakeResponse(data = {"error": "invalid uri"}))
        # by default the response with the error is returned
        self.assertEqual(er.execQuery(QueryArticles(keywords = "x")), {"error": "invalid uri"})
        self.assertRaises(QueryError, er.execQuery, QueryArticles(keywords = "x"), raiseOnError = True)

    def testIteratorDoesNotChangeTheQuery(self):
        er = makeER()
        er.execQuery = mock.Mock(side_effect = [self._makeArticlePage(["a1", "a2"], 2), self._makeArticlePage(["a3"], 2)])
        q = QueryArticlesIter(keywords = "x")
        before = (repr(q), list(q.resultTypeList))
        self.assertEqual(len(list(q.execQuery(er))), 3)
        self.assertEqual((repr(q), list(q.resultTypeList)), before, "iterating must not change the query")
        # each page was requested with its own copy of the query
        pages = [c.args[0]._getQueryParams()["articlesPage"] for c in er.execQuery.call_args_list]
        self.assertEqual(pages, [1, 2])

    def testIteratorsOfTheSameQueryAreIndependent(self):
        er = makeER()
        def respond(query, *args, **kwargs):
            page = query._getQueryParams()["articlesPage"]
            return self._makeArticlePage(["p%d-a" % page, "p%d-b" % page], 2)
        er.execQuery = mock.Mock(side_effect = respond)
        q = QueryArticlesIter(keywords = "x")
        it1, it2 = q.execQuery(er), q.execQuery(er)
        self.assertIsNot(it1, it2)
        expected = ["p1-a", "p1-b", "p2-a", "p2-b"]
        # interleave the two iterations: start the first one, run the second one to the end, then finish the first one
        got1 = [next(it1)["uri"]]
        got2 = [a["uri"] for a in it2]
        got1 += [next(it1)["uri"] for _ in range(3)]
        self.assertEqual(got1, expected)
        self.assertEqual(got2, expected)
        self.assertRaises(StopIteration, next, it1)

    def testIteratingOverTheQueryStillWorks(self):
        # compatibility: after execQuery() the query object itself can be iterated
        er = makeER()
        er.execQuery = mock.Mock(return_value = self._makeArticlePage(["a1", "a2"], 1))
        q = QueryArticlesIter(keywords = "x")
        q.execQuery(er)
        self.assertEqual([a["uri"] for a in q], ["a1", "a2"])

    def testExecQueryRejectsUnknownArguments(self):
        er = makeER()
        for query in [QueryArticlesIter(keywords = "x"), QueryEventsIter(keywords = "x"), QueryMentionsIter(keywords = "x"), QueryEventArticlesIter("eng-1")]:
            self.assertRaises(TypeError, query.execQuery, er, sortby = "date")
        self.assertRaises(TypeError, RequestEventArticles, keyword = "x")

    def testEventArticlesIteratorKeepsOperatorsAndConditions(self):
        er = makeER()
        er.execQuery = mock.Mock(return_value = {"eng-1": {"articles": {"results": [{"uri": "a1"}], "pages": 1, "totalResults": 1}}})
        q = QueryEventArticlesIter("eng-1", conceptUri = QueryItems.OR(["c1", "c2"]), categoryUri = QueryItems.AND(["cat1", "cat2"]),
                                   keywords = "tesla", lang = "eng")
        with self.assertLogs("eventregistry", level = "WARNING") as logs:
            logging.getLogger("eventregistry").warning("marker")
            list(q.execQuery(er, sortBy = "date"))
            q.count(er)
        self.assertEqual(len(logs.output), 1, "no warning about the operators should be logged: %s" % logs.output)
        for call in er.execQuery.call_args_list:
            params = call.args[0]._getQueryParams()
            self.assertEqual(params["conceptUri"], ["c1", "c2"])
            self.assertEqual(params["conceptOper"], "or", "the OR operator must not be replaced by the default AND")
            self.assertEqual(params["categoryOper"], "and")
            self.assertEqual(params["keyword"], "tesla")
            self.assertEqual(params["articlesLang"], "eng")
        self.assertEqual(er.execQuery.call_args_list[0].args[0]._getQueryParams()["articlesSortBy"], "date")

    def testArticleIteratorCount(self):
        er = makeER()
        er.execQuery = mock.Mock(return_value = {"articles": {"results": [], "pages": 1, "totalResults": 512}})
        self.assertEqual(QueryArticlesIter(keywords = "x").count(er), 512)

    def testArticleIteratorCountKeepsRequestedResult(self):
        er = makeER()
        er.execQuery = mock.Mock(return_value = {"articles": {"results": [], "pages": 1, "totalResults": 5}})
        q = QueryArticlesIter(keywords = "x")
        q.setRequestedResult(RequestArticlesConceptAggr())
        q.count(er)
        self.assertIsInstance(q.resultTypeList[0], RequestArticlesConceptAggr, "count() should not overwrite the requested result type")

    def testArticleIteratorCanBeIteratedTwice(self):
        er = makeER()
        responses = [self._makeArticlePage(["a1", "a2"], 1), self._makeArticlePage(["a1", "a2"], 1)]
        er.execQuery = mock.Mock(side_effect = responses)
        it = QueryArticlesIter(keywords = "x").execQuery(er)
        self.assertEqual([a["uri"] for a in it], ["a1", "a2"])
        self.assertEqual([a["uri"] for a in it], ["a1", "a2"], "a second iteration should re-execute the query and return the results again")

    def testArticleIteratorRequiresExecQuery(self):
        self.assertRaises(RuntimeError, iter, QueryArticlesIter(keywords = "x"))

    def testEventIteratorPagesThroughResults(self):
        er = makeER()
        responses = [
            {"events": {"results": [{"uri": "e1"}], "pages": 2, "totalResults": 2}},
            {"events": {"results": [{"uri": "e2"}], "pages": 2, "totalResults": 2}},
        ]
        er.execQuery = mock.Mock(side_effect = responses)
        it = QueryEventsIter(keywords = "x").execQuery(er)
        self.assertEqual([e["uri"] for e in it], ["e1", "e2"])

    def testMentionsIteratorPagesThroughResults(self):
        er = makeER()
        responses = [
            {"mentions": {"results": [{"uri": "m1"}, {"uri": "m2"}], "pages": 1, "totalResults": 2}},
        ]
        er.execQuery = mock.Mock(side_effect = responses)
        it = QueryMentionsIter(keywords = "x").execQuery(er)
        self.assertEqual([m["uri"] for m in it], ["m1", "m2"])

    def testEventArticlesIterator(self):
        er = makeER()
        responses = [
            {"eng-1": {"articles": {"results": [{"uri": "a1"}], "pages": 1, "totalResults": 1}}},
        ]
        er.execQuery = mock.Mock(side_effect = responses)
        it = QueryEventArticlesIter("eng-1").execQuery(er)
        self.assertEqual([a["uri"] for a in it], ["a1"])


class TestTopicPageDefinition(unittest.TestCase):

    def setUp(self):
        self.tp = TopicPage(eventRegistry = None)

    def testArticleIsDuplicateFilterUsesCorrectKey(self):
        self.tp.setArticleIsDuplicateFilter("keepAll")
        self.assertEqual(self.tp.topicPage["articleIsDuplicate"], "keepAll")
        self.assertNotIn("isDuplicateFilter", self.tp.topicPage)
        self.assertRaises(ValueError, self.tp.setArticleIsDuplicateFilter, "bogusValue")

    def testAddConcept(self):
        self.tp.addConcept("http://en.wikipedia.org/wiki/Apple_Inc.", 30, label = "Apple", required = True)
        concept = self.tp.topicPage["concepts"][0]
        self.assertEqual(concept["uri"], "http://en.wikipedia.org/wiki/Apple_Inc.")
        self.assertEqual(concept["wgt"], 30)
        self.assertEqual(concept["label"], "Apple")
        self.assertTrue(concept["required"])
        # required and excluded cannot both be set
        self.assertRaises(ValueError, self.tp.addConcept, "uri", 10, required = True, excluded = True)

    def testAddKeywordAndCategory(self):
        self.tp.addKeyword("iphone", 20)
        self.assertEqual(self.tp.topicPage["keywords"][0]["keyword"], "iphone")
        self.tp.addCategory("dmoz/Business", 15, excluded = True)
        self.assertTrue(self.tp.topicPage["categories"][0]["excluded"])
        self.assertRaises(ValueError, self.tp.addKeyword, "", 10)

    def testLanguageValidation(self):
        self.tp.setLanguages("eng")
        self.assertEqual(self.tp.topicPage["langs"], ["eng"])
        self.tp.setLanguages(["eng", "deu"])
        self.assertEqual(self.tp.topicPage["langs"], ["eng", "deu"])
        self.assertRaises(ValueError, self.tp.setLanguages, "english")

    def testSourceRankPercentileValidation(self):
        self.tp.setSourceRankPercentile(10, 60)
        self.assertEqual(self.tp.topicPage["startSourceRankPercentile"], 10)
        self.assertEqual(self.tp.topicPage["endSourceRankPercentile"], 60)
        self.assertRaises(ValueError, self.tp.setSourceRankPercentile, 15, 60)
        self.assertRaises(ValueError, self.tp.setSourceRankPercentile, 60, 40)

    def testSaveAndLoadDefinitionRoundTrip(self):
        self.tp.addKeyword("solar", 25)
        self.tp.setMaxDaysBack(14)
        fd, fname = tempfile.mkstemp(suffix = ".json")
        os.close(fd)
        try:
            self.tp.saveTopicPageDefinitionToFile(fname)
            tp2 = TopicPage(eventRegistry = None)
            tp2.loadTopicPageFromFile(fname)
            self.assertEqual(tp2.topicPage, self.tp.topicPage)
        finally:
            os.remove(fname)


class TestRequestClasses(unittest.TestCase):

    def testRequestArticlesInfoBounds(self):
        self.assertRaises(ValueError, RequestArticlesInfo, page = 0)
        self.assertRaises(ValueError, RequestArticlesInfo, count = 101)
        req = RequestArticlesInfo(page = 2, count = 50, sortBy = "date")
        self.assertEqual(req.resultType, "articles")
        self.assertEqual(req.articlesPage, 2)
        self.assertEqual(req.articlesCount, 50)
        req.setPage(5)
        self.assertEqual(req.articlesPage, 5)

    def testRequestArticlesReturnInfoFlagsApplied(self):
        req = RequestArticlesInfo(returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(concepts = True)))
        self.assertTrue(getattr(req, "includeArticleConcepts"))

    def testRequestArticlesRecentActivityExclusiveParams(self):
        self.assertRaises(ValueError, RequestArticlesRecentActivity,
                          updatesAfterTm = "2020-01-01T00:00:00", updatesAfterMinsAgo = 10)
        req = RequestArticlesRecentActivity(updatesAfterMinsAgo = 10)
        self.assertEqual(req.recentActivityArticlesUpdatesAfterMinsAgo, 10)

    def testRequestEventArticlesForwardsFilters(self):
        req = RequestEventArticles(keywords = "tesla", lang = "eng")
        self.assertEqual(req.resultType, "articles")
        self.assertEqual(req.keyword, "tesla")
        self.assertEqual(req.lang, "eng")
        # queryParams must have been merged into the object and removed
        self.assertFalse(hasattr(req, "queryParams"))

    def testResultTypesAreSet(self):
        self.assertEqual(RequestArticlesUriWgtList().resultType, "uriWgtList")
        self.assertEqual(RequestArticlesTimeAggr().resultType, "timeAggr")
        self.assertEqual(RequestArticlesConceptAggr().resultType, "conceptAggr")
        self.assertEqual(RequestEventsUriWgtList().resultType, "uriWgtList")
        self.assertEqual(RequestEventsConceptAggr().resultType, "conceptAggr")
        self.assertEqual(RequestEventInfo().resultType, "info")
        self.assertEqual(RequestMentionsInfo().resultType, "mentions")
        self.assertEqual(RequestStoryInfo().resultType, "info")
        self.assertEqual(RequestArticleInfo().resultType, "info")


class TestAnalyticsParamAssembly(unittest.TestCase):

    def _makeAnalytics(self):
        er = makeER()
        er.jsonRequestAnalytics = mock.Mock(return_value = {})
        return er, Analytics(er)

    def testAnnotate(self):
        er, an = self._makeAnalytics()
        an.annotate("some text", lang = "eng", customParams = {"extra": 1})
        url, params = er.jsonRequestAnalytics.call_args.args
        self.assertEqual(url, "/api/v1/annotate")
        self.assertEqual(params["text"], "some text")
        self.assertEqual(params["lang"], "eng")
        self.assertEqual(params["extra"], 1)

    def testSentimentValidatesMethod(self):
        er, an = self._makeAnalytics()
        self.assertRaises(ValueError, an.sentiment, "text", method = "bogus")
        an.sentiment("text", method = "rnn")
        url, params = er.jsonRequestAnalytics.call_args.args
        self.assertEqual(params["method"], "rnn")

    def testExtractArticleInfoSerializesHeadersAndCookies(self):
        er, an = self._makeAnalytics()
        an.extractArticleInfo("http://x.com", headers = {"User-Agent": "test"}, cookies = {"a": "b"})
        url, params = er.jsonRequestAnalytics.call_args.args
        self.assertEqual(json.loads(params["headers"]), {"User-Agent": "test"})
        self.assertEqual(json.loads(params["cookies"]), {"a": "b"})


class InvalidJsonResponse(FakeResponse):
    def json(self):
        raise ValueError("Expecting value: line 1 column 1 (char 0)")


class TestRequestErrorsAndRetries(unittest.TestCase):

    def testStatusCodesRaiseTypedErrors(self):
        expected = {204: NoDataError, 400: InvalidRequestError, 404: InvalidRequestError, 401: UnauthorizedError,
                    403: ForbiddenError, 500: ServerError, 503: ServerError}
        # 429 is repeated until the request succeeds, so it is never raised by jsonRequest
        self.assertIsInstance(makeER()._getErrorForResponse(FakeResponse(status_code = 429, text = "slow down"), "url"), RateLimitError)
        for code, errorClass in expected.items():
            er = makeER()
            er._reqSession.post = mock.Mock(return_value = FakeResponse(status_code = code, text = "server says no"))
            with mock.patch("eventregistry.EventRegistry.time.sleep"):
                with self.assertRaises(errorClass) as ctx:
                    er.jsonRequest("/api/v1/test", {})
            err = ctx.exception
            self.assertIsInstance(err, EventRegistryError)
            self.assertEqual(err.statusCode, code)
            self.assertEqual(err.responseText, "server says no")
            self.assertEqual(err.url, "https://eventregistry.org/api/v1/test")
            self.assertIs(er.getLastException(), err)
        self.assertTrue(issubclass(UnauthorizedError, AccessError) and issubclass(ForbiddenError, AccessError))

    def testPermanentErrorsAreNotRetried(self):
        for code in [204, 400, 401, 403, 404, 405, 413, 422]:
            er = makeER(repeatFailedRequestCount = 5)
            er._reqSession.post = mock.Mock(return_value = FakeResponse(status_code = code, text = "err"))
            with mock.patch("eventregistry.EventRegistry.time.sleep") as sleep:
                self.assertRaises(EventRegistryError, er.jsonRequest, "/api/v1/test", {})
            self.assertEqual(er._reqSession.post.call_count, 1, "%d responses must not be retried" % code)
            self.assertFalse(sleep.called)

    def testNetworkErrorIsRetriedAndRaisedAsNetworkError(self):
        er = makeER(repeatFailedRequestCount = 2)
        er._reqSession.post = mock.Mock(side_effect = requests.exceptions.ConnectionError("connection refused"))
        with mock.patch("eventregistry.EventRegistry.time.sleep"):
            with self.assertRaises(NetworkError) as ctx:
                er.jsonRequest("/api/v1/test", {})
        self.assertEqual(er._reqSession.post.call_count, 3)
        self.assertIsInstance(ctx.exception.__cause__, requests.exceptions.ConnectionError)
        # a timeout is a network error too and the request succeeds when it is repeated
        er = makeER(repeatFailedRequestCount = 2)
        er._reqSession.post = mock.Mock(side_effect = [requests.exceptions.ReadTimeout("timed out"), FakeResponse(data = {"ok": 1})])
        with mock.patch("eventregistry.EventRegistry.time.sleep"):
            self.assertEqual(er.jsonRequest("/api/v1/test", {}), {"ok": 1})

    def testInvalidJsonIsRetriedAndRaisedAsInvalidResponseError(self):
        er = makeER(repeatFailedRequestCount = 1)
        er._reqSession.post = mock.Mock(return_value = InvalidJsonResponse(text = "<html>truncated"))
        with mock.patch("eventregistry.EventRegistry.time.sleep"):
            self.assertRaises(InvalidResponseError, er.jsonRequest, "/api/v1/test", {})
        self.assertEqual(er._reqSession.post.call_count, 2)

    def testRetriesAreLimitedAndUseExponentialBackoff(self):
        er = makeER(repeatFailedRequestCount = 3)
        er._reqSession.post = mock.Mock(return_value = FakeResponse(status_code = 503, text = "down"))
        with mock.patch("eventregistry.EventRegistry.time.sleep") as sleep:
            self.assertRaises(ServerError, er.jsonRequest, "/api/v1/test", {})
        self.assertEqual(er._reqSession.post.call_count, 4)
        # no sleep after the last attempt
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [2, 4, 8])

    def testRetryAfterHeaderIsUsed(self):
        er = makeER(repeatFailedRequestCount = 1)
        er._reqSession.post = mock.Mock(side_effect = [FakeResponse(status_code = 429, text = "slow down", headers = {"Retry-After": "7"}),
                                                       FakeResponse(data = {"ok": 1})])
        with mock.patch("eventregistry.EventRegistry.time.sleep") as sleep:
            self.assertEqual(er.jsonRequest("/api/v1/test", {}), {"ok": 1})
        self.assertEqual(sleep.call_args.args[0], 7)

    def testTooManySimultaneousRequestsAreAlwaysRepeated(self):
        # 429 is repeated until it succeeds, also when the other errors are not repeated at all
        er = makeER(repeatFailedRequestCount = 0)
        er._reqSession.post = mock.Mock(side_effect = [FakeResponse(status_code = 429, text = "slow down")] * 6 + [FakeResponse(data = {"ok": 1})])
        with mock.patch("eventregistry.EventRegistry.time.sleep") as sleep:
            with self.assertLogs("eventregistry", level = "WARNING"):
                self.assertEqual(er.jsonRequest("/api/v1/test", {}), {"ok": 1})
        self.assertEqual(er._reqSession.post.call_count, 7)
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [2, 4, 8, 16, 32, 60])
        # the repeats of 429 don't count towards repeatFailedRequestCount
        er = makeER(repeatFailedRequestCount = 1)
        er._reqSession.post = mock.Mock(side_effect = [FakeResponse(status_code = 503, text = "down"), FakeResponse(status_code = 429, text = "slow down"),
                                                       FakeResponse(status_code = 429, text = "slow down"), FakeResponse(data = {"ok": 1})])
        with mock.patch("eventregistry.EventRegistry.time.sleep"):
            self.assertEqual(er.jsonRequest("/api/v1/test", {}), {"ok": 1})
        er = makeER(repeatFailedRequestCount = 1)
        er._reqSession.post = mock.Mock(side_effect = [FakeResponse(status_code = 503, text = "down"), FakeResponse(status_code = 429, text = "slow down"),
                                                       FakeResponse(status_code = 503, text = "down")])
        with mock.patch("eventregistry.EventRegistry.time.sleep"):
            self.assertRaises(ServerError, er.jsonRequest, "/api/v1/test", {})
        self.assertEqual(er._reqSession.post.call_count, 3)

    def testIterationContinuesAfterTooManySimultaneousRequests(self):
        er = makeER(repeatFailedRequestCount = 0)
        page = lambda uris: FakeResponse(data = {"articles": {"results": [{"uri": u} for u in uris], "totalResults": 4, "pages": 2}})
        er._reqSession.post = mock.Mock(side_effect = [page(["1", "2"]), FakeResponse(status_code = 429, text = "slow down"), page(["3", "4"])])
        q = QueryArticlesIter(keywords = "x")
        with mock.patch("eventregistry.EventRegistry.time.sleep"), self.assertLogs("eventregistry", level = "WARNING"):
            uris = [a["uri"] for a in q.execQuery(er, maxItems = 4)]
        self.assertEqual(uris, ["1", "2", "3", "4"])

    def testDefaultRetryCountIsLimited(self):
        default = inspect.signature(EventRegistry.__init__).parameters["repeatFailedRequestCount"].default
        self.assertEqual(default, 3, "failed requests should not be repeated indefinitely by default")

    def testLockIsNotHeldWhileWaitingToRetry(self):
        er = makeER(repeatFailedRequestCount = 1)
        er._reqSession.post = mock.Mock(side_effect = [FakeResponse(status_code = 503, text = "down"), FakeResponse(data = {"ok": 1})])
        lockFreeDuringSleep = []
        def fakeSleep(secs):
            gotLock = er._lock.acquire(blocking = False)
            lockFreeDuringSleep.append(gotLock)
            if gotLock:
                er._lock.release()
        with mock.patch("eventregistry.EventRegistry.time.sleep", side_effect = fakeSleep):
            er.jsonRequest("/api/v1/test", {})
        self.assertEqual(lockFreeDuringSleep, [True])

    def testApiKeyIsMaskedInVerboseLogs(self):
        er = makeER(verboseOutput = True, apiKey = "SECRETKEY123")
        er._reqSession.post = mock.Mock(return_value = FakeResponse(status_code = 400, text = "bad"))
        with self.assertLogs("eventregistry", level = "ERROR") as logs:
            self.assertRaises(InvalidRequestError, er.jsonRequest, "/api/v1/test", {"keyword": "x"})
        output = "\n".join(logs.output)
        self.assertNotIn("SECRETKEY123", output)
        self.assertIn('"apiKey": "***"', output)
        self.assertIn('"keyword": "x"', output)
        # the key is still sent to the server
        self.assertEqual(er._reqSession.post.call_args.kwargs["json"]["apiKey"], "SECRETKEY123")

    def testProxyCredentialsAreMaskedInVerboseLogs(self):
        er = makeER(verboseOutput = True)
        er._reqSession.post = mock.Mock(return_value = FakeResponse(status_code = 400, text = "bad"))
        with self.assertLogs("eventregistry", level = "ERROR") as logs:
            self.assertRaises(InvalidRequestError, er.jsonRequestAnalytics, "/api/v1/extractArticleInfo", {"proxyUrl": "http://user:pass@1.2.3.4:8080"})
        output = "\n".join(logs.output)
        self.assertNotIn("user:pass", output)
        self.assertIn("http://***@1.2.3.4:8080", output)
        self.assertNotIn("TESTKEY", output)


class TestSmallFixes(unittest.TestCase):

    def testEmptyListIsIgnored(self):
        params = QueryArticles(keywords = "x", conceptUri = [], sourceUri = QueryItems.OR([]), categoryUri = QueryItems.AND([])).queryParams
        for name in ["conceptUri", "conceptOper", "sourceUri", "sourceOper", "categoryUri", "categoryOper"]:
            self.assertNotIn(name, params)
        self.assertEqual(params["keyword"], "x")

    def testTopicPageDefinitionIsMergedWithDefaults(self):
        er = makeER()
        er.jsonRequest = mock.Mock(return_value = {"articles": {"results": []}, "events": {"results": []}})
        definition = {"concepts": [{"uri": "http://en.wikipedia.org/wiki/Tesla,_Inc.", "wgt": 50}]}
        topic = TopicPage(er)
        topic.loadTopicPageFromDefinition(definition)
        topic.getArticles()
        topic.getEvents()
        self.assertEqual(er.jsonRequest.call_args_list[0].args[1]["dataType"], ["news"])
        self.assertEqual(topic.topicPage["concepts"], definition["concepts"])
        self.assertNotIn("dataType", definition, "the provided definition must not be changed")
        # the same for a definition loaded from a file
        fname = os.path.join(tempfile.gettempdir(), "er-test-topicpage.json")
        with open(fname, "w", encoding = "utf-8") as f:
            json.dump(definition, f)
        topic = TopicPage(er)
        topic.loadTopicPageFromFile(fname)
        topic.getArticles()
        os.remove(fname)

    def testDateTimesAreSentAsUtcWithoutOffset(self):
        encode = QueryParamsBase.encodeDateTime
        tz = datetime.timezone(datetime.timedelta(hours = -5))
        self.assertEqual(encode(datetime.datetime(2026, 10, 1, 23, 30, tzinfo = tz)), "2026-10-02T04:30:00")
        self.assertEqual(encode(datetime.datetime(2026, 10, 1, 23, 30, tzinfo = datetime.timezone.utc)), "2026-10-01T23:30:00")
        # without a timezone the value is considered to be in UTC
        self.assertEqual(encode(datetime.datetime(2026, 10, 1, 23, 30)), "2026-10-01T23:30:00")
        self.assertEqual(encode("2026-10-01T10:00:00"), "2026-10-01T10:00:00")
        self.assertEqual(encode("2026-10-01T10:00:00.123"), "2026-10-01T10:00:00.123")
        self.assertEqual(encode("2026-10-01T10:00:00Z"), "2026-10-01T10:00:00")
        self.assertEqual(encode("2026-10-01T10:00:00+02:00"), "2026-10-01T08:00:00")
        self.assertEqual(encode("2026-10-01T01:00:00+0200"), "2026-09-30T23:00:00")
        self.assertRaises(ValueError, encode, "2026-10-01 10:00:00")

    def testDateOfDateTimeWithTimezoneIsInUtc(self):
        tz = datetime.timezone(datetime.timedelta(hours = -5))
        self.assertEqual(QueryParamsBase.encodeDate(datetime.datetime(2026, 10, 1, 23, 30, tzinfo = tz)), "2026-10-02")
        self.assertEqual(QueryParamsBase.encodeDate(datetime.datetime(2026, 10, 1, 23, 30)), "2026-10-01")
        self.assertEqual(QueryParamsBase.encodeDate(datetime.date(2026, 10, 1)), "2026-10-01")

    def testReturnInfoFlagsRejectMisspelledNames(self):
        self.assertRaises(TypeError, ArticleInfoFlags, bodylen = -1)
        self.assertRaises(TypeError, EventInfoFlags, Title = True)
        # unknown names are still sent to the server (new flags), but with a warning
        with self.assertLogs("eventregistry", level = "WARNING") as logs:
            flags = ArticleInfoFlags(someNewFlag = True)
        self.assertEqual(flags._getFlags().get("someNewFlag"), True)
        self.assertIn("someNewFlag", " ".join(logs.output))

    def testImportingDoesNotDependOnLogLevelVariable(self):
        env = dict(os.environ, LOGLEVEL = "debug")
        res = subprocess.run([sys.executable, "-c", "import eventregistry, logging; print(len(logging.getLogger('eventregistry').handlers))"],
                             capture_output = True, text = True, env = env)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(res.stdout.strip(), "0", "the package should not add its own log handlers")

    def testStarImportExportsOnlyPublicNames(self):
        import eventregistry
        namespace = {}
        exec("from datetime import datetime; from eventregistry import *", namespace)
        self.assertIs(namespace["datetime"], datetime.datetime, "the star import must not overwrite the user's names")
        for name in ["os", "json", "re", "time", "requests", "threading", "logger", "urlencode", "copy", "inspect"]:
            self.assertNotIn(name, namespace, "'%s' should not be exported by the package" % name)
        for name in ["EventRegistry", "QueryArticles", "QueryArticlesIter", "QueryItems", "ReturnInfo", "ArticleInfoFlags", "RequestArticlesInfo",
                     "ComplexArticleQuery", "BaseQuery", "TopicPage", "Analytics", "GetTrendingConcepts", "EventRegistryError", "QueryError", "allLangs"]:
            self.assertIn(name, namespace, "'%s' should be exported by the package" % name)
        self.assertEqual(len(eventregistry.__all__), len(set(eventregistry.__all__)), "a name is exported by more than one module")


class TestNewFeatures(unittest.TestCase):

    def testApiKeyFromEnvironment(self):
        noSettings = os.path.join(tempfile.gettempdir(), "er-no-such-settings.json")
        with mock.patch.dict(os.environ, {"EVENTREGISTRY_API_KEY": "ENVKEY"}):
            self.assertEqual(EventRegistry(settingsFName = noSettings)._apiKey, "ENVKEY")
            # the key given as the argument wins
            self.assertEqual(EventRegistry(apiKey = "ARGKEY", settingsFName = noSettings)._apiKey, "ARGKEY")

    def testNewArticleAggregates(self):
        expected = {
            RequestArticlesLangAggr: {"resultType": "langAggr"},
            RequestArticlesSentimentAggr: {"resultType": "sentimentAggr"},
            RequestArticlesAuthorAggr: {"resultType": "authorAggr", "authorAggrAuthorCount": 50, "authorAggrIncludePeople": True, "authorAggrIncludeAgencies": True, "authorAggrSampleSize": 500000},
            RequestArticlesLocAggr: {"resultType": "locAggr", "locAggrSampleSize": 500000},
            RequestArticlesSourceExAggr: {"resultType": "sourceExAggr", "sourceExAggrSourceCount": 50, "sourceExAggrTimeWindow": "day", "sourceExAggrSampleSize": 20000},
        }
        for cls, params in expected.items():
            q = QueryArticles(keywords = "x", requestedResult = cls())
            sent = q._getQueryParams()
            self.assertEqual(sent["resultType"], [params["resultType"]])
            for name, val in params.items():
                if name != "resultType":
                    self.assertEqual(sent[name], val, "%s.%s" % (cls.__name__, name))
        self.assertRaises(ValueError, RequestArticlesAuthorAggr, articlesSampleSize = 2000000)
        self.assertRaises(ValueError, RequestArticlesSourceExAggr, articlesSampleSize = 60000)

    def testNewEventAggregates(self):
        sent = QueryEvents(keywords = "x", requestedResult = RequestEventsSentimentAggr())._getQueryParams()
        self.assertEqual(sent["resultType"], ["sentimentAggr"])
        sent = QueryEvents(keywords = "x", requestedResult = RequestEventsAuthorAggr(authorCount = 10, includeAgencies = False))._getQueryParams()
        self.assertEqual(sent["resultType"], ["authorAggr"])
        self.assertEqual((sent["authorAggrAuthorCount"], sent["authorAggrIncludeAgencies"], sent["authorAggrSampleSize"]), (10, False, 50000))
        self.assertRaises(ValueError, RequestEventsAuthorAggr, eventsSampleSize = 200000)

    def testEventsQueryUsesIgnoreKeyword(self):
        params = QueryEvents(keywords = "x", ignoreKeywords = "y").queryParams
        self.assertEqual(params["ignoreKeyword"], "y")
        self.assertNotIn("ignoreKeywords", params)

    def testBaseQueryKeywordSearchMode(self):
        self.assertEqual(BaseQuery(keyword = "x", keywordSearchMode = "exact").getQuery(), {"keyword": "x", "keywordSearchMode": "exact"})
        self.assertEqual(BaseQuery(keyword = "x").getQuery(), {"keyword": "x"})
        # the conditions can be a string or QueryItems, a plain list is not accepted
        self.assertEqual(BaseQuery(sourceLocationUri = QueryItems.OR(["a", "b"])).getQuery(), {"sourceLocationUri": {"$or": ["a", "b"]}})
        self.assertRaises(TypeError, BaseQuery, authorUri = ["a", "b"])

    def testTopicPageBySavedUri(self):
        er = makeER()
        er.jsonRequest = mock.Mock(return_value = {"articles": {"results": []}})
        topic = TopicPage(er)
        topic.getArticles(uri = "my-topic-uri", onlyAfterTm = datetime.datetime(2026, 10, 1, 12, 0, tzinfo = datetime.timezone.utc), maxDaysBack = 3)
        path, params = er.jsonRequest.call_args.args
        self.assertEqual(path, "/api/v1/article")
        self.assertEqual((params["action"], params["uri"], params["onlyAfterTm"], params["maxDaysBack"]), ("getArticlesForTopicPage", "my-topic-uri", "2026-10-01T12:00:00", 3))
        # the definition in the object is not sent when a saved topic page is used
        self.assertNotIn("topicPage", params)
        self.assertNotIn("dataType", params)
        topic.getEvents(uri = "my-topic-uri", onlyAfterTm = "2026-10-01T12:00:00")
        path, params = er.jsonRequest.call_args.args
        self.assertEqual((path, params["action"], params["uri"], params["onlyAfterTm"]), ("/api/v1/event", "getEventsForTopicPage", "my-topic-uri", "2026-10-01T12:00:00"))
        # without the uri the definition is sent, as before
        topic.getArticles()
        params = er.jsonRequest.call_args.args[1]
        self.assertIn("topicPage", params)
        self.assertNotIn("uri", params)
        self.assertNotIn("onlyAfterTm", params)

    def testRecentArticlesNamedFilters(self):
        er = makeER()
        recent = GetRecentArticles(er, keywords = QueryItems.OR(["a", "b"]), sourceUri = "bbc.com", lang = "eng", maxArticleCount = 50,
                                   updatesAfterMinsAgo = 10, isDuplicateFilter = "skipDuplicates", minSentiment = 0.2, dataType = ["news", "pr"])
        params = recent.queryParams
        self.assertEqual((params["keyword"], params["keywordOper"]), (["a", "b"], "or"))
        self.assertEqual((params["sourceUri"], params["lang"], params["isDuplicateFilter"], params["minSentiment"], params["dataType"]),
                         ("bbc.com", "eng", "skipDuplicates", 0.2, ["news", "pr"]))
        self.assertEqual((params["recentActivityArticlesMaxArticleCount"], params["recentActivityArticlesUpdatesAfterMinsAgo"]), (50, 10))
        self.assertNotIn("action", params)
        self.assertEqual(recent._getPath(), "/api/v1/minuteStreamArticles")
        # without filters only the parameters of the feed are sent
        plain = GetRecentArticles(er, returnInfo = ReturnInfo()).queryParams
        self.assertNotIn("keyword", plain)
        self.assertNotIn("recentActivityArticlesMaxArticleCount", plain)
        # other parameters can still be passed as they are
        self.assertEqual(GetRecentArticles(er, someNewParam = 1).queryParams["someNewParam"], 1)

    def testMentionsAcceptComplexMentionQuery(self):
        cq = ComplexMentionQuery(BaseQuery(keyword = "Tesla"))
        for cls in (QueryMentions, QueryMentionsIter):
            q = cls.initWithComplexQuery(cq)
            self.assertIsInstance(q, cls)
            self.assertEqual(json.loads(q.queryParams["query"]), {"$query": {"keyword": "Tesla"}})
            self.assertRaises(TypeError, cls.initWithComplexQuery, 123)
        # a single mention uri is accepted by the iterator as well
        self.assertEqual(QueryMentionsIter.initWithMentionUriList("m1").queryParams["mentionUri"], "m1")

    def testMentionAggregates(self):
        sent = QueryMentions(keywords = "x", requestedResult = RequestMentionsEventTypeAggr())._getQueryParams()
        self.assertEqual((sent["resultType"], sent["eventTypeAggrSampleSize"]), (["eventTypeAggr"], 100000))
        self.assertRaises(ValueError, RequestMentionsEventTypeAggr, mentionsSampleSize = 500000)
        sent = QueryMentions(keywords = "x", requestedResult = RequestMentionsCategoryAggr())._getQueryParams()
        self.assertEqual((sent["resultType"], sent["categoryAggrSampleSize"]), (["categoryAggr"], 20000))
        # the concept graph of mentions was never supported by the server and was removed
        import eventregistry
        self.assertFalse(hasattr(eventregistry, "RequestMentionsConceptGraph"))

    def testRecentEventsNamedFilters(self):
        er = makeER()
        recent = GetRecentEvents(er, conceptUri = "c1", maxEventCount = 20, updatesAfterTm = "2026-10-01T10:00:00+02:00", minArticlesInEvent = 5)
        params = recent.queryParams
        self.assertEqual((params["conceptUri"], params["recentActivityEventsMaxEventCount"], params["recentActivityEventsUpdatesAfterTm"], params["minArticlesInEvent"]),
                         ("c1", 20, "2026-10-01T08:00:00", 5))
        self.assertNotIn("action", params)


class TestQueryRepr(unittest.TestCase):

    def testQueryReprShowsParams(self):
        q = QueryArticles(keywords = QueryItems.OR(["Tesla", "SpaceX"]), lang = "eng", dateStart = datetime.date(2026, 9, 1))
        self.assertEqual(repr(q), "QueryArticles(action='getArticles', keyword=['Tesla', 'SpaceX'], keywordOper='or', lang='eng', "
                                  "dateStart='2026-09-01', resultType=['articles'])")

    def testReprWithoutResultType(self):
        q = QueryArticles(keywords = "Tesla")
        q.resultTypeList = []
        self.assertEqual(repr(q), "QueryArticles(action='getArticles', keyword='Tesla')")
        self.assertEqual(repr(GetSourceInfo("bbc.com")).split("(")[0], "GetSourceInfo")


if __name__ == "__main__":
    unittest.main(verbosity = 2)
