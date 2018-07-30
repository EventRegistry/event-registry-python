from __future__ import print_function
import unittest, math, random
from eventregistry import *
from DataValidator import DataValidator
from eventregistryadmin import EventRegistryAdmin


class TestQueryPaging(DataValidator):

    def testPagingUri1(self):
        """
        test pages 1 and 2, download uriwgtlist and then test in reverse
        """
        q = QueryArticles(sourceUri="bbc.co.uk", dateStart="2018-04-22", dateEnd="2018-04-25")
        q.setRequestedResult(RequestArticlesUriWgtList(page=1, count=1000))
        res = self.er.execQuery(q)
        arr = res.get("uriWgtList", {}).get("results", [])
        uriList = self.er.getUriFromUriWgt(arr)

        q.setRequestedResult(RequestArticlesUriWgtList(page=2, count=1000))
        res = self.er.execQuery(q)
        arr = res.get("uriWgtList", {}).get("results", [])
        uriList.extend(self.er.getUriFromUriWgt(arr))

        erAdmin = EventRegistryAdmin(self.er._host)
        erAdmin.clearCache()

        q = QueryArticles(sourceUri="bbc.co.uk", dateStart="2018-04-22", dateEnd="2018-04-25")
        q.setRequestedResult(RequestArticlesUriWgtList(page=2, count=1000))
        res = self.er.execQuery(q)
        arr = res.get("uriWgtList", {}).get("results", [])
        uriList2 = self.er.getUriFromUriWgt(arr)

        q.setRequestedResult(RequestArticlesUriWgtList(page=1, count=1000))
        res = self.er.execQuery(q)
        arr = res.get("uriWgtList", {}).get("results", [])
        uriList2.extend(self.er.getUriFromUriWgt(arr))

        uriList.sort()
        uriList2.sort()
        self.assertTrue(len(uriList) == len(uriList2))
        for i in range(len(uriList)):
            self.assertTrue(uriList[i] == uriList2[i])


    def testPagingArt1(self):
        """
        test pages 1 and 2, download items
        """
        q = QueryArticles(sourceUri="bbc.co.uk", dateStart="2018-04-22", dateEnd="2018-04-25")
        q.setRequestedResult(RequestArticlesInfo(page=1, count=100))
        res = self.er.execQuery(q)
        arr = res.get("articles", {}).get("results", [])
        uriList = [art["uri"] for art in arr]

        q.setRequestedResult(RequestArticlesInfo(page=2, count=100))
        res = self.er.execQuery(q)
        arr = res.get("articles", {}).get("results", [])
        uriList.extend([art["uri"] for art in arr])

        q = QueryArticles(sourceUri="bbc.co.uk", dateStart="2018-04-22", dateEnd="2018-04-25")
        q.setRequestedResult(RequestArticlesInfo(page=2, count=100))
        res = self.er.execQuery(q)
        arr = res.get("articles", {}).get("results", [])
        uriList2 = [art["uri"] for art in arr]

        q.setRequestedResult(RequestArticlesInfo(page=1, count=100))
        res = self.er.execQuery(q)
        arr = res.get("articles", {}).get("results", [])
        uriList2.extend([art["uri"] for art in arr])

        uriList.sort()
        uriList2.sort()
        self.assertTrue(len(uriList) == len(uriList2))
        for i in range(len(uriList)):
            self.assertTrue(uriList[i] == uriList2[i])


    def testAllPagesArt1(self):
        """
        download all pages of results through articles directly and using uriWgtList - in both cases should be the same
        """
        q = QueryArticles(sourceUri="bbc.co.uk", dateStart="2018-04-22", dateEnd="2018-04-25")
        page = 1
        uriList = []
        while True:
            q.setRequestedResult(RequestArticlesInfo(page=page, count=100))
            res = self.er.execQuery(q)
            arr = res.get("articles", {}).get("results", [])
            uriList.extend([art["uri"] for art in arr])
            page += 1
            if len(arr) == 0:
                break

        erAdmin = EventRegistryAdmin(self.er._host)
        erAdmin.clearCache()

        q = QueryArticles(sourceUri="bbc.co.uk", dateStart="2018-04-22", dateEnd="2018-04-25")
        page = 1
        uriList2 = []
        while True:
            q.setRequestedResult(RequestArticlesUriWgtList(page=page, count=100))
            res = self.er.execQuery(q)
            arr = res.get("uriWgtList", {}).get("results", [])
            uriList2.extend(self.er.getUriFromUriWgt(arr))
            page += 1
            if len(arr) == 0:
                break

        uriList.sort()
        uriList2.sort()
        self.assertTrue(len(uriList) == len(uriList2))
        for i in range(len(uriList)):
            self.assertTrue(uriList[i] == uriList2[i])


    def testDownloadingOfArticlePages(self):
        """
        download article pages in random order of pages and in the normal order
        """
        iter = QueryArticlesIter(sourceUri="bbc.co.uk", dateStart="2018-04-10", dateEnd="2018-04-16")
        # number of matches
        count = iter.count(self.er)
        print("\nFound %d articles" % count)

        # try again with a randomized order of pages
        uriSet = set()
        totArts = 0
        pages = list(range(1, int(1 + math.ceil(count / 100))))
        random.shuffle(pages)
        for page in pages:
            q = QueryArticles(sourceUri="bbc.co.uk", dateStart="2018-04-10", dateEnd="2018-04-16")
            q.setRequestedResult(RequestArticlesInfo(page=page, count=100))
            res = self.er.execQuery(q)
            c = res.get("articles", {}).get("totalResults", -1)
            self.assertTrue(c == count)
            arts = res.get("articles", {}).get("results", [])
            for art in arts:
                uriSet.add(art["uri"])
            self.assertTrue(len(arts) <= 100)
            totArts += len(arts)
        self.assertTrue(len(uriSet) == count)
        self.assertTrue(totArts == count)

        erAdmin = EventRegistryAdmin(self.er._host)
        erAdmin.clearCache()

        uriSet = set()
        totArts = 0
        pages = list(range(1, int(1 + math.ceil(count / 100))))
        for page in pages:
            q = QueryArticles(sourceUri="bbc.co.uk", dateStart="2018-04-10", dateEnd="2018-04-16")
            q.setRequestedResult(RequestArticlesInfo(page=page, count=100))
            res = self.er.execQuery(q)
            c = res.get("articles", {}).get("totalResults", -1)
            self.assertTrue(c == count)
            arts = res.get("articles", {}).get("results", [])
            for art in arts:
                uriSet.add(art["uri"])
            self.assertTrue(len(arts) <= 100)
            totArts += len(arts)
        self.assertTrue(len(uriSet) == count)
        self.assertTrue(totArts == count)


    def testDownloadingOfArticleUris(self):
        iter = QueryArticlesIter(conceptUri= self.er.getConceptUri("Trump"), dateStart = "2016-12-01", dateEnd = "2017-01-01")
        # number of matches
        count = iter.count(self.er)
        print("\nFound %d articles by uris\nDownloading page:" % count, end="")

        # try again with a randomized order of pages
        print("\nFound %d articles by uris\nDownloading page:" % count, end="")
        uriSet = set()
        totArts = 0
        pages = list(range(1, int(1 + math.ceil(count / 10000))))
        random.shuffle(pages)
        for page in pages:
            print("%d" % page, end=", ")
            q = QueryArticles(conceptUri= self.er.getConceptUri("Trump"), dateStart = "2016-12-01", dateEnd = "2017-01-01")
            q.setRequestedResult(RequestArticlesUriWgtList(page=page, count=10000))
            res = self.er.execQuery(q)
            c = res.get("uriWgtList", {}).get("totalResults", -1)
            self.assertTrue(c == count)
            arts = res.get("uriWgtList", {}).get("results", [])
            for art in arts:
                uriSet.add(art.split(":")[0])
            self.assertTrue(len(arts) <= 10000)
            totArts += len(arts)
        self.assertTrue(len(uriSet) == count)
        self.assertTrue(totArts == count)

        erAdmin = EventRegistryAdmin(self.er._host)
        erAdmin.clearCache()

        uriSet = set()
        totArts = 0
        pages = list(range(1, int(1 + math.ceil(count / 10000))))
        for page in pages:
            print("%d" % page, end=", ")
            q = QueryArticles(conceptUri= self.er.getConceptUri("Trump"), dateStart = "2016-12-01", dateEnd = "2017-01-01")
            q.setRequestedResult(RequestArticlesUriWgtList(page=page, count=10000))
            res = self.er.execQuery(q)
            c = res.get("uriWgtList", {}).get("totalResults", -1)
            self.assertTrue(c == count)
            arts = res.get("uriWgtList", {}).get("results", [])
            for art in arts:
                uriSet.add(art.split(":")[0])
            self.assertTrue(len(arts) <= 10000)
            totArts += len(arts)
        self.assertTrue(len(uriSet) == count)
        self.assertTrue(totArts == count)


    def testDownloadingOfArticles(self):
        iter = QueryArticlesIter(conceptUri= self.er.getConceptUri("peace"), dateStart = "2018-04-18", dateEnd = "2018-04-22")
        # number of matches
        count = iter.count(self.er)
        print("\nFound %d articles\nDownloading page:" % count, end="")

        # try again with a randomized order of pages
        print("\nFound %d articles\nDownloading page:" % count, end="")
        uriSet = set()
        totArts = 0
        pages = list(range(1, int(1 + math.ceil(count / 100))))
        random.shuffle(pages)
        for page in pages:
            print("%d" % page, end=", ")
            q = QueryArticles(conceptUri= self.er.getConceptUri("peace"), dateStart = "2018-04-18", dateEnd = "2018-04-22")
            q.setRequestedResult(RequestArticlesInfo(page=page, count=100))
            res = self.er.execQuery(q)
            c = res.get("articles", {}).get("totalResults", -1)
            self.assertTrue(c == count)
            arts = res.get("articles", {}).get("results", [])
            for art in arts:
                uriSet.add(art["uri"])
            self.assertTrue(len(arts) <= 100)
            totArts += len(arts)
        self.assertTrue(len(uriSet) == count)
        self.assertTrue(totArts == count)

        erAdmin = EventRegistryAdmin(self.er._host)
        erAdmin.clearCache()

        uriSet = set()
        totArts = 0
        pages = list(range(1, int(1 + math.ceil(count / 100))))
        for page in pages:
            print("%d" % page, end=", ")
            q = QueryArticles(conceptUri= self.er.getConceptUri("peace"), dateStart = "2018-04-18", dateEnd = "2018-04-22")
            q.setRequestedResult(RequestArticlesInfo(page=page, count=100))
            res = self.er.execQuery(q)
            c = res.get("articles", {}).get("totalResults", -1)
            self.assertTrue(c == count)
            arts = res.get("articles", {}).get("results", [])
            for art in arts:
                uriSet.add(art["uri"])
            self.assertTrue(len(arts) <= 100)
            totArts += len(arts)
        self.assertTrue(len(uriSet) == count)
        self.assertTrue(totArts == count)



    def testDownloadingOfEventUris(self):
        iter = QueryEventsIter(conceptUri= self.er.getConceptUri("Trump"), dateStart = "2016-10-01", dateEnd = "2016-11-01")
        # number of matches
        count = iter.count(self.er)
        print("\nFound %d events by uris\nDownloading page:" % count, end="")

        # try again with a randomized order of pages
        print("\nFound %d events by uris\nDownloading page:" % count, end="")
        uriSet = set()
        pages = list(range(1, int(1 + math.ceil(count / 1000))))
        random.shuffle(pages)
        for page in pages:
            print("%d" % page, end=", ")
            q = QueryEvents(conceptUri= self.er.getConceptUri("Trump"), dateStart = "2016-10-01", dateEnd = "2016-11-01")
            q.setRequestedResult(RequestEventsUriWgtList(page=page, count=1000))
            res = self.er.execQuery(q)
            c = res.get("uriWgtList", {}).get("totalResults", -1)
            self.assertTrue(c == count)
            arts = res.get("uriWgtList", {}).get("results", [])
            self.assertTrue(len(arts) > 0)
            for art in arts:
                uriSet.add(art.split(":")[0])
            self.assertTrue(len(arts) <= 1000)
        # self.assertTrue(len(uriSet) == count)

        erAdmin = EventRegistryAdmin(self.er._host)
        erAdmin.clearCache()

        uriSet2 = set()
        pages = list(range(1, int(1 + math.ceil(count / 1000))))
        for page in pages:
            print("%d" % page, end=", ")
            q = QueryEvents(conceptUri= self.er.getConceptUri("Trump"), dateStart = "2016-10-01", dateEnd = "2016-11-01")
            q.setRequestedResult(RequestEventsUriWgtList(page=page, count=1000))
            res = self.er.execQuery(q)
            c = res.get("uriWgtList", {}).get("totalResults", -1)
            self.assertTrue(c == count)
            arts = res.get("uriWgtList", {}).get("results", [])
            self.assertTrue(len(arts) > 0)
            for art in arts:
                uriSet2.add(art.split(":")[0])
            self.assertTrue(len(arts) <= 1000)
        self.assertTrue(len(uriSet) == len(uriSet2))


    def testDownloadingOfEvents(self):
        iter = QueryEventsIter(conceptUri= self.er.getConceptUri("peace"), dateStart = "2018-03-25", dateEnd = "2018-04-05")
        # number of matches
        count = iter.count(self.er)
        print("\nFound %d events\nDownloading page:" % count, end="")

        # try again with a randomized order of pages
        print("\nFound %d events\nDownloading page:" % count, end="")
        uriSet = set()
        pages = list(range(1, int(1 + math.ceil(count / 50))))
        random.shuffle(pages)
        for page in pages:
            print("%d" % page, end=", ")
            q = QueryEvents(conceptUri= self.er.getConceptUri("peace"), dateStart = "2018-03-25", dateEnd = "2018-04-05")
            q.setRequestedResult(RequestEventsInfo(page=page, count=50))
            res = self.er.execQuery(q)
            c = res.get("events", {}).get("totalResults", -1)
            self.assertTrue(c == count)
            arts = res.get("events", {}).get("results", [])
            for art in arts:
                uriSet.add(art["uri"])
            self.assertTrue(len(arts) <= 50)
        self.assertTrue(len(uriSet) == count)

        uriSet = set()
        pages = list(range(1, int(1 + math.ceil(count / 50))))
        for page in pages:
            print("%d" % page, end=", ")
            q = QueryEvents(conceptUri= self.er.getConceptUri("peace"), dateStart = "2018-03-25", dateEnd = "2018-04-05")
            q.setRequestedResult(RequestEventsInfo(page=page, count=50))
            res = self.er.execQuery(q)
            c = res.get("events", {}).get("totalResults", -1)
            self.assertTrue(c == count)
            arts = res.get("events", {}).get("results", [])
            for art in arts:
                uriSet.add(art["uri"])
            self.assertTrue(len(arts) <= 100)
        self.assertTrue(len(uriSet) == count)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryPaging)
    unittest.TextTestRunner(verbosity=3).run(suite)
