from eventregistry import *

er = EventRegistry()

#
# top 10 top trending concepts in the news
#
q = GetTrendingConcepts(source = "news", count = 10,
    returnInfo = ReturnInfo(
        conceptInfo = ConceptInfoFlags(trendingHistory = True)))
ret = er.execQuery(q)
print(er.format(ret))

#
# get 20 most trending concept for each entity type
#
q = GetTrendingConceptGroups(source = "news")
# get top trends for individual concept groups - people, locations and organizations
q.getConceptTypeGroups()
ret = er.execQuery(q)
print(er.format(ret))

#
# top 20 trending concepts in the social media
#
q = GetTrendingConcepts(source = "social", count = 20,
    returnInfo = ReturnInfo(
        conceptInfo = ConceptInfoFlags(trendingHistory = True)))
ret = er.execQuery(q)
print(er.format(ret))


#
# top 10 trending categories in the news
#
q = GetTrendingCategories(source = "news", count = 10,
    returnInfo = ReturnInfo(
        categoryInfo = CategoryInfoFlags(parentUri = True, childrenUris = True, trendingHistory = True)))
ret = er.execQuery(q)
print(er.format(ret))