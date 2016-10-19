from eventregistry import *

er = EventRegistry()

obamaUri = er.getConceptUri("Obama")
ebolaUri = er.getConceptUri("ebola")

q = GetCounts([obamaUri, ebolaUri])
ret = er.execQuery(q)
print(er.format(ret))

# return the same data but only for a small date range
q.setDateRange("2015-05-15", "2015-05-20")
ret = er.execQuery(q)
print(er.format(ret))

q = GetCountsEx(type = "category")
q.queryById(list(range(10)))  # return trends of first 10 categories
ret = er.execQuery(q)
print(er.format(ret))

# get geographic spreadness of the concept Obama
obamaUri = er.getConceptUri("Obama")
q = GetCounts(obamaUri, source="geo")
ret = er.execQuery(q)

# get the sentiment expressed about Obama
q = GetCounts(obamaUri, source="sentiment")
ret = er.execQuery(q)

# get the stock prices for Apple
apple = er.getCustomConceptUri("apple")
q = GetCounts(apple, source="custom")
ret = er.execQuery(q)