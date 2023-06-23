"""
examples showing how to obtain information how frequently a particular concept is mentioined in
the news articles, or an article is about a particular category
"""


from eventregistry import *

er = EventRegistry()

obamaUri = er.getConceptUri("Trump")
ebolaUri = er.getConceptUri("ebola")

q = GetCounts([obamaUri, ebolaUri])
ret = er.execQuery(q)
print(er.format(ret))

q = GetCountsEx([er.getCategoryUri("business")], type="category")
ret = er.execQuery(q)
print(er.format(ret))
