
#### NOTE: this is the latest version of python module for accessing the Event Registry data. It uses the latest ER API that is not yet supported on the current version of backend. You can use it in a few weeks when we make the upgrade. 
#### For now, still use [https://github.com/gregorleban/event-registry-python](https://github.com/gregorleban/event-registry-python)

----------


Accessing Event Registry data through Python
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

##Searching for events

An example of a query for events could look something like this:

```python
q = QueryEvents()
q.addConcept(er.getConceptUri("Obama"))                 # get events related to Barack Obama
q.addCategory(er.getCategoryUri("society issues"))      # and are related to issues in society
q.addNewsSource(er.getNewsSourceUri("bbc"))             # and have been reported by the BBC
q.addRequestedResult(RequestEventsUriList())            # return uris of all events
q.addRequestedResult(RequestEventsInfo(page = 0, count = 30))   # return event details for first 30 events
q.addRequestedResult(RequestEventsConceptAggr())        # compute concept aggregate on the events
res = er.execQuery(q)
```

We start by adding a concept, category and news source condition. By calling the `addRequestedResult` method we specify what the desired results that we wish to obtain from the query are. By calling the `execQuery` method we execute the query and return the results. The `res` object in our example would be a python dictionary with the following structure:

```
{ 
‘conceptAggr’: [ 
	{ 	
		'labelEng': 'United States', 
		'score': 42.0, 
		'type': u'loc', 
		'uri': u'http://en.wikipedi...ed_States'}, 
	{ 
		'labelEng': 'Barack Obama', 
		'score': 29.0, 
		'type': 'person', 
		'uri': u'http://en.wikipedi...ack_Obama'}, 
	…
	],
‘events’: { 
	‘resultCount’: 122,
	‘results’: [
		{
			'articleCounts': {	'eng': 54.0, 'total': 54.0}, 
			'categories': [{...}], 
			'concepts': [{...}, ...], 
			'eventDate': '2014-08-29', 
			'eventDateEnd': '', 
			'multiLingInfo': { 
				u'eng': {...}
			}, 
			'uri': '1211229', 
			'wgt': 9.0
		}, …
		]
	},
‘uriList’: ['1211229', '1204045', '1195905', '1175569', …]
}
```

As it can be seen from the result, each requested information has a corresponding property in the returned object and its value holds the returned results.

##Obtaining information about particular event(s)

When information about a particular event is required, one can use the `QueryEvent` class as in the following example:

```python
q = QueryEvent("123")		# get information about single event with URI 123
q.addRequestedResult(RequestEventInfo(["eng", "spa", "slv"]))	# get event information. concept labels should be in three langauges
q.addRequestedResult(RequestEventArticles(0, 10))	# get 10 articles describing the event
q.addRequestedResult(RequestEventArticleTrend())	# get info how articles were trending over time
q.addRequestedResult(RequestEventKeywordAggr())		# get top keywords describing the event
eventRes = er.execQuery(q);							# execute the query
```

In this example we have requested for information about the event with URI “123”. We have asked for event details including the title and summary in English, Spanish and Slovene language. We have also asked for 10 articles about event. Since sorting is not specified, this will return 10 articles that are closest to the center of the clusters. The article trending request will return info about the intensity of new articles at different times, whereas the keyword request will return top keywords for the event.

##Searching for articles

An example of the `QueryArticles` class use when searching for articles is as follows:

```python
q = QueryArticles()		# we want to make a search for articles
q.setDateLimit(datetime.date(2014, 4, 16), datetime.date(2014, 4, 28))		# articles should be in particular date range
q.addKeyword("apple")		# article should contain word apple
q.addKeyword("iphone")		# article should also contain word iphone
q.addRequestedResult(RequestArticlesInfo(page=0, count = 30));	# get 30 articles that match the criteria
res = er.execQuery(q)		# execute the query
```

In this case we specify the time limit to include only articles between 16th and 28th April, 2014. Additionally we specify two keywords to search for – apple and iphone. The resulting information will only contain 30 top articles.

##Obtaining details about individual article(s)

The last example shows the use of the `QueryArticle` class. 

```python
uri = "http://www.bbc.com/news/technology-29139533"
q = QueryArticle(uri);						# get info about article from specified URL
q.addRequestedResult(RequestArticleInfo())	# return available info about the article
q.addRequestedResult(RequestArticleDuplicatedArticles())	# get information about articles that are duplicates of this article
articleRes = er.execQuery(qa)				# execute the query
```

Assuming that uri is a valid URI of an article in the Event Registry, the example requests for article information as well as the list of articles that are duplicates of the article.
