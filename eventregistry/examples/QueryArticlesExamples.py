from eventregistry import *

er = EventRegistry()

# search for the phrase "Barack Obama" - both words have to appear together
q = QueryArticles(keywords = "Barack Obama")
res = er.execQuery(q)


# search for articles that mention the two words - maybe together, maybe apart
q = QueryArticles(keywords = ["Barack", "Obama"])
# set some custom information that should be returned as a result of the query
q.setRequestedResult(RequestArticlesInfo(count = 30,
    returnInfo = ReturnInfo(
        articleInfo = ArticleInfoFlags(duplicateList = True, concepts = True, categories = True, location = True, image = True))))
res = er.execQuery(q)


# search for articles that mention the phrase "Barack Obama" and Trump - the phrase and the word are not necessarily next to each other
q = QueryArticles(keywords = ["Barack Obama", "Trump"])
q.setRequestedResult(RequestArticlesInfo(count = 30,
    returnInfo = ReturnInfo(
        articleInfo = ArticleInfoFlags(duplicateList = True, concepts = True, categories = True, location = True, image = True))))
res = er.execQuery(q)


# query articles using the iterator class
# iterator class simplifies retrieving and listing the list of matching articles
q = QueryArticlesIter(conceptUri = er.getConceptUri("George Clooney"))
for art in q.execQuery(er, sortBy = "date"):
    print art


# query articles using the QueryArticles class
# old way of iterating through the pages of results - requesting results page by page
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
# articles published between 2016-03-22 and 2016-03-23
q.setDateLimit(datetime.date(2016, 3, 22), datetime.date(2016, 3, 23))
# related to Brussels
#q.addConcept(er.getConceptUri("Brussels"))
# published by New York Times
q.addNewsSource(er.getNewsSourceUri("New York Times"))
# return details about the articles, including the concepts, categories, location and image
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


#
# examples of complex queries that combine various OR and AND operators
#

# prepare some variables used in the queries
trumpUri = er.getConceptUri("Trump")
obamaUri = er.getConceptUri("Obama")
politicsUri = er.getCategoryUri("politics")
merkelUri = er.getConceptUri("merkel")
businessUri = er.getCategoryUri("business")


# find articles that (1) were published on 2017-04-22 and (2) are either about Obama or mention keyword Trump and (3) are related to business
cq1 = ComplexArticleQuery(
    includeQuery = CombinedQuery.AND([
        BaseQuery(dateStart = "2017-04-22", dateEnd = "2017-04-22"),
        CombinedQuery.OR([
            BaseQuery(conceptUri = QueryItems.OR([obamaUri])),
            BaseQuery(keyword = "Trump")
        ]),
        BaseQuery(categoryUri = businessUri)
    ])
)
q = QueryArticles.initWithComplexQuery(cq1)
res = er.execQuery(q)


# find articles that are both about Obama and Trump and are not in English or German language
cq2 = ComplexArticleQuery(
    includeQuery = BaseQuery(
        conceptUri = QueryItems.AND([obamaUri, trumpUri])),
    excludeQuery = BaseQuery(lang = QueryItems.OR(["eng", "deu"])))
listRes1 = getQueryUriListForComplexQuery(cq1)
q = QueryArticles.initWithComplexQuery(cq2)
res = er.execQuery(q)


# get articles that were published on 2017-02-05 or are about trump or are about politics or are about Merkel and business
# # and are not published on 2017-02-05 or are about Obama
qStr = """
{
    "include": {
        "$or": [
            { "dateStart": "2017-02-05", "dateEnd": "2017-02-05" },
            { "conceptUri": "%s" },
            { "categoryUri": "%s" },
            {
                "$and": [
                    { "conceptUri": "%s" },
                    { "categoryUri": "%s" }
                ]
            }
        ]
    },
    "exclude": {
        "$or": [
            { "dateStart": "2017-02-04", "dateEnd": "2017-02-04" },
            { "conceptUri": "%s" }
        ]
    }
}
    """ % (trumpUri, politicsUri, merkelUri, businessUri, obamaUri)
q1 = QueryArticles.initWithComplexQuery(qStr)
res = er.execQuery(q1)
