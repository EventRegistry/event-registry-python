# Examples

Runnable examples of the most used features of the Event Registry Python SDK. Each file contains several small
examples. An example is a function with a descriptive name, a docstring that says what it shows and comments that
explain the details (often also a shortened version of the returned result).

## Setting the API key

The examples create the `EventRegistry` instance without the `apiKey` parameter, so the key has to be available in one
of these ways:

1. in the `EVENTREGISTRY_API_KEY` environment variable

   ```bash
   # Linux / macOS
   export EVENTREGISTRY_API_KEY=your-api-key
   # Windows (cmd)
   set EVENTREGISTRY_API_KEY=your-api-key
   # Windows (PowerShell)
   $env:EVENTREGISTRY_API_KEY = "your-api-key"
   ```

2. in a `settings.json` file, stored in the `.eventregistry` folder in your home directory
   (`~/.eventregistry/settings.json`), with the content

   ```json
   { "apiKey": "your-api-key" }
   ```

You can find your API key on the [dashboard page](https://newsapi.ai/dashboard) of your account (you can
[register](https://newsapi.ai/register) for free). Do not commit the key to a repository.

## Running the examples

Install the package (`pip install eventregistry`, or `pip install -e .` in the root of the cloned repository) and run
a file from this folder:

```bash
# list the examples in the file - this makes no requests
python QueryArticlesExamples.py

# run one example
python QueryArticlesExamples.py articlesWithAllKeywords

# run several examples
python QueryArticlesExamples.py conceptAggr timeAggr

# run all examples in the file
python QueryArticlesExamples.py all
```

Importing an example file makes no requests, so you can also call the examples from your own code:

```python
from eventregistry import EventRegistry
import QueryArticlesExamples

er = EventRegistry()
QueryArticlesExamples.articlesWithAllKeywords(er)
```

## The examples use your tokens

The examples make real requests to the API, and each request uses the tokens of your account, the same as when you
make it from your own code. Run individual examples instead of `all` when you want to keep the usage low. Things to be
aware of:

- running `all` in `QueryArticlesExamples.py` or `QueryEventsExamples.py` makes more than 50 requests
- `iterateOverArticlesPageByPage` in `QueryArticlesExamples.py` and the examples in `QueryEventExamples.py` that iterate
  over the articles of an event download **all** the matching results
- several examples search for content that is older than a month (the archive), which is available only in the paid
  plans
- the examples in `FeedOfNewArticlesExamples.py` and `FeedOfNewEventsExamples.py` repeat a request in a loop and sleep
  in between, so they run for a long time (the ones in `FeedOfNewEventsExamples.py` until you stop them with Ctrl+C)

## Files

| File | What it shows |
| --- | --- |
| [QueryArticlesExamples.py](QueryArticlesExamples.py) | Searching for articles: keywords, concepts, categories, sources, dates, iterating over the results, aggregates of the results (top concepts, categories, sources, keywords, time distribution, ...), recent activity, complex queries and keyword search modes |
| [QueryArticleExamples.py](QueryArticleExamples.py) | Getting the details about individual articles by their URI or URL |
| [QueryEventsExamples.py](QueryEventsExamples.py) | Searching for events: the same kinds of filters, iterators, aggregates, complex queries and keyword search modes as for the articles |
| [QueryEventExamples.py](QueryEventExamples.py) | Getting the details about an individual event: its articles, article trend, keywords, sources and similar events |
| [QueryMentionsExamples.py](QueryMentionsExamples.py) | Searching for mentions of event types (stock price changes, acquisitions, labor issues, ...) by event type, industry, concepts and dates |
| [BreakingEvents.py](BreakingEvents.py) | Getting the list of currently breaking events |
| [FeedOfNewArticlesExamples.py](FeedOfNewArticlesExamples.py) | Getting the feed of articles as they are added to Event Registry - the full stream, or only the articles that match a query |
| [FeedOfNewEventsExamples.py](FeedOfNewEventsExamples.py) | Getting the feed of new and updated events - the full stream, or only the events that match a query |
| [TopicPagesExamples.py](TopicPagesExamples.py) | Creating, loading and saving topic pages and getting the articles and events that match them |
| [TrendsExamples.py](TrendsExamples.py) | Getting the currently trending concepts and categories |
| [CountsExamples.py](CountsExamples.py) | Getting the daily number of articles that mention a concept or belong to a category |
| [AutoSuggestionsExamples.py](AutoSuggestionsExamples.py) | Finding the URIs of concepts, categories and locations from their (partial) labels |
| [EventForTextExamples.py](EventForTextExamples.py) | Finding the events that a given text is about |
| [AnalyticsExamples.py](AnalyticsExamples.py) | Using the text analytics endpoints (sentiment) |
