# Event Registry / NewsAPI.ai Python SDK

`eventregistry` is a Python package for accessing the news data available in [Event Registry](https://eventregistry.org/) through its API. It can be used to search for articles or events using a large set of filters, like keywords, concepts, categories, sources, sentiment, date, etc., to follow the feed of new content and to compute summaries (top sources, concepts, sentiment, ...) of the matching content. Details about the News API are available on the [landing page of the product](https://newsapi.ai/).

## Installation

The package requires **Python 3.9 or newer**. Install it with pip:

    pip install eventregistry

To update an existing installation to the latest version:

    pip install eventregistry --upgrade

To check the installation, run python and type:

```python
import eventregistry
print(eventregistry.__version__)
```

When updating to a new major version, see the [migration guide](https://github.com/EventRegistry/event-registry-python/wiki/Migration-guide) for the changes that can require an update of your code.

## API key

To make requests you need an API key, which you get for free by [registering](https://newsapi.ai/register) - it is shown on your [dashboard](https://newsapi.ai/dashboard). The key can be provided in one of these ways (the first one found is used):

1. as the `apiKey` argument: `EventRegistry(apiKey = "YOUR_API_KEY")`
2. in the `EVENTREGISTRY_API_KEY` environment variable
3. in a `settings.json` file with the content `{ "apiKey": "YOUR_API_KEY" }`, stored in the `.eventregistry` folder of your home directory (`~/.eventregistry/settings.json`)

With the environment variable or the settings file the key stays out of your code and you can simply create the instance with `EventRegistry()`. See [Authorization](https://github.com/EventRegistry/event-registry-python/wiki/EventRegistry-class#authorization) for details.

## Examples

**Iterate over the articles: the newest articles from US based sources, with positive sentiment, that mention "George Clooney" or "Sandra Bullock"**

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

# obtain at most 500 newest articles or blog posts; remove maxItems to get all
for art in q.execQuery(er, sortBy = "date", maxItems = 500):
    print(art["dateTime"], art["title"])
```

**Search by concepts instead of keywords: business articles from the last month related to Microsoft or Google, in any language**

```python
from eventregistry import *
# allowUseOfArchive = False limits the search to the last month of data (and uses fewer tokens)
er = EventRegistry(apiKey = YOUR_API_KEY, allowUseOfArchive = False)

q = QueryArticlesIter(
    conceptUri = QueryItems.OR([er.getConceptUri("Microsoft"), er.getConceptUri("Google")]),
    categoryUri = er.getCategoryUri("news business"))

for art in q.execQuery(er, sortBy = "date", maxItems = 500):
    print(art["title"])
```

**Search for the latest events related to Star Wars**

```python
from eventregistry import *
er = EventRegistry(apiKey = YOUR_API_KEY)

q = QueryEvents(keywords = "Star Wars")
q.setRequestedResult(RequestEventsInfo(sortBy = "date", count = 50))   # request event details for latest 50 events

# get the full list of 50 events at once
print(er.execQuery(q))
```

**Combine conditions with a complex query: articles about electric vehicles or batteries, published in January 2024 by German or French sources, that don't mention Tesla**

```python
from eventregistry import *
er = EventRegistry(apiKey = YOUR_API_KEY)

electricVehicleUri = er.getConceptUri("electric vehicle")   # = "http://en.wikipedia.org/wiki/Electric_vehicle"
batteryUri = er.getConceptUri("electric battery")           # = "http://en.wikipedia.org/wiki/Electric_battery"
teslaUri = er.getConceptUri("Tesla")                        # = "http://en.wikipedia.org/wiki/Tesla,_Inc."
germanyUri = er.getLocationUri("Germany")                   # = "http://en.wikipedia.org/wiki/Germany"
franceUri = er.getLocationUri("France")                     # = "http://en.wikipedia.org/wiki/France"

# the query in the JSON format of the complex query language (a python dict or a string with the JSON object)
query = {
    "$query": {
        "conceptUri": {
            "$or": [electricVehicleUri, batteryUri]
        },
        "sourceLocationUri": {
            "$or": [germanyUri, franceUri]
        },
        "dateStart": "2024-01-01",
        "dateEnd": "2024-01-31",
        "$not": {
            "conceptUri": teslaUri
        }
    }
}
q = QueryArticlesIter.initWithComplexQuery(query)
for art in q.execQuery(er, sortBy = "date", maxItems = 100):
    print(art["title"])
```

**Handle the errors**

Failed requests raise exceptions derived from `EventRegistryError`. Requests that fail with a temporary error (connection problem, timeout, server error) are first repeated automatically (3 times by default, see the `repeatFailedRequestCount` parameter). Requests rejected because too many requests are made at the same time (status 429) are repeated until they succeed, so an iteration over the results is not interrupted.

```python
from eventregistry import *
er = EventRegistry(apiKey = YOUR_API_KEY)

q = QueryArticlesIter(keywords = "Tesla", lang = "eng")
try:
    for art in q.execQuery(er, sortBy = "date", maxItems = 100):
        print(art["title"])
except AccessError as ex:
    # status 401 or 403: invalid API key, no more tokens or a disabled account
    print("Check your API key and tokens:", ex.responseText)
except QueryError as ex:
    print("The server could not execute the query:", ex)
except EventRegistryError as ex:
    print("The request failed with status %s: %s" % (ex.statusCode, ex))
```

## Documentation

The documentation is on the [wiki pages](https://github.com/EventRegistry/event-registry-python/wiki):

* **[Quickstart recipes](https://github.com/EventRegistry/event-registry-python/wiki/Quickstart-recipes)** - copy-paste-ready scripts for the most common tasks, including paging, limits and token usage
* [Terminology](https://github.com/EventRegistry/event-registry-python/wiki/Terminology) - what we mean by an *event*, *story*, *concept* or *category*
* [`EventRegistry` class](https://github.com/EventRegistry/event-registry-python/wiki/EventRegistry-class) - the main class, API key, autosuggest methods
* [Searching for articles](https://github.com/EventRegistry/event-registry-python/wiki/Searching-for-articles), [events](https://github.com/EventRegistry/event-registry-python/wiki/Searching-for-events) and [mentions](https://github.com/EventRegistry/event-registry-python/wiki/Searching-for-mentions) (requires special access)
* [`ReturnInfo` class](https://github.com/EventRegistry/event-registry-python/wiki/ReturnInfo-class) and the [data models](https://github.com/EventRegistry/event-registry-python/wiki/Data-models) - what details can be returned about articles, events, concepts, sources, ...
* [Topic pages](https://github.com/EventRegistry/event-registry-python/wiki/Topic-pages) and the [feed of new articles/events](https://github.com/EventRegistry/event-registry-python/wiki/Feed-of-new-articles-events) - monitoring of new content
* [Trends](https://github.com/EventRegistry/event-registry-python/wiki/Trends) and [text analytics](https://github.com/EventRegistry/event-registry-python/wiki/Text-analytics)
* [Usage tracking](https://github.com/EventRegistry/event-registry-python/wiki/Usage-tracking) - tokens and how to check their use
* **[Errors and troubleshooting](https://github.com/EventRegistry/event-registry-python/wiki/Errors-and-troubleshooting)** - the exceptions, retries, the limit of 5 simultaneous requests, logging, common mistakes
* **[Migration guide](https://github.com/EventRegistry/event-registry-python/wiki/Migration-guide)** - updating from version 9 to 10 and from 10 to 11

Other resources:

* [Examples folder](https://github.com/EventRegistry/event-registry-python/tree/master/eventregistry/examples) - runnable examples of the most used features. Each file contains several examples as functions; `python QueryArticlesExamples.py` lists them and `python QueryArticlesExamples.py <name>` runs one.
* [API reference](https://eventregistry.github.io/event-registry-python/) - all the classes and methods, generated from the docstrings
* [Change log](https://github.com/EventRegistry/event-registry-python/blob/master/CHANGELOG.md) - the changes in each version
* [Interactive Jupyter notebook](https://mybinder.org/v2/gh/EventRegistry/event-registry-python-intro/master) - examples that you can view and modify in the browser

The package contains type hints (`py.typed`), so editors and type checkers know the arguments of the classes and methods.

## Running the tests

Clone the [repository](https://github.com/EventRegistry/event-registry-python) and install the package with the test dependencies:

    pip install -e ".[test]"

The tests need no API key and no network access:

    python -m unittest eventregistry.tests.TestOfflineUnit eventregistry.tests.TestRequestPayloads eventregistry.tests.TestQueryParamsBase

## Reporting issues

Please report bugs and suggestions on the [GitHub issues page](https://github.com/EventRegistry/event-registry-python/issues). Include the version of the package (`eventregistry.__version__`), a short piece of code that reproduces the problem (without your API key) and the full error message. For questions about your account, tokens or the data, use the contact options on [newsapi.ai](https://newsapi.ai/).

## Data access and usage restrictions

Event Registry is a commercial service but it allows also unsubscribed users to perform a certain number of operations. Non-paying users are not allowed to use the obtained data for any commercial purposes (see the details on our [Terms of Service page](https://newsapi.ai/terms)) and have access to only last 30 days of content. In order to avoid these restrictions please contact us about the [available plans](https://newsapi.ai/plans).
