## Accessing Event Registry data through Python

This library contains classes that allow one to obtain from Event Registry (http://eventregistry.org) all available data, such as news articles, events, trends, etc.

The detailed documentation on how to use the library is available at the [project's wiki page](https://github.com/EventRegistry/event-registry-python/wiki). Examples of use are in the [Examples folder in the repository](https://github.com/EventRegistry/event-registry-python/tree/master/eventregistry/examples).

Changes introduced in the different versions of the module are described in the [CHANGELOG.md](https://github.com/EventRegistry/event-registry-python/blob/master/CHANGELOG.md) as well as on the [Releases](https://github.com/EventRegistry/event-registry-python/releases) page.

## Installation

Event Registry package can be installed using Python's pip installer. In the command line, simply type:

    pip install eventregistry

and the package should be installed. Alternatively, you can also clone the package from the GitHub repository at https://github.com/EventRegistry/event-registry-python. After cloning it, open the command line and run:

    python setup.py install

### Validating installation

To ensure the package has been properly installed run python and type:

```python
import eventregistry
```

If you don't get any error messages then your installation has been successful.

### Updating the package

As features are added to the package you will need at some point to update it. In case you have downloaded the package from GitHub simply do a `git pull`. If you have installed it using the `pip` command, then simply run

	pip install eventregistry --upgrade

### Authentication and API key

When making queries to Event Registry you will have to use an API key that you can obtain for free. The details how to obtain and use the key are described in the [Authorization](../../wiki/EventRegistry-class#authorization) section.

## Three simple examples to make you interested

**Print a list of recently added articles mentioning George Clooney**

```python
from eventregistry import *
er = EventRegistry(apiKey = YOUR_API_KEY)
q = QueryArticlesIter(conceptUri = er.getConceptUri("George Clooney"))
for art in q.execQuery(er, sortBy = "date"):
    print art
```

**Search for latest events related to Star Wars**

```python
from eventregistry import *
er = EventRegistry(apiKey = YOUR_API_KEY)
q = QueryEvents(conceptUri = er.getConceptUri("Star Wars"))
q.setRequestedResult(RequestEventsInfo(sortBy = "date", count=10))   # return event details for last 10 events
print er.execQuery(q)
```

**What are the currently trending topics**

```python
from eventregistry import *
er = EventRegistry(apiKey = YOUR_API_KEY)
# top 10 trending concepts in the news
q = GetTrendingConcepts(source = "news", count = 10)
print er.execQuery(q)
```

## Where to next?

Depending on your interest and existing knowledge of the `eventregistry` package you can check different things:

**[Terminology](../../wiki/Terminology)**. There are numerous terms in the Event Registry that you will constantly see. If you don't know what we mean by an *event*, *story*, *concept* or *category*, you should definitely check this page first.

**[Learn about `EventRegistry` class](../../wiki/Eventregistry-class)**. You will need to use the `EventRegistry` class whenever you will want to interact with Event Registry so you should learn about it.

**[Details about articles/events/concepts/categories/... that we can provide](../../wiki/ReturnInfo-class)**. When you will be requesting information about events, articles, concepts, and other things, what details can you ask for each of these?

**[Querying events](../../wiki/Searching-for-events)**. Check this page if you are interested in searching for events that match various search criteria, such as relevant concepts, keywords, date, location or others.

**[Querying articles](../../wiki/Searching-for-articles)**. Read if you want to search for articles based on the publisher's URL, article date, mentioned concepts or others.

**[Trends](../../wiki/Trends)**. Are you interested in finding which concepts are currently trending the most in the news? Maybe which movie actor is most popular in social media? How about trending of various news categories?

**[Articles and events shared the most on social media](../../wiki/Social-shares)**. Do you want to get the list of articles that have been shared the most on Facebook and Twitter on a particular date? What about the most relevant event based on shares on social media?

**[Daily mentions and sentiment of concepts and categories](../../wiki/Number-of-mentions-in-news-or-social-media)**. Are you interested in knowing how often was a particular concept or category mentioned in the news in the previous two years? How about the sentiment expressed on social media about your favorite politician?

**[Correlations of concepts](../../wiki/Correlations)**. Do you have some time series of daily measurements? Why not find the concepts that correlate the most with it based on the number of mentions in the news.

## Data access and usage restrictions

Event Registry is a commercial service but it allows also unsubscribed users to perform a certain number of operations. Free users are not allowed to use the obtained data for any commercial purposes (see the details on our [Terms of Service page](http://eventregistry.org/terms)). In order to avoid these restrictions please contact us about the [available plans](http://eventregistry.org/pricing).
