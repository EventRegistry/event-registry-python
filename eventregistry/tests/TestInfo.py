import unittest
from eventregistry import *
from DataValidator import DataValidator

class TestInfo(DataValidator):
    def test_sourcesByUri(self):
        sources = self.er.suggestNewsSources("a", count = 10)
        sourceUriList = [source.get("uri") for source in sources]
        q = GetSourceInfo(sourceUriList, returnInfo = ReturnInfo(
            sourceInfo = SourceInfoFlags(title = True,
                                         description = True,
                                         location = True,
                                         ranking = True,
                                         articleCount = True,
                                         sourceGroups = True,
                                         details = True)))
        res = self.er.execQuery(q)
        self.assertEqual(len(res), len(sourceUriList), "Expected different number of sources")
        for item in list(res.values()):
            self.assertIsNotNone(item.get("id"), "Source id is missing")
            self.assertIsNotNone(item.get("uri"), "Source uri is missing")
            self.assertIsNotNone(item.get("title"), "Source title is missing")
            self.assertIsNotNone(item.get("description"), "Source description is missing")
            self.assertIsNotNone(item.get("ranking"), "Source ranking is missing")
            self.assertIsNotNone(item.get("articleCount"), "Source articleCount is missing")
            self.assertIsNotNone(item.get("sourceGroups"), "Source sourceGroups is missing")
            self.assertIsNotNone(item.get("details"), "Source details is missing")


    def test_conceptsByUri(self):
        concepts = self.er.suggestConcepts("a", count = 10)
        uriList = [concept.get("uri") for concept in concepts]
        q = GetConceptInfo(uriList, returnInfo = ReturnInfo(
            conceptInfo = ConceptInfoFlags(type = "wiki",
                                           lang = ["deu", "slv"],
                                           label = True,
                                           synonyms = True,
                                           image = True,
                                           description = True,
                                           details = True,
                                           conceptClassMembership = True,
                                           conceptClassMembershipFull = True,
                                           trendingScore = True,
                                           trendingHistory = True,
                                           trendingSource = ["news", "social"])))

        res = self.er.execQuery(q)
        self.assertEqual(len(res), len(uriList), "Expected 10 concepts")
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
            self.assertIsNotNone(item.get("trendingScore"), "Concept should have trendingScore")
            self.assertIsNotNone(item.get("trendingScore").get("news"), "Concept should have trendingScore for news")
            self.assertIsNotNone(item.get("trendingScore").get("social"), "Concept should have trendingScore for social")
            self.assertIsNotNone(item.get("trendingHistory"), "Concept should have trendingHistory")
            self.assertIsNotNone(item.get("trendingHistory").get("news"), "Concept should have trendingHistory for news")
            self.assertIsNotNone(item.get("trendingHistory").get("social"), "Concept should have trendingHistory for social")


    def test_categories(self):
        categories = self.er.suggestCategories("a", count = 10)
        catUriList = [category.get("uri") for category in categories]
        q = GetCategoryInfo(catUriList, returnInfo = ReturnInfo(
            categoryInfo = CategoryInfoFlags(
                parentUri = True,
                childrenUris = True,
                trendingScore = True,
                trendingHistory = True,
                trendingSource = ["news", "social"])))
        res = self.er.execQuery(q)
        self.assertEqual(len(res), len(catUriList), "Expected 10 categories")
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
