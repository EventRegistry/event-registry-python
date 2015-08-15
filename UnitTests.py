from EventRegistry import *

def Assert(condition, msg):
    if not condition:
        print msg

#er = EventRegistry(host = "http://eventregistry.org", logging = True)
#er = EventRegistry(host = "http://beta.eventregistry.org", logging = True)
er = EventRegistry(host = "http://localhost:8090", logging = True)

q = QueryEvents()
Assert(er.getConceptUri("Obama") != None, "No suggestions are provided for name Obama");

q.addConcept(er.getConceptUri("Obama"))                 # get events related to obama
#q.addCategory(er.getCategoryUri("society issues"))      # and are related to issues in society
#q.addNewsSource(er.getNewsSourceUri("bbc"))             # and have been reported by BBC
q.addRequestedResult(RequestEventsUriList())            # return uris of all events
q.addRequestedResult(RequestEventsInfo(page = 0, count = 100, sortBy = "size", sortByAsc = True, conceptLang = "deu", conceptTypes = "person", \
    includeEventConcepts = True, includeEventArticleCounts = True, includeEventTitle = True, includeEventSummary = True, includeEventCategories =  True, includeEventLocation = True, includeEventStories = True, includeEventImages = True))   # return event details for first 30 events
q.addRequestedResult(RequestEventsConceptAggr(conceptCount = 5, conceptTypes = ["org", "loc"]))        # compute concept aggregate on the events
res = er.execQuery(q)
obj = createStructFromDict(res)

Assert(hasattr(obj, "conceptAggr"), "Results should contain conceptAggr");
Assert(hasattr(obj, "events"), "Results should contain events");
Assert(hasattr(obj, "uriList"), "Results should contain uriList");

Assert(len(obj.conceptAggr) <= 10, "Received a list of concepts that is too long")
for concept in obj.conceptAggr:
    Assert(concept.type == "loc" or concept.type == "org", "Got concept of invalid type")

lastArtCount = 0;
Assert(len(obj.events.results) <= 100, "Returned list of events was too long")

foundImages = False; foundLocation = False;
for event in obj.events.results:
    Assert(hasattr(event, "articleCounts"), "Event did not contain wanted content");
    Assert(hasattr(event, "categories"), "Event did not contain wanted content");
    Assert(hasattr(event, "concepts"), "Event did not contain wanted content");
    Assert(hasattr(event, "stories"), "Event did not contain wanted content");
    Assert(hasattr(event, "title"), "Event did not contain wanted content");
    Assert(hasattr(event, "summary"), "Event did not contain wanted content");
    foundImages = foundImages or hasattr(event, "images");
    foundLocation = foundLocation or hasattr(event, "location");

    Assert(event.articleCounts.total >= lastArtCount, "Events were not sorted by increasing size")
    lastArtCount = event.articleCounts.total;
    for concept in event.concepts:
        Assert(hasattr(concept.label, "deu"), "Concept did not contain label in expected langage")
        Assert(concept.type == "person", "Got concept of invalid type")

Assert(foundImages, "None of the results contained any images. Might be a bug");
Assert(foundLocation, "None of the results contained a location. Might be a bug");

q = QueryEvents();
q.addKeyword("car")  # get events containing word car
q.addRequestedResult(RequestEventsInfo(page = 1, count = 10, sortBy = "date", sortByAsc = False, conceptTypes = "org", \
    includeEventConcepts = False, includeEventArticleCounts = False, includeEventTitle = False, includeEventSummary = False, includeEventCategories =  False, includeEventLocation = False, includeEventStories = False, includeEventImages = False))
q.addRequestedResult(RequestEventsConceptTrends(conceptCount = 5, conceptTypes = ["org", "loc"], conceptLangs = "spa"))
res = er.execQuery(q)
obj = createStructFromDict(res)

Assert(hasattr(obj, "events"), "Results should contain events");
Assert(hasattr(obj, "conceptTrends"), "Results should contain conceptAggr");

for concept in obj.conceptTrends.conceptInfo:
    Assert(concept.type == "loc" or concept.type == "org", "Got concept of invalid type")
    Assert(hasattr(concept.label, "spa"), "Concept did not contain label in expected langage")

lastEventDate = obj.events.results[0].eventDate if len(obj.events.results) > 0 else "";
for event in obj.events.results:
    Assert(event.eventDate <= lastEventDate, "Events are not sorted by date");
    lastEventDate = event.eventDate;
    Assert(not hasattr(event, "articleCounts"), "Event contained unwanted content");
    Assert(not hasattr(event, "categories"), "Event contained unwanted content");
    Assert(not hasattr(event, "concepts"), "Event contained unwanted content");
    Assert(not hasattr(event, "location"), "Event contained unwanted content");
    Assert(not hasattr(event, "stories"), "Event contained unwanted content");
    Assert(not hasattr(event, "images"), "Event contained unwanted content");
    Assert(not hasattr(event, "title"), "Event contained unwanted content");
    Assert(not hasattr(event, "summary"), "Event contained unwanted content");

    
q = QueryEvents();
q.addLocation(er.getLocationUri("Washington"))
q.addRequestedResult(RequestEventsConceptTrends(40, conceptTypes=["person"]))
q.addRequestedResult(RequestEventsCategoryAggr())
q.addRequestedResult(RequestEventsInfo())
res = er.execQuery(q)

# get info about event with uri "123"
eventUri = "131"
q = QueryEvent(eventUri);
q.addRequestedResult(RequestEventInfo(["eng", "spa", "slv"], conceptTypes = "wiki", includeEventConcepts = True, includeEventArticleCounts = True, includeEventTitle = True, includeEventSummary = True, includeEventCategories =  True, includeEventLocation = True, includeEventStories = True, includeEventImages = True))
q.addRequestedResult(RequestEventArticles(0, 50, sortyBy = "cosSim", sortByAsc = True, includeArticleConcepts = True, conceptLang = "spa", conceptTypes = "wiki", includeArticleStoryUri = True, includeArticleDuplicateList = True, includeArticleOriginalArticleInfo = True, includeArticleCategories = True, includeArticleLocation = True, includeArticleExtractedDates = True))        # get 10 articles about the event (any language is ok) that are closest to the center of the event
q.addRequestedResult(RequestEventArticleTrend())
q.addRequestedResult(RequestEventKeywordAggr())
eventRes = er.execQuery(q);

Assert(eventRes.has_key(eventUri), "Returned information did not contain information about the event");
Assert(eventRes[eventUri].has_key("info"), "Event did not contain expected information");
Assert(eventRes[eventUri].has_key("articleTrend"), "Event did not contain expected information");
Assert(eventRes[eventUri].has_key("keywordAggr"), "Event did not contain expected information");

eventInfo = createStructFromDict(eventRes[eventUri]["info"])
Assert(hasattr(eventInfo, "articleCounts"), "Event did not contain wanted content")
Assert(hasattr(eventInfo, "categories"), "Event did not contain wanted content")
Assert(hasattr(eventInfo, "concepts"), "Event did not contain wanted content")
Assert(hasattr(eventInfo, "stories"), "Event did not contain wanted content")
Assert(hasattr(eventInfo, "title"), "Event did not contain wanted content")
Assert(hasattr(eventInfo, "summary"), "Event did not contain wanted content")
for concept in eventInfo.concepts:
    Assert(hasattr(concept.label, "eng"), "Concept did not contain label in expected langage")
    Assert(hasattr(concept.label, "slv"), "Concept did not contain label in expected langage")
    Assert(hasattr(concept.label, "spa"), "Concept did not contain label in expected langage")
    Assert(concept.type == "wiki", "Got concept of invalid type")

articles = createStructFromDict(eventRes[eventUri]["articles"])
lastSim = -1
for article in articles.results:
    Assert(article.sim >= lastSim, "Articles are not sorted by cos sim")
    lastSim = article.sim
    Assert(hasattr(article, "concepts"), "Article did not contain expected information")
    Assert(hasattr(article, "categories"), "Article did not contain expected information")
    Assert(hasattr(article, "eventUri"), "Article did not contain expected information")
    Assert(hasattr(article, "storyUri"), "Article did not contain expected information")
    if (article.isDuplicate):
        Assert(hasattr(article, "originalArticle"), "Article did not contain expected information")
    else:
        Assert(hasattr(article, "duplicates"), "Article did not contain expected information")
    for concept in article.concepts:
        Assert(hasattr(concept.label, "spa"), "Concept did not contain label in expected langage")
        Assert(concept.type == "wiki", "Concept of wrong type")

if (len(articles.results) > 0):
    articleUris = [art.uri for art in articles.results[:5]]  # take only first X articles
    # query info about specific articles
    qa = QueryArticle(articleUris);
    qa.addRequestedResult(RequestArticleInfo())                 # get all info about the specified article
    qa.addRequestedResult(RequestArticleSimilarArticles())      # get info about similar articles
    qa.addRequestedResult(RequestArticleDuplicatedArticles())   # if an article has duplicates then return list of duplicated articles
    qa.addRequestedResult(RequestArticleOriginalArticle())      # if an article is a duplicate then return the information about original article
    articleRes = er.execQuery(qa);
    
    Assert(len(articleRes.keys()) == len(articleUris), "Did not receive expected set of articles")

    for artKey in articleRes.keys():
        artDict = articleRes[artKey]
        article = createStructFromDict(artDict)
        Assert(hasattr(article, "info"), "Article did not contain expected information")
        Assert(hasattr(article, "similarArticles"), "Article did not contain expected information")
        Assert(hasattr(article, "duplicatedArticles"), "Article did not contain expected information")
        


      