import unittest
from eventregistry import *
from DataValidator import DataValidator

class TestAutoSuggest(DataValidator):

    def testConcepts(self):
        q = QueryEvents()
        self.assertIsNotNone(self.er.getConceptUri("Obama"), "No suggestions are provided for name Obama")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAutoSuggest)
    unittest.TextTestRunner(verbosity=2).run(suite)
