from EventRegistry import *

er = EventRegistry(host = "http://eventregistry.org", logging = True)

q = QueryEvents()
q.addConcept(er.getConceptUri("Obama"))                 # get events related to obama
#q.addCategory(er.getCategoryUri("society issues"))      # and are related to issues in society
#q.addNewsSource(er.getNewsSourceUri("bbc"))             # and have been reported by BBC
q.addRequestedResult(RequestEventsUriList())            # return uris of all events
q.addRequestedResult(RequestEventsInfo(page = 0, count = 30, sortBy = "size", sortByAsc = True, conceptLang = "deu", conceptTypes = "person"))   # return event details for first 30 events
q.addRequestedResult(RequestEventsConceptAggr(conceptCount = 5, conceptTypes = ["org", "loc"]))        # compute concept aggregate on the events
res = er.execQuery(q)
obj = createStructFromDict(res)

q = QueryEvents();
q.addLocation(er.getLocationUri("Berlin"))
q.setDateLimit(datetime.date(2014, 4, 16), datetime.date(2014, 4, 28))
q.addRequestedResult(RequestEventsTrendingConcepts(40, conceptTypes=["person"]))
q.addRequestedResult(RequestEventsCategoryAggr())
q.addRequestedResult(RequestEventsInfo())
res = er.execQuery(q)

# get info about event with uri "123"
q = QueryEvent("997019");
q.addRequestedResult(RequestEventInfo(["eng", "spa", "slv"]))
q.addRequestedResult(RequestEventArticles(0, 10))        # get 10 articles about the event (any language is ok) that are closest to the center of the event
q.addRequestedResult(RequestEventArticleTrend())
q.addRequestedResult(RequestEventKeywordAggr())
eventRes = er.execQuery(q);

if (eventRes.has_key("articles") and len(eventRes["articles"]) > 0):
    articleUris = [art["uri"] for art in eventRes["articles"]["results"][:5]]  # take only first two articles
    # query info about specific articles
    qa = QueryArticle(articleUris);
    qa.addRequestedResult(RequestArticleInfo())                 # get all info about the specified article
    #qa.addRequestedResult(RequestArticleDuplicatedArticles())   # get info about duplicated articles for the specified two articles
    articleRes = er.execQuery(qa);
            
q = QueryArticle("http://www.kentucky.com/2014/07/17/3340248/official-malaysian-plane-shot.html");
q.addRequestedResult(RequestArticleInfo())                 # get all info about the specified article
res = er.execQuery(q);

q = QueryArticles();
q.setDateLimit(datetime.date(2014, 4, 16), datetime.date(2014, 4, 28))
#q.addKeyword("apple")
#q.addKeyword("iphone")
q.addConcept(er.getConceptUri("Apple"));
q.addRequestedResult(RequestArticlesInfo(page=0, count = 30, includeDuplicateList = True, includeConcepts = True, includeCategories = True, includeLocation = True, includeImage = True));
res = er.execQuery(q)

obj = createStructFromDict(res);
uris = [article.uri for article in obj.articles.results[:5]]
q = QueryArticle(uris, includeConcepts = True, includeCategories = True, includeLocation = True)
q.addRequestedResult(RequestArticleInfo())
q.addRequestedResult(RequestArticleOriginalArticle())
q.addRequestedResult(RequestArticleDuplicatedArticles())
res = er.execQuery(q);
obj = createStructFromDict(res)

# recent activity
q = QueryEvents()
q.addConcept(er.getConceptUri("Obama"))
q.addRequestedResult(RequestEventsRecentActivity())     # get most recently updated events related to obama
res = er.execQuery(q)
obj = createStructFromDict(res)

# let's say now that a minute has passed
q.clearRequestedResults()
q.addRequestedResult(RequestEventsRecentActivity(lastEventActivityId = obj.recentActivity.events.lastActivityId))
res = er.execQuery(q)
obj2 = createStructFromDict(res)

q = QueryArticles()
q.addConcept(er.getConceptUri("Obama"))
q.addRequestedResult(RequestArticlesRecentActivity())     # get most recently added articles related to obama
res = er.execQuery(q)

recentEvents = er.getRecentEvents()
recentArticles = er.getRecentArticles()

q = QueryArticles();
q.addConcept("topic-page-3")
q.setDateLimit("2014-09-20", "2014-09-29")
q.addRequestedResult(RequestArticlesInfo(page=0, count=10));
res = er.execQuery(q);

print er.getRecentStats()
