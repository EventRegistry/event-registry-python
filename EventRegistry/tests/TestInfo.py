import unittest
from eventregistry import *

class TestInfo(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.er = EventRegistry(host = "http://eventregistry.org")

    def test_sourcesById(self):
        q = GetSourceInfo(returnInfo = ReturnInfo(
            sourceInfo = SourceInfoFlags(title = True,
                                         description = True,
                                         location = True,
                                         importance = True,
                                         articleCount = True,
                                         tags = True,
                                         details = True)))
        q.queryById(list(range(10)))
        res = self.er.execQuery(q)
        self.assertEqual(len(res), 10, "Expected 10 sources")
        for item in list(res.values()):
            self.assertIsNotNone(item.get("id"), "Source id is missing")
            self.assertIsNotNone(item.get("uri"), "Source uri is missing")
            self.assertIsNotNone(item.get("title"), "Source title is missing")
            self.assertIsNotNone(item.get("description"), "Source description is missing")
            self.assertIsNotNone(item.get("importance"), "Source importance is missing")
            self.assertIsNotNone(item.get("articleCount"), "Source articleCount is missing")
            self.assertIsNotNone(item.get("tags"), "Source tags is missing")
            self.assertIsNotNone(item.get("details"), "Source tags is missing")
        if True not in ["location" in source for source in list(res.values())]:
            print("Warning: none of the sources has a location set")

        q = GetSourceInfo(returnInfo = ReturnInfo(
            sourceInfo = SourceInfoFlags(title = False,
                                         description = False,
                                         location = False,
                                         importance = False,
                                         articleCount = False,
                                         tags = False,
                                         details = False)))
        q.queryById(list(range(10)))
        res = self.er.execQuery(q)
        self.assertEqual(len(res), 10, "Expected 10 sources")
        for item in list(res.values()):
            self.assertIsNotNone(item.get("id"), "Source id is missing")
            self.assertIsNotNone(item.get("uri"), "Source uri is missing")
            self.assertIsNone(item.get("title"), "Source title should be missing")
            self.assertIsNone(item.get("description"), "Source description should be missing")
            self.assertIsNone(item.get("importance"), "Source importance should be missing")
            self.assertIsNone(item.get("articleCount"), "Source articleCount should be missing")
            self.assertIsNone(item.get("tags "), "Source tags should be missing")
            self.assertIsNone(item.get("details"), "Source tags should be missing")
            self.assertIsNone(item.get("location"), "Source location should be missing")


    def test_sourcesByUri(self):
        q = GetSourceInfo(returnInfo = ReturnInfo(
            sourceInfo = SourceInfoFlags(title = True,
                                         description = True,
                                         location = True,
                                         importance = True,
                                         articleCount = True,
                                         tags = True,
                                         details = True)))
        sources = self.er.suggestNewsSources("a")
        uris = [source.get("uri") for source in sources]
        q.queryByUri(uris)
        res = self.er.execQuery(q)
        self.assertEqual(len(res), len(uris), "Expected different number of sources")
        for item in list(res.values()):
            self.assertIsNotNone(item.get("id"), "Source id is missing")
            self.assertIsNotNone(item.get("uri"), "Source uri is missing")
            self.assertIsNotNone(item.get("title"), "Source title is missing")
            self.assertIsNotNone(item.get("description"), "Source description is missing")
            self.assertIsNotNone(item.get("importance"), "Source importance is missing")
            self.assertIsNotNone(item.get("articleCount"), "Source articleCount is missing")
            self.assertIsNotNone(item.get("tags"), "Source tags is missing")
            self.assertIsNotNone(item.get("details"), "Source tags is missing")


    def test_conceptsById(self):
        q = GetConceptInfo(returnInfo = ReturnInfo(
            conceptInfo = ConceptInfoFlags(type = "wiki",
                                           lang = ["deu", "slv"],
                                           label = True,
                                           synonyms = True,
                                           image = True,
                                           description = True,
                                           details = True,
                                           conceptClassMembership = True,
                                           conceptClassMembershipFull = True,
                                           conceptFolderMembership = True,
                                           trendingScore = True,
                                           trendingHistory = True,
                                           trendingSource = ["news", "social"])))
        q.queryById(list(range(10)))
        res = self.er.execQuery(q)
        self.assertEqual(len(res), 10, "Expected 10 concepts")
        for item in list(res.values()):
            self.assertIsNotNone(item.get("id"), "Concept id is missing")
            self.assertIsNotNone(item.get("uri"), "Concept uri is missing")
            self.assertIsNotNone(item.get("type"), "Concept type is missing")
            # since we've asked for specific concepts then types could be anything
            #self.assertEqual(item.get("type"), "wiki", "Concept type should be wiki")
            self.assertIsNotNone(item.get("label"), "Concept should have a label")
            self.assertIsNotNone(item.get("label").get("deu"), "Concept should have a label in german")
            self.assertIsNotNone(item.get("label").get("slv"), "Concept should have a label in slovene")
            self.assertIsNotNone(item.get("description"), "Concept should have a description")
            self.assertTrue("image" in item, "Concept should have an image")
            self.assertTrue("synonyms" in item, "Concept should have synonyms")
            self.assertTrue("details" in item, "Concept should have details")
            self.assertIsNotNone(item.get("conceptClassMembership"), "Concept should have conceptClassMembership")
            self.assertIsNotNone(item.get("conceptClassMembershipFull"), "Concept should have conceptClassMembershipFull")
            self.assertIsNotNone(item.get("conceptFolderMembership"), "Concept should have conceptFolderMembership")
            self.assertIsNotNone(item.get("trendingScore"), "Concept should have trendingScore")
            self.assertIsNotNone(item.get("trendingScore").get("news"), "Concept should have trendingScore for news")
            self.assertIsNotNone(item.get("trendingScore").get("social"), "Concept should have trendingScore for social")
            self.assertIsNotNone(item.get("trendingHistory"), "Concept should have trendingHistory")
            self.assertIsNotNone(item.get("trendingHistory").get("news"), "Concept should have trendingHistory for news")
            self.assertIsNotNone(item.get("trendingHistory").get("social"), "Concept should have trendingHistory for social")

        q = GetConceptInfo(returnInfo = ReturnInfo(
            conceptInfo = ConceptInfoFlags(type = "wiki",
                                           label = False,
                                           synonyms = False,
                                           image = False,
                                           description = False,
                                           details = False,
                                           conceptClassMembership = False,
                                           conceptClassMembershipFull = False,
                                           conceptFolderMembership = False,
                                           trendingScore = False,
                                           trendingHistory = False),
            locationInfo = LocationInfoFlags(label = False, placeCountry = False)))
        q.queryById(list(range(10)))
        res = self.er.execQuery(q)
        self.assertEqual(len(res), 10, "Expected 10 concepts")
        for item in list(res.values()):
            self.assertIsNotNone(item.get("id"), "Concept id is missing")
            self.assertIsNotNone(item.get("uri"), "Concept uri is missing")
            self.assertIsNotNone(item.get("type"), "Concept type is missing")
            # since we've asked for specific concepts then types could be anything
            #self.assertEqual(item.get("type"), "wiki", "Concept type should be wiki")
            self.assertIsNone(item.get("label"), "Concept should have not have a label")
            self.assertIsNone(item.get("synonyms"), "Concept should not have have synonyms")
            self.assertIsNone(item.get("image"), "Concept should not have have an image")
            self.assertIsNone(item.get("description"), "Concept should not have have a description")
            self.assertIsNone(item.get("details"), "Concept should not have have details")
            self.assertIsNone(item.get("conceptClassMembership"), "Concept should not have have conceptClassMembership")
            self.assertIsNone(item.get("conceptClassMembershipFull"), "Concept should not have have conceptClassMembershipFull")
            self.assertIsNone(item.get("conceptFolderMembership"), "Concept should not have have conceptFolderMembership")
            self.assertIsNone(item.get("trendingScore"), "Concept should not have have trendingScore")
            self.assertIsNone(item.get("trendingHistory"), "Concept should not have have trendingHistory")


    def test_categories(self):
        q = GetCategoryInfo(returnInfo = ReturnInfo(
            categoryInfo = CategoryInfoFlags(
                parentUri = True,
                childrenUris = True,
                trendingScore = True,
                trendingHistory = True,
                trendingSource = ["news", "social"])))
        q.queryById(list(range(10)))
        res = self.er.execQuery(q)
        self.assertEqual(len(res), 10, "Expected 10 categories")
        for item in list(res.values()):
            self.assertIsNotNone(item.get("id"), "Category id is missing")
            self.assertIsNotNone(item.get("uri"), "Category uri is missing")
            self.assertTrue("parentUri" in item, "Category parent uri is missing")
            self.assertIsNotNone(item.get("childrenUris"), "Category children uris are missing")
            self.assertIsNotNone(item.get("trendingScore"), "Category trending score is missing")
            self.assertIsNotNone(item.get("trendingHistory"), "Category trending history is missing")
            self.assertIsNotNone(item.get("trendingScore").get("news"), "Category trending score for news is missing")
            self.assertIsNotNone(item.get("trendingScore").get("social"), "Category trending score for social is missing")
            self.assertIsNotNone(item.get("trendingHistory").get("news"), "Category trending history for news is missing")
            self.assertIsNotNone(item.get("trendingHistory").get("social"), "Category trending history for social is missing")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInfo)
    unittest.TextTestRunner(verbosity=3).run(suite)