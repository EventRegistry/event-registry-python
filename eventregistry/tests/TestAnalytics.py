import unittest
import eventregistry as ER
from .DataValidator import DataValidator

class TestAnalytics(DataValidator):

    def testConcepts(self):
        analytics = ER.Analytics(self.er)
        annInfo = analytics.annotate("Microsoft released a new version of Windows OS.")
        self.assertTrue("annotations" in annInfo, "Annotations were not provided for the given text")
        anns = annInfo["annotations"]
        self.assertTrue(len(anns) == 2)
        self.assertTrue("url" in anns[0])
        self.assertTrue("title" in anns[0])
        self.assertTrue("lang" in anns[0])
        self.assertTrue("secLang" in anns[0])
        self.assertTrue("secUrl" in anns[0])
        self.assertTrue("secTitle" in anns[0])
        self.assertTrue("wgt" in anns[0])
        self.assertTrue("wikiDataItemId" in anns[0])
        self.assertTrue("adverbs" in annInfo)
        self.assertTrue("adjectives" in annInfo)
        self.assertTrue("verbs" in annInfo)
        self.assertTrue("nouns" in annInfo)
        self.assertTrue("ranges" in annInfo)
        self.assertTrue("language" in annInfo)


    def testCategories(self):
        analytics = ER.Analytics(self.er)
        cats = analytics.categorize("Microsoft released a new version of Windows OS.")
        self.assertTrue("dmoz" in cats)
        self.assertTrue("categories" in cats.get("dmoz"))
        self.assertTrue("keywords" in cats.get("dmoz"))
        cat = cats.get("dmoz").get("categories")[0]
        self.assertTrue("label" in cat)
        self.assertTrue("score" in cat)
        kw = cats.get("dmoz").get("keywords")[0]
        self.assertTrue("keyword" in kw)
        self.assertTrue("wgt" in kw)


    def testLanguage(self):
        analytics = ER.Analytics(self.er)
        langInfo = analytics.detectLanguage("Microsoft released a new version of Windows OS.")
        print(langInfo)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAnalytics)
    unittest.TextTestRunner(verbosity=2).run(suite)
