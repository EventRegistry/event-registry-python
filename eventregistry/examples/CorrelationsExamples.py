from eventregistry import *

er = EventRegistry(logging = True)

#
# first example. Concepts and categories that correlate the most with Obama
corr = GetTopCorrelations(er)

counts = GetCounts(er.getConceptUri("Obama"))
corr.loadInputDataWithCounts(counts)

candidateConceptsQuery = QueryArticles(conceptUri = er.getConceptUri("Obama"))

conceptInfo = corr.getTopConceptCorrelations(
    candidateConceptsQuery = candidateConceptsQuery,
    conceptType = ["person", "org", "loc"],
    exactCount = 10,
    approxCount = 100)

categoryInfo = corr.getTopCategoryCorrelations(
    exactCount = 10,
    approxCount = 100)



#
# second example. Concepts and categories that correlate with keywords "iphone"
corr = GetTopCorrelations(er)

query = QueryArticles(keywords = "iphone")
corr.loadInputDataWithQuery(query)

conceptInfo = corr.getTopConceptCorrelations(
    exactCount = 10,
    approxCount = 100)

categoryInfo = corr.getTopCategoryCorrelations(
    exactCount = 10,
    approxCount = 100)

