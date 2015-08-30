from eventregistry import *

er = EventRegistry()

# top 10 trending concepts in the news
q = GetTrendingConcepts(source = "news", count = 10,
    returnInfo = ReturnInfo(
        conceptInfo = ConceptInfoFlags(trendingHistory = True)))
res = er.execQuery(q)
print er.prettyFormatObj(ret)

# top 20 trending concepts in the social media
q = GetTrendingConcepts(source = "social", count = 20,
    returnInfo = ReturnInfo(
        conceptInfo = ConceptInfoFlags(trendingHistory = True)))
res = er.execQuery(q)
print er.prettyFormatObj(ret)

# top 10 trending categories in the news
q = GetTrendingCategories(source = "news", count = 10,
    returnInfo = ReturnInfo(
        categoryInfo = CategoryInfoFlags(parentUri = True, childrenUris = True, trendingHistory = True)))
res = er.execQuery(q)
print er.prettyFormatObj(ret)