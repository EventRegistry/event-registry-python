Event Registry is a Python package that can be used to easily access the news data available in [Event Registry](http://eventregistry.org/) through the API. The package can be used to query for articles or events by filtering using a large set of filters, like keywords, concepts, topics, sources, sentiment, date, etc. Details about the News API are available on the [landing page of the product](https://newsapi.ai/).

## Installation

Event Registry package can be installed using Python's pip installer. In the command line, simply type:

    pip install eventregistry

and the package should be installed. Alternatively, you can also clone the package from the [GitHub repository](https://github.com/EventRegistry/event-registry-python). After cloning it, open the command line and run:

    python setup.py install

### Validating installation

To ensure the package has been properly installed run python and type:

```python
import eventregistry
```

If you don't get any error messages, then your installation has been successful.

### Updating the package

As features are added to the package you will need at some point to update it. In case you have downloaded the package from GitHub simply do a `git pull`. If you have installed it using the `pip` command, then simply run

	pip install eventregistry --upgrade

### Authentication and API key

When making queries to Event Registry you will have to use an API key that you can obtain for free. The details on how to obtain and use the key are described in the [Authorization](../../wiki/EventRegistry-class#authorization) section.

## Four simple examples to get you interested

**Print a list of recently articles or blog posts from *US based sources* *with positive sentiment* mentioning phrases *"George Clooney"* or *"Sandra Bullock"***

```python
from eventregistry import *
er = EventRegistry(apiKey = YOUR_API_KEY)

# get the USA URI
usUri = er.getLocationUri("USA")    # = http://en.wikipedia.org/wiki/United_States

q = QueryArticlesIter(
    keywords = QueryItems.OR(["George Clooney", "Sandra Bullock"]),
    minSentiment = 0.4,
    sourceLocationUri = usUri,
    dataType = ["news", "blog"])

# obtain at most 500 newest articles or blog posts, remove maxItems to get all
for art in q.execQuery(er, sortBy = "date", maxItems = 500):
    print(art)
```

**Print a list of most relevant *business* articles from the last month related to *Microsoft* or *Google*. The articles should be in any language (including Chinese, Arabic, ...)**

```python
from eventregistry import *
# allowUseOfArchive=False will allow us to search only over the last month of data
er = EventRegistry(apiKey = YOUR_API_KEY, allowUseOfArchive=False)

# get the URIs for the companies and the category
microsoftUri = er.getConceptUri("Microsoft")    # = http://en.wikipedia.org/wiki/Microsoft
googleUri = er.getConceptUri("Google")          # = http://en.wikipedia.org/wiki/Google
businessUri = er.getCategoryUri("news business")    # = news/Business

q = QueryArticlesIter(
    conceptUri = QueryItems.OR([microsoftUri, googleUri]),
    categoryUri = businessUri)

# obtain at most 500 newest articles, remove maxItems to get all
for art in q.execQuery(er, sortBy = "date", maxItems = 500):
    print(art)
```


**Search for latest events related to Star Wars**

```python
from eventregistry import *
er = EventRegistry(apiKey = YOUR_API_KEY)

q = QueryEvents(keywords = "Star Wars")
q.setRequestedResult(RequestEventsInfo(sortBy = "date", count = 50))   # request event details for latest 50 events

# get the full list of 50 events at once
print(er.execQuery(q))
```

**Search for articles that (a) mention immigration, (b) are related to business, and (c) were published by news sources located in New York City**

```python
from eventregistry import *
er = EventRegistry(apiKey = YOUR_API_KEY)

q = QueryArticlesIter(
    # here we don't use keywords so we will also get articles that mention immigration using various synonyms
    conceptUri = er.getConceptUri("immigration"),
    categoryUri = er.getCategoryUri("business"),
    sourceLocationUri = er.getLocationUri("New York City"))

# obtain 500 articles that have were shared the most on social media
for art in q.execQuery(er, sortBy = "socialScore", maxItems = 500):
    print(art)
```

**What are the currently trending topics**

```python
from eventregistry import *
er = EventRegistry(apiKey = YOUR_API_KEY)

# top 10 trending concepts in the news
q = GetTrendingConcepts(source = "news", count = 10)
print(er.execQuery(q))
```

## Learning from examples

We believe that it's easiest to learn how to use our service by looking at examples. For this reason, we have prepared examples of various most used features. View the examples grouped by main search actions:

[View examples of searching for articles](https://github.com/EventRegistry/event-registry-python/blob/master/eventregistry/examples/QueryArticlesExamples.py)

[View examples of searching for events](https://github.com/EventRegistry/event-registry-python/blob/master/eventregistry/examples/QueryEventsExamples.py)

[View examples of obtaining information about an individual event](https://github.com/EventRegistry/event-registry-python/blob/master/eventregistry/examples/QueryEventExamples.py)

[Examples of how to obtain the full feed of articles](https://github.com/EventRegistry/event-registry-python/blob/master/eventregistry/examples/FeedOfNewArticlesExamples.py)

[Examples of how to obtain the full feed of events](https://github.com/EventRegistry/event-registry-python/blob/master/eventregistry/examples/FeedOfNewEventsExamples.py)

## Play with interactive Jupyter notebook

To interactively learn about how to use the SDK, see examples of use, see how to get extra meta-data properties, and more, please open [this Binder](https://mybinder.org/v2/gh/EventRegistry/event-registry-python-intro/master). You'll be able to view and modify the examples.

## Where to next?

**[Terminology](../../wiki/Terminology)**. There are numerous terms in the Event Registry that you will constantly see. If you don't know what we mean by an *event*, *story*, *concept* or *category*, you should definitely check this page first.

**[Learn about `EventRegistry` class](../../wiki/Eventregistry-class)**. You will need to use the `EventRegistry` class whenever you will want to interact with Event Registry so you should learn about it.

**[Details about articles/events/concepts/categories/... that we can provide](../../wiki/ReturnInfo-class)**. When you will be requesting information about events, articles, concepts, and other things, what details can you ask for each of these?

**[Querying events](../../wiki/Searching-for-events)**. Check this page if you are interested in searching for events that match various search criteria, such as relevant concepts, keywords, date, location or others.

**[Querying articles](../../wiki/Searching-for-articles)**. Read if you want to search for articles based on the publisher's URL, article date, mentioned concepts or others.

**[Trends](../../wiki/Trends)**. Are you interested in finding which concepts are currently trending the most in the news? Maybe which movie actor is most popular in social media? How about trending of various news categories?

**[Articles and events shared the most on social media](../../wiki/Social-shares)**. Do you want to get the list of articles that have been shared the most on Facebook and Twitter on a particular date? What about the most relevant event based on shares on social media?

## Data access and usage restrictions

Event Registry is a commercial service but it allows also unsubscribed users to perform a certain number of operations. Non-paying users are not allowed to use the obtained data for any commercial purposes (see the details on our [Terms of Service page](http://newsapi.ai/terms)) and have access to only last 30 days of content. In order to avoid these restrictions please contact us about the [available plans](http://newsapi.ai/plans).