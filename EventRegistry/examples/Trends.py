from EventRegistry import *

#er = EventRegistry(host = "http://eventregistry.org", logging = True)
er = EventRegistry(host = "http://localhost:8090", logging = True)

# top 10 trending concepts in the news
q = GetTrendingConcepts(source = "news", count = 10,
    returnInfo = ReturnInfo(
        conceptInfo = ConceptInfoFlags(conceptClassMembership = True, trendingScore = True, trendingHistory = True)))
res = er.execQuery(q)
print res

# top 20 trending concepts in the social media
q = GetTrendingConcepts(source = "social", count = 20,
    returnInfo = ReturnInfo(
        conceptInfo = ConceptInfoFlags(conceptClassMembership = True, trendingScore = True, trendingHistory = True)))
res = er.execQuery(q)
print res

# top 10 trending categories in the news
q = GetTrendingCategories(source = "news", count = 10,
    returnInfo = ReturnInfo(
        categoryInfo = CategoryInfoFlags(parent = True, children = True, trendingScore = True, trendingHistory = True)))
res = er.execQuery(q)
print res
