Accessing Event Registry through Python
=====================

This library contains classes that allow one to easily access the event and article information from Event Registry ([http://eventregistry.org](http://eventregistry.org "http://eventregistry.org")).

To use the library one needs to import it:

```python
from EventRegistry import *
```

The main class that one needs to use is `EventRegistry`. It stores the location of the service and is able to make the necessary web requests. An instance can be created by calling:

```python
er = EventRegistry()
```

To obtain a list of URI suggestions for a label, the class provides methods such as `suggestConcepts`, `suggestNewsSources`, `suggestLocations` and `suggestCategories`. Each of the calls returns a list of python dictionaries where the “uri” key contains the URI value to use in the requests. If one is sure that the desired item will be first in the list, they can use an easier approach by calling methods `getConceptUri`, `getLocationUri`, `getCategoryUri` and `getNewsSourceUri` that all accept label as an argument and directly return the URI of the first item in the list.

There are four main class that are used for querying data – `QueryEvents`, `QueryEvent`, `QueryArticles` and `QueryArticle`.

##QueryEvents example

An example of a query for events could look something like this:

<pre><code>q = QueryEvents()
q.addConcept(er.getConceptUri("Obama"))                     # get events related to Barack Obama
q.addCategory(er.getCategoryUri("society issues"))       # and are related to issues in society
q.addNewsSource(er.getNewsSourceUri("bbc"))             # and have been reported by the BBC
q.addRequestedResult(RequestEventsUriList())               # return uris of all events
q.addRequestedResult(RequestEventsInfo(page = 0, count = 30))   # return event details for first 30 events
q.addRequestedResult(RequestEventsConceptAggr())        # compute concept aggregate on the events
res = er.execQuery(q)
</code></pre>

We start by adding a concept, category and news source condition. By calling the addRequestedResult method we specify what the desired results that we wish to obtain from the query are. By calling the execQuery method we execute the query and return the results. The res object in our example would be a python dictionary with the following structure:
{ 
‘conceptAggr’: [ 
{'labelEng': 'United States', 'score': 42.0, 'type': u'loc', 'uri': u'http://en.wikipedi...ed_States'}, 
{ 'labelEng': 'Barack Obama', 'score': 29.0, 'type': 'person', 'uri': u'http://en.wikipedi...ack_Obama'}, …],
‘events’: { ‘resultCount’: 122,
	‘results’: [
{'articleCounts': {'eng': 54.0, 'total': 54.0}, 'categories': [{...}], 'concepts': [{...}, ...], 'eventDate': '2014-08-29', 'eventDateEnd': '', 'multiLingInfo': {u'eng': {...}}, 'uri': '1211229', 'wgt': 9.0}, …
]}
‘uriList’: ['1211229', '1204045', '1195905', '1175569', …]
}
As it can be seen from the result, each requested information has a corresponding property in the returned object and its value holds the returned results.
QueryEvent example
When information about a particular event is required, one can use the QueryEvent class as in the following example:
>>> q = QueryEvent("123");
>>> q.addRequestedResult(RequestEventInfo(["eng", "spa", "slv"]))
>>> q.addRequestedResult(RequestEventArticles(0, 10))
>>> q.addRequestedResult(RequestEventArticleTrend())
>>> q.addRequestedResult(RequestEventKeywordAggr())
>>> eventRes = er.execQuery(q);
In this example we have requested for information about the event with URI “123”. We have asked for event details including the title and summary in English, Spanish and Slovene language. We have also asked for 10 articles about event. Since sorting is not specified, this will return 10 articles that are closest to the center of the clusters. The article trending request will return info about the intensity of new articles at different times, whereas the keyword request will return top keywords for the event.
QueryArticles example
An example of the QueryArticles class use when searching for articles is as follows:
>>> q = QueryArticles();
>>> q.setDateLimit(datetime.date(2014, 4, 16), datetime.date(2014, 4, 28))
>>> q.addKeyword("apple")
>>> q.addKeyword("iphone")
>>> q.addRequestedResult(RequestArticlesInfo(page=0, count = 30));
>>> res = er.execQuery(q)
In this case we specify the time limit to include only articles between 16th and 28th April, 2014. Additionally we specify two keywords to search for – apple and iphone. The resulting information will only contain 30 top articles.
QueryArticle example
The last example shows the use of the QueryArticle class. 
>>> uri = “http://www.bbc.com/news/technology-29139533”
>>> q = QueryArticle(uri);
>>> q.addRequestedResult(RequestArticleInfo())
>>> q.addRequestedResult(RequestArticleDuplicatedArticles())
>>> articleRes = er.execQuery(qa);
Assuming that uri is a valid URI of an article in the Event Registry, the example requests for article information as well as the list of articles that are duplicates of the article.
