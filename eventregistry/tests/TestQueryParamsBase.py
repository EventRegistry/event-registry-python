import datetime, unittest, math
from eventregistry import *


class TestQueryParamsBase(unittest.TestCase):

    def testDateConversion(self):
        self.assertEqual("2015-01-01", QueryParamsBase.encodeDate(datetime.datetime(2015, 1, 1, 12, 0, 0)))
        self.assertEqual("2015-01-01", QueryParamsBase.encodeDate(datetime.date(2015, 1, 1)))
        self.assertEqual("2015-01-01", QueryParamsBase.encodeDate("2015-01-01"))

        self.assertEqual("2015-01-01T12:00:00", QueryParamsBase.encodeDateTime(datetime.datetime(2015, 1, 1, 12, 0, 0)))
        self.assertEqual("2015-01-01T12:00:00.123", QueryParamsBase.encodeDateTime("2015-01-01T12:00:00.123"))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryParamsBase)
    unittest.TextTestRunner(verbosity=3).run(suite)
