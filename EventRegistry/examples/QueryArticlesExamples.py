from eventregistry import *

#er = EventRegistry(host="http://eventregistry.ijs.si:8010")
er = EventRegistry()

#q = QueryArticles(keywords = u"الدوحة")
#q.setRequestedResult(RequestArticlesInfo(count = 30,
#    returnInfo = ReturnInfo(
#        articleInfo = ArticleInfoFlags(duplicateList = True, concepts = True, categories = True, location = True, image = True))))
## execute the query
#res = er.execQuery(q)

# query articles using the iterator class
q = QueryArticlesIter(conceptUri = er.getConceptUri("George Clooney"))
for art in q.execQuery(er, sortBy = "date"):
    print art


# query articles using the QueryArticles class
q = QueryArticles(conceptUri = er.getConceptUri("George Clooney"))
page = 1
while True:
    q.setRequestedResult(RequestArticlesInfo(page = page))
    res = er.execQuery(q)
    for article in res["articles"]["results"]:
        print article    # here use the info about the article
    if page >= res["articles"]["pages"]:
        break
    page += 1

q = QueryArticles()
# articles published on 2016-03-22 or 2016-03-23
q.setDateLimit(datetime.date(2016, 3, 22), datetime.date(2016, 3, 23))
# related to Brussels
#q.addConcept(er.getConceptUri("Brussels"))
# published by New York Times
q.addNewsSource(er.getNewsSourceUri("New York Times"))
# return details about the articles
q.setRequestedResult(RequestArticlesInfo(count = 30,
    returnInfo = ReturnInfo(
        articleInfo = ArticleInfoFlags(duplicateList = True, concepts = True, categories = True, location = True, image = True))))
# execute the query
res = er.execQuery(q)


# get recent articles about Obama
q = QueryArticles()
q.addConcept(er.getConceptUri("Obama"))
q.setRequestedResult(RequestArticlesRecentActivity())     # get most recently added articles related to obama
res = er.execQuery(q)
