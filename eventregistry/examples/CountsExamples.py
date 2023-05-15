"""
examples showing how to obtain information how frequently a particular concept is mentioined in
the news articles, or an article is about a particular category
"""


from eventregistry import *

er = EventRegistry(host = "https://eventregistry.org")

obamaUri = er.getConceptUri("Trump")
ebolaUri = er.getConceptUri("ebola")

q = GetCounts([obamaUri, ebolaUri],
            dateStart = "2015-05-15",
            dateEnd = "2018-05-20")
ret = er.execQuery(q)
print(er.format(ret))

q = GetCountsEx([er.getCategoryUri("business")], type="category",
            dateStart = "2015-05-15",
            dateEnd = "2018-05-20")
ret = er.execQuery(q)
print(er.format(ret))

# get geographic spreadness of the concept Obama
obamaUri = er.getConceptUri("Obama")
q = GetCounts(obamaUri, source="geo")
ret = er.execQuery(q)

# get the sentiment expressed about Obama
q = GetCounts(obamaUri, source="sentiment")
ret = er.execQuery(q)
