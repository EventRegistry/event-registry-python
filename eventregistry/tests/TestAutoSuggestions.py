import unittest
from eventregistry import *
from .DataValidator import DataValidator

class TestAutoSuggest(DataValidator):

    def testConcepts(self):
        self.assertTrue(self.er.getConceptUri("Obama") == "http://en.wikipedia.org/wiki/Barack_Obama", "No suggestions are provided for name Obama")


    def testCategories(self):
        self.assertTrue(self.er.getCategoryUri("business") == "dmoz/Business")
        self.assertTrue(self.er.getCategoryUri("birding") == "dmoz/Recreation/Birding")


    def testSource(self):
        self.assertTrue(self.er.getNewsSourceUri("nytimes") == "nytimes.com")
        self.assertTrue(self.er.getNewsSourceUri("bbc") == "bbc.co.uk")

        # test PR sources
        self.assertTrue(self.er.getNewsSourceUri("Business Wire") == "businesswire.com")
        self.assertTrue(self.er.getNewsSourceUri("dailypolitical.com") == "dailypolitical.com")

        # test blogs
        self.assertTrue(self.er.getNewsSourceUri("slideshare.net") == "slideshare.net")
        self.assertTrue(self.er.getNewsSourceUri("topix.com") == "topix.com")

        self.assertTrue(self.er.suggestLocations("Washington")[0].get("wikiUri") == "http://en.wikipedia.org/wiki/Washington_(state)")
        self.assertTrue(self.er.suggestLocations("London")[0].get("wikiUri") == "http://en.wikipedia.org/wiki/City_of_London")

        srcList = self.er.suggestSourcesAtPlace(self.er.getConceptUri("New York City"))
        self.assertTrue(len(srcList) > 0)


    def testLocations(self):
        self.assertTrue(len(self.er.suggestLocationsAtCoordinate(38.893352, -77.093779, 300, limitToCities=True)) > 0)






if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAutoSuggest)
    unittest.TextTestRunner(verbosity=2).run(suite)
