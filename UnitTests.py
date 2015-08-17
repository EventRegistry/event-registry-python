from EventRegistry import *

def Assert(condition, msg):
    if not condition:
        print msg

#er = EventRegistry(host = "http://eventregistry.org", logging = True)
#er = EventRegistry(host = "http://beta.eventregistry.org", logging = True)
er = EventRegistry(host = "http://localhost:8090", logging = True)

q = QueryEvents()
Assert(er.getConceptUri("Obama") != None, "No suggestions are provided for name Obama")

q.addConcept(er.getConceptUri("Obama"))                 # get events related to obama
#q.addCategory(er.getCategoryUri("society issues"))      # and are related to issues in society
#q.addNewsSource(er.getNewsSourceUri("bbc"))             # and have been reported by BBC
q.addRequestedResult(RequestEventsUriList())            # return uris of all events
q.addRequestedResult(RequestEventsInfo(page = 0, count = 100, sortBy = "size", sortByAsc = True, 
                returnInfo = ReturnInfo(
                   conceptLang = "deu", conceptType = "person",
                   eventInfo = EventInfoFlags(concepts = True, articleCounts = True, title = True, summary = True, categories = True, location = True, stories = True, images = True)
                   )))   # return event details for first 100 events
q.addRequestedResult(RequestEventsConceptAggr(conceptCount = 5,
                returnInfo = ReturnInfo(conceptType = ["org", "loc"])))        # compute concept aggregate on the events
res = er.execQuery(q)
obj = createStructFromDict(res)

Assert(hasattr(obj, "conceptAggr"), "Results should contain conceptAggr")
Assert(hasattr(obj, "events"), "Results should contain events")
Assert(hasattr(obj, "uriList"), "Results should contain uriList")

Assert(len(obj.conceptAggr) <= 10, "Received a list of concepts that is too long")
for concept in obj.conceptAggr:
    Assert(concept.type == "loc" or concept.type == "org", "Got concept of invalid type")

lastArtCount = 0
Assert(len(obj.events.results) <= 100, "Returned list of events was too long")

foundImages = False
foundLocation = False
for event in obj.events.results:
    Assert(hasattr(event, "articleCounts"), "Event should contain articleCounts")
    Assert(hasattr(event, "categories"), "Event should contain categories")
    Assert(hasattr(event, "concepts"), "Event should contain concepts")
    Assert(hasattr(event, "stories"), "Event should contain stories")
    Assert(hasattr(event, "title"), "Event should contain title")
    Assert(hasattr(event, "summary"), "Event should contain summary")
    foundImages = foundImages or hasattr(event, "images")
    foundLocation = foundLocation or hasattr(event, "location")

    Assert(event.articleCounts.total >= lastArtCount, "Events were not sorted by increasing size")
    lastArtCount = event.articleCounts.total
    for concept in event.concepts:
        Assert(hasattr(concept.label, "deu"), "Concept should contain label in german language")
        Assert(concept.type == "person", "Got concept of invalid type")

Assert(foundImages, "None of the results contained any images. Might be a bug")
Assert(foundLocation, "None of the results contained a location. Might be a bug")

q = QueryEvents()
q.addKeyword("car")  # get events containing word car
q.addRequestedResult(RequestEventsInfo(page = 1, count = 10, sortBy = "date", sortByAsc = False, 
                        returnInfo = ReturnInfo(conceptType = "org", 
                                                eventInfo = EventInfoFlags(concepts = False, articleCounts = False, title = False, summary = False, categories = False, location = False, stories = False, images = False)
                                                )))
q.addRequestedResult(RequestEventsConceptTrends(conceptCount = 5, 
                        returnInfo = ReturnInfo(conceptType = ["org", "loc"], conceptLang = "spa")))
res = er.execQuery(q)
obj = createStructFromDict(res)

Assert(hasattr(obj, "events"), "Results should contain events")
Assert(hasattr(obj, "conceptTrends"), "Results should contain conceptAggr")

for concept in obj.conceptTrends.conceptInfo:
    Assert(concept.type == "loc" or concept.type == "org", "Got concept of invalid type")
    Assert(hasattr(concept.label, "spa"), "Concept did not contain label in expected langage")

lastEventDate = obj.events.results[0].eventDate if len(obj.events.results) > 0 else ""
for event in obj.events.results:
    Assert(event.eventDate <= lastEventDate, "Events are not sorted by date")
    lastEventDate = event.eventDate
    Assert(not hasattr(event, "articleCounts"), "Event should not contain articleCounts")
    Assert(not hasattr(event, "categories"), "Event should not contain categories")
    Assert(not hasattr(event, "concepts"), "Event should not contain concepts")
    Assert(not hasattr(event, "location"), "Event should not contain location")
    Assert(not hasattr(event, "stories"), "Event should not contain stories")
    Assert(not hasattr(event, "images"), "Event should not contain images")
    Assert(not hasattr(event, "title"), "Event should not contain title")
    Assert(not hasattr(event, "summary"), "Event should not contain summary")

    
q = QueryEvents()
q.addLocation(er.getLocationUri("Washington"))
q.addRequestedResult(RequestEventsConceptTrends(40, 
            returnInfo = ReturnInfo(conceptType= "person")))
q.addRequestedResult(RequestEventsCategoryAggr())
q.addRequestedResult(RequestEventsInfo())
res = er.execQuery(q)

# get info about event with uri "123"
eventUri = "131"
q = QueryEvent(eventUri)
q.addRequestedResult(RequestEventInfo(
    returnInfo = ReturnInfo(conceptLang = ["eng", "spa", "slv"], conceptType = "wiki", 
        eventInfo = EventInfoFlags(concepts = True, articleCounts = True, title = True, summary = True, categories = True, location = True, stories = True, images = True)
    )))
q.addRequestedResult(RequestEventArticles(page = 0, count = 50, sortBy = "cosSim", sortByAsc = True, 
    returnInfo = ReturnInfo(conceptLang = "spa", conceptType = "wiki", 
        articleInfo = ArticleInfoFlags(concepts = True, storyUri = True, duplicateList = True, originalArticle = True, categories = True, location = True, extractedDates = True)
    ))) # get 10 articles about the event (any language is ok) that are closest to the center of the event
q.addRequestedResult(RequestEventArticleTrend())
q.addRequestedResult(RequestEventKeywordAggr())
eventRes = er.execQuery(q)

Assert(eventRes.has_key(eventUri), "Returned information did not contain information about the event")
Assert(eventRes[eventUri].has_key("info"), "Event did not contain 'info' result")
Assert(eventRes[eventUri].has_key("articleTrend"), "Event did not contain 'articleTrend' result")
Assert(eventRes[eventUri].has_key("keywordAggr"), "Event did not contain 'keywordAggr' result")

eventInfo = createStructFromDict(eventRes[eventUri]["info"])
Assert(hasattr(eventInfo, "articleCounts"), "Event did not contain articleCounts")
Assert(hasattr(eventInfo, "categories"), "Event did not contain categories")
Assert(hasattr(eventInfo, "concepts"), "Event did not contain concepts")
Assert(hasattr(eventInfo, "stories"), "Event did not contain stories")
Assert(hasattr(eventInfo, "title"), "Event did not contain title")
Assert(hasattr(eventInfo, "summary"), "Event did not contain summary")
for concept in eventInfo.concepts:
    Assert(hasattr(concept.label, "eng"), "Concept did not contain label in English langage")
    Assert(hasattr(concept.label, "slv"), "Concept did not contain label in Slovene langage")
    Assert(hasattr(concept.label, "spa"), "Concept did not contain label in Spanish langage")
    Assert(concept.type == "wiki", "Got concept of invalid type")

# check if we got expected content in the articles
articles = createStructFromDict(eventRes[eventUri]["articles"])
lastSim = -1
for article in articles.results:
    Assert(article.sim >= lastSim, "Articles are not sorted by cos sim")
    lastSim = article.sim
    Assert(hasattr(article, "concepts"), "Article did not contain concepts")
    Assert(hasattr(article, "categories"), "Article did not contain categories")
    Assert(hasattr(article, "eventUri"), "Article did not contain eventUri")
    Assert(hasattr(article, "storyUri"), "Article did not contain storyUri")
    if (article.isDuplicate):
        Assert(hasattr(article, "originalArticle"), "Article is a duplicate but did not contain original article")
    else:
        Assert(hasattr(article, "duplicates"), "Article did not contain duplicates list")
    for concept in article.concepts:
        Assert(hasattr(concept.label, "spa"), "Concept did not contain label in Spanish langage")
        Assert(concept.type == "wiki", "Concept of wrong type")

if (len(articles.results) > 0):
    articleUris = [art.uri for art in articles.results[:5]]  # take only first X articles
    # query info about specific articles
    qa = QueryArticle(articleUris)
    qa.addRequestedResult(RequestArticleInfo())                 # get all info about the specified article
    qa.addRequestedResult(RequestArticleSimilarArticles())      # get info about similar articles
    qa.addRequestedResult(RequestArticleDuplicatedArticles())   # if an article has duplicates then return list of duplicated articles
    qa.addRequestedResult(RequestArticleOriginalArticle())      # if an article is a duplicate then return the information about original article
    articleRes = er.execQuery(qa)
    
    Assert(len(articleRes.keys()) == len(articleUris), "Did not receive expected set of articles")

    for artKey in articleRes.keys():
        artDict = articleRes[artKey]
        article = createStructFromDict(artDict)
        Assert(hasattr(article, "info"), "Article did not contain 'info' result")
        Assert(hasattr(article, "similarArticles"), "Article did not contain 'similarArticles' result")
        Assert(hasattr(article, "duplicatedArticles"), "Article did not contain 'duplicatedArticles' result")
        


      