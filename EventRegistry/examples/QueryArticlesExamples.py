from eventregistry import *

er = EventRegistry()


q = QueryArticles()
q.setDateLimit(datetime.date(2014, 4, 16), datetime.date(2014, 4, 28))
#q.addKeyword("apple")
#q.addKeyword("iphone")
q.addConcept(er.getConceptUri("Apple"))
q.addRequestedResult(RequestArticlesInfo(count = 30, 
    returnInfo = ReturnInfo(
        articleInfo = ArticleInfoFlags(duplicateList = True, concepts = True, categories = True, location = True, image = True))))
res = er.execQuery(q)

# get recent articles about Obama
q = QueryArticles()
q.addConcept(er.getConceptUri("Obama"))
q.addRequestedResult(RequestArticlesRecentActivity())     # get most recently added articles related to obama
res = er.execQuery(q)
