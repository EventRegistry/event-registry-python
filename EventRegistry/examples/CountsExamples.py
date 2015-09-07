from eventregistry import *

er = EventRegistry()

obamaUri = er.getConceptUri("Obama")
ebolaUri = er.getConceptUri("ebola")

q = GetCounts([obamaUri, ebolaUri])
ret = er.execQuery(q)
print er.format(ret)

# return the same data but only for a small date range
q.setDateRange("2015-05-15", "2015-05-20")
ret = er.execQuery(q)
print er.format(ret)

q = GetCountsEx(type = "category")
q.queryById(range(10))  # return trends of first 10 categories
ret = er.execQuery(q)
print er.format(ret)