# Change Log

## [v8.7]() (2019-10-16)

**Added**

- added `EventRegistry.getServiceStatus()` method that reports status of the services
- `ComplexQueryArticles` and `ComplexQueryEvents` classes now support in the constructor additional filters like `minSentiment`, `maxSentiment`, `minFacebookShares`, `endSourceRankPercentile`, etc.

**Updated**

- `ReturnInfo` classes (`ArticleInfoFlags`, `ConceptInfoFlags`, ...) were updated. Some obsolete parameters were removed and we have added support for kwdargs to supply some very rarely used parameters directly.
- `TopicPage.getArticles` and `TopicPage.getEvents` methods now support also `**kwargs` so that you can now also provide other available parameters that are less frequently used.

**Removed**

- removed `EventRegistry.suggestCustomConcepts()` and `EventRegistry.getCustomConceptUri()` methods. Not used anymore since we are not supporting anymore the correlation feature.


## [v8.6]() (2019-02-22)

**Added**
- We added sentiment, which can now be used in querying of articles and events. The `QueryArticles`, `QueryArticlesIter`, `QueryEvents`, `QueryEventsIter` constructors now all have additional parameters `minSentiment` and `maxSentiment` that can be used to filter the articles and events. The valid values are between -1 (very negative sentiment) and 1 (very positive sentiment). Value 0 represents neutral sentiment.
- Sentiment was also added as a property in the returned articles and events.

**Updated**

- Analytics: We updated `trainTopicOnTweets()`, `trainTopicClearTopic()` and `trainTopicGetTrainedTopic()` methods in the `Analytics` class.
- `Analytics.annotate()` method now supports passing custom parameters that should be used when annotating the text.
- Changed some defaults in the returned data. When searching articles, we now by default return article image and sentiment.


## [v8.5.1]() (2018-12-12)

**Updated**

- Analytics. updated `trainTopicOnTweets()`, `trainTopicClearTopic()` and `trainTopicGetTrainedTopic()` methods in the `Analytics` class.
- `QueryArticles.initWithComplexQuery()` was updated - the parameter `dataType` was removed (since the `dataType` value should be provided in the `$filter` section of the query)
- `TopicPage` now supports setting also the source rank percentile
- `Analytics.extractArticleInfo` now also supports setting the headers and cookies to be used when making the requests



## [v8.5]() (2018-08-29)

**Added**
- Added `Analytics.trainTopicOnTweets()` method that can be used to train a topic by analyzing a group of tweets. See example of usage on the [wiki page](https://github.com/EventRegistry/event-registry-python/wiki/Text-analytics#train-a-topic-based-on-the-tweets).
- Added a group of `Analytics.trainTopic*()` methods that can be used to analyze your own documents and build a topic from them. See example of usage on the [wiki page](https://github.com/EventRegistry/event-registry-python/wiki/Text-analytics#train-a-custom-topic).

## [v8.4]() (2018-08-24)

**Added**
- added `EventRegistry.getUsageInfo()` method, which returns the number of used tokens and the total number of available tokens for the given user. The existing methods `EventRegisty.getRemainingAvailableRequests()` and `EventRegistry.getDailyAvailableRequests()` are still there, but their value is only valid after making at least one request.
- added searching of articles and events based on article authors. You can now provide `authorUri` parameter when creating the `QueryArticles` and `QueryEvents` instances.
- added author related methods to `EventRegistry` class: `EventRegistry.suggestAuthors()` to obtain uris of authors for given (partial) name and `EventRegistry.getAuthorUri()` to obtain a single author uri for the given (partial) name.
- added ability to search articles and events by authors. `QueryArticles` and `QueryEvents` constructors now also accept `authorUri` parameter that can be used to limit the results to articles/events by those authors. Use `QueryOper.AND()` or `QueryOper.OR()` to specify multiple authors in the same query.
- BETA: added a filter for returning only articles that are written by sources that have a certain ranking. The filter can be specified by setting the parameters `startSourceRankPercentile` and `endSourceRankPercentile` when creating the `QueryArticles` instance. The default value for `startSourceRankPercentile` is 0 and for `endSourceRankPercentile` is 100. The values that can be set are not any value between 0 and 100 but has to be a number divisible by 10. By setting `startSourceRankPercentile` to 0 and `endSourceRankPercentile` to 20 you would get only articles from top ranked news sources (according to [Alexa site ranking](https://www.alexa.com/siteinfo)) that would amount to about *approximately 20%* of all matching content. Note: 20 percentiles do not represent 20% of all top sources. The value is used to identify the subset of news sources that generate approximately 20% of our collected news content. The reason for this choice is that top ranked 10% of news sources writes about 30% of all news content and our choice normalizes this effect. This feature could potentially change in the future.
- `QueryEventArticlesIter` is now able to return only a subset of articles assigned to an event. You can use the same filters as with the `QueryArticles` constructor and you can specify them when constructing the instance of `QueryEventArticlesIter`. The same kind of filtering is also possible if you want to use the `RequestEventArticles()` class instead.
- added some parameters and changed default values in some of the result types to reflect the backend changes.
- added optional parameter `proxyUrl` to `Analytics.extractArticleInfo()`. It can be used to download article info through a proxy that you provide (to avoid potential GDPR issues). The `proxyUrl` should be in format `{schema}://{username}:{pass}@{proxy url/ip}`.

## [v8.3.1]() (2018-08-12)

**Updated**
- Text analytics: categorization API now supports additional parameter for determining the taxonomy of interest

## [v8.3.0]() (2018-07-26)

**Updated**
- Important bug fixes related to article and event iterators. The existing classes had issues when accessing the data from the last month as well as historical data.

## [v8.2.1]() (2018-07-19)

**Updated**
- Added some utility methods to the  `TopicPage` class.


## [v8.2.0]() (2018-06-29)

**Added**
- added `TopicPage` class. It can be used to create a topic by specifying keywords, concepts, sources, ... as well as their weights. You can specify a threshold and receive only articles and events that match enough specified conditions to reach the required weight. Alternatively you can simply sort the results by relevance and get the top ranked results that are most related to your topic page. See `TopicPageExamples.py` file for examples on how to use the topic pages.
- added named entity extraction endpoint to `Analytics`. Call `Analytics.ner(text)` to extract named entities.

**Updated**
- sentiment analysis now supports two models - vocabulary based as well as a model using neural networks. Choose the model by specifying the `method` parameter. Possible values for it are `vocabulary` (vocabulary based sentiment analysis, default) or `rnn` (neural networks based model).


## [v8.1.0]() (2018-06-10)

**Added**
- added `blog` data type. Various methods in `EventRegistry` class accept it, such as `suggestNewsSources()`, `suggestSourcesAtPlace()` and `getNewsSourceUri()`.

**Updated**
- `QueryArticlesIter.initWithComplexQuery()` now accepts also the `dataType` parameter (by default `news`).

**Removed**
- Removed the parameter `articleBatchSize` from `QueryArticlesIter.execQuery` since it was not useful. We are always returning the maximum number of results that can be obtained with a single query.


## [v8.0]() (2018-04-10)

**Added**
- Text analytics: added `Analytics.semanticSimilarity` API call. It can be used to determine how semantically related two documents are. The documents can be in the same or different languages.
- Text analytics: added `Analytics.extractArticleInfo` API call. It provides functionality to extract article title, body, date, author and other information from the given URL.
- `dataType` parameter when searching for articles. Event Registry is now separating collected content by data type. The possible values for data type are "news", "pr" (for PR content) and "blogs" (we will start indexing and providing blog content shortly). The dataType parameter can be set in the QueryArticles and QueryArticlesIter classes as well as in the `EventRegistry.getNewsSourceUri` and `EventRegistry.suggestNewsSources`.

**Changed**
- changed params in the GetCounts and GetCountsEx classes.
- `EventRegistry.suggestNewsSources()` and `EventRegistry.getNewsSourceUri()` now also accepts `dataType` parameter, which is by default ["news", "pr"]. It determines what kind of data sources to include in the generated suggestions.
- `QueryArticles` and `QueryArticlesIter` classes now supports additional parameter `dataType` that determines what type of data should be returned. By default, the value is `news`. For now it can also be `pr` or an array with both values.

**Removed**
- Removed the RequestEventArticleUris, RequestArticlesUriList, RequestEventsUriList due to backend changes. Use the equivalent \*UriWgt\* version of the classes.
- Removed RequestArticlesUrlList class since it is not supported anymore.
- Removed `QueryArticles.addRequestedResult()`, `QueryEvents.addRequestedResult()`, `QueryArticle.addRequestedResult()`, `QueryEvent.addRequestedResult()`, and `Query.clearRequestedResults()`. As before, a single result type can be requested per call so the methods are not usable. Use `setRequestedResult()` methods.
- Data model change: We removed the `id` property from different returned data objects. Although the documentation clearly stated that the property is for internal use only, users commonly used the property, which caused potential issues.


## [v6.7.0]() (2017-11-30)

**Added**
- Added a class `Analytics` that can be used to semantically annotate a document, categorize the document into a predefined taxonomy of categories or to detect a language of a text. In future, more analytics methods will be added to this class. NOTE: the functionality is currently in BETA. The API calls or the provided outputs may change in the future.
- Added property `links` into the output of the article format. It contains the list of URLs extracted from the article body (not from the whole HTML but just the part containing the body).
- Added sentiment to the news articles. The `sentiment` property will be by default added to the output format for the article. It can be `null` if the property is not set.

**Removed**
- Removed the flag `details` from all the `*InfoFlags` that had it (`ArticleInfoFlag`, `SourceInfoFlag`, etc.). All the properties provided previously by this property are provided anyway using the other flags.
- Removed the flag `flags` from all the `*InfoFlags`. The flag represents some internal properties that are not publicly useful.


## [v6.6.0]() (2017-10-17)

**Added**
- Added a flag `allowUseOfArchive` to `EventRegistry` constructor. The flag determines if queries made by that EventRegistry instance can use the archive data (data since Jan 2014) or just the recent data (last 31 days of content). Queries made on the archive use more of your data plan tokens so if you just want to use the recent content, make sure that you set the flag to `False`. Note that archive data can be accessed only by paid subscribers.
- Added `EventRegistry.printLastReqStats()` which prints to console some stats regarding the latest executed request. It prints whether the archive was used in the query, the number of tokens used by the request, etc.
- Added a parameter `allowUseOfArchive` to the `EventRegistry.execQuery()` method. It can be used to override the flag about the use of archive that was set when constructing the `Event Registry` class.
- Added version checking on the startup. If your version of the module is of lower value than the latest version, we print a warning.

**Changed**
- Changed the maximum number of articles and events that can be returned per search. The maximum number of returned articles can be 100 and the number of events can be 50.

**Deprecated**

**Removed**
- Removed the query parameters `categoryIncludeSub` and `ignoreCategoryIncludeSub`. The flag is set to true and can not be changed.
- Removed parameter `maxItems` from `QueryArticlesIter.execQuery()` and `QueryEventIter.execQuery()`. The iterator will always cache the maximum number of items that can be returned with a single query.

**Fixed**
- When using the article and event iterators, the iterators now automatically know if the archive should be used when downloading different pages matching the search results.


## [v6.5.1]() (2017-08-21)

**Added**
- `QueryArticles` and `QueryArticlesIter` now support additional constructor argument `keywordsLoc` which allows users to specify where should the keywords provided using `keywords` occur. Default is `body` (the keywords should be mentioned in the body of the article), other valid options are `title` (should be mentioned in the article's title) or `title,body` (should be mentioned anywhere in the article).
- `QueryArticles` and `QueryArticlesIter`: same as `keywordsLoc` determines keyword location for `keywords`, an `ignoreKeywordsLoc` parameter can also be specified for determining the location of the keywords to ignore, which are determined by `ignoreKeywords` parameter.
- When using the advanced query language, you can now also specify `keywordLoc` parameter in the `BaseQuery`.
- added `EventRegistry.suggestLocationsAtCoordinate()` method which returns geographic places near the given geo locations
- added `EventRegistry.suggestSourcesAtCoordinate()` method which returns the list of news sources that are close to the given geographic location
- added `EventRegistry.suggestSourcesAtPlace()` method that can return a list of news sources that we are crawling at the specified place or country. The input argument has to be a location URI obtained by calling `EventRegistry.getLocationUri()`.
- added `EventRegistry.getUrl()` method which for a given query object returns the url that can be used to make a direct HTTP request.
- added `videos` property to `Article` data model. When one or more videos were identified in an article you can retrieve them by setting `video=True` flag in `ArticleInfoFlags`.
- added category weights to articles. Our models currently produce weights for each of the categories associated with an article. The weights are in range 1 to 100. The weights were present even before, but their value was always 100.

**Changed**
- When querying for articles, we now by default return full article body. Previously we returned 300 characters by default.
- `ArticleMapper.getArticleUri()` now returns `None` or `string`, no longer a `list`. We no longer store multiple versions of the articles with the same url.
- we've changed the order of parameters in `ArticleInfoFlags`. In case you didn't set parameter values by name, then check if it matches the desired properties. The change was done to reflect importance and usability of individual parameters.

**Removed**
- `EventRegistry.getArticleUris()` no longer accepts parameter `includeAllVersions`.

**Fixed**
- Use of `QueryArticlesIter` and `QueryEventsIter` now correctly assigns also the weights to the returned articles and events.


## [v6.5.0]() (2017-06-14)

**Added**
- `QueryArticles` and `QueryEvents`: When creating an instance of the class using a parameter that is a list (such as `conceptUri`, `categoryUri`, ...) you can (should) now provide the list using the `QueryItems.AND()` or `QueryItems.OR()` methods to explicitly define whether Boolean `AND` or `OR` should be used between the multiple items. If just a list is provided instead, a warning will be displayed in the console output. If a single value is used for the parameter, it is still perfectly ok to provide it directly as `string`.
- `QueryArticles` and `QueryEvents`: Added two new supported parameters `sourceLocationUri` and `sourceGroupUri`. Parameter `sourceLocationUri` can be used to specify a location URI (obtained with `EventRegistry.getLocationUri`) to use a set of news sources from a specific geographic location. The locations used can be cities or countries. `sourceGroupUri` can be used to use in search a set of news sources that belong to a manually curated list of news sources (such as top business related sources, top entertainment sources, ...). See next item to see how to find the values for this parameter.
- `EventRegistry` class. Added methods `suggestSourceGroups()` and `getSourceGroupUri()` that can be used to get the list of news source groups that match a given name/uri (`suggestSourceGroups()`) or the single top suggestion (`getSourceGroupUri()`). Source groups are  that can be used to find or filter content to a specific set of publishers.
- when querying a list of articles, valid `sortBy` values are now also `sourceAlexaGlobalRank` (global rank of the news source) and `sourceAlexaCountryRank` (country rank of the news source).
- `SourceInfoFlags` flag `image` was added which, if `True` adds `image` and `thumbImage` fields to the returned source information.

**Changed**
- `QueryArticles` and `QueryEvents`: Default values for parameters `conceptUri`, `categoryUri` and other parameters that accept lists were changed from `[]` to `None` to reflect the preference for using `QueryItems` class when specifying an array of values.
- `QueryArticles` and `QueryEvents`: changed method `setArticleUriList()` to a static method `initWithArticleUriList()` to avoid mistakenly creating an instance with query parameters and additionaly caling the `setArticleUriList()`.
- `QueryArticles` and `QueryEvents`: method `initWithComplexQuery()` now accepts also query as a `string` value, not only instances of `ComplexArticleQuery` and `ComplexEventQuery`.
- `SourceInfoFlags` flag `importance` was changed to `ranking` since now we return multiple rankings for the source
- `SourceInfoFlags` flag `tags` was changed to `sourceGroups` since term `tags` was too generic.
- Articles data model has changed: `socialScore` property is now named `shares` to better represent the content. The returned object can now include also shares on Google Plus, Pinterest, LinkedIn. The name of the parameter `socialScore` in `ArticleInfoFlags` was also changed to `shares`.
- Source data model has changed: `importance` property was changed to an object `ranking` containing multiple indicators of source importance.

**Deprecated**
- when sorting articles, `sortBy` value `sourceImportance` is now deprecated. Use value `sourceImportanceRank`. Is is equvalent to reversed value of `sourceImportance` therefore also make sure to negate your existing value of `sortByAsc` value. The parameter was changed to make it comparable to added sorting options `sourceAlexaGlobalRank` and `sourceAlexaCountryRank` which also represent rankings (lower value means better value).

**Removed**
- `QueryArticles` and `QueryEvents`: removed the `conceptOper` parameter. It's functionality is now replaced by providing the array of values inside `QueryItems.AND()` or `QueryItems.OR()`.
- `QueryArticles` and `QueryEvents`: removed the utility methods `addConcept()`, `addLocation()`, `addCategory()`, `addNewsSource()`, `addKeyword()`, `setDateLimit()`, `setDateMentionLimit()`. The values of these parameters should be set when initializing the object. The methods were removed since users used static method `initWithComplexQuery()` and additionally calling these methods which had no effect on the results.



## [v6.4.1](https://github.com/EventRegistry/event-registry-python/tree/6.4.1) (2016-04-11)
[Full Changelog](https://github.com/EventRegistry/event-registry-python/compare/6.3.1...6.4.1)

**Added**
- Added a new query language that can be used to specify arbitrarily complex search queries with multiple subqueries. You can create the complex queries by defining them using the new `ComplexArticleQuery` and `ComplexEventQuery` classes and then passing them to `QueryArticles.initWithComplexQuery()` or `QueryEvents.initWithComplexQuery()`. Alternatively you can pass to the `initWithComplexQuery()` methods also a string containing the JSON object with query definition. The details of the query language are described separately for [event](https://github.com/EventRegistry/event-registry-python/wiki/Searching-for-events#advanced-query-language) and [article](https://github.com/EventRegistry/event-registry-python/wiki/Searching-for-articles#advanced-query-language) queries.
- `ArticleMapped`: method `getArticleUris` has additional parameter `includeAllVersions` where, if True, we return a dict where the `articleUrls` are keys and the value is a list with 0, 1 or more article URIs. More articles uris can occur if the article was updated several times article was updated several times.
- Examples folder was updated with various examples of uses of `QueryEventsIter`, `QueryArticlesIter` and `QueryEventArticlesIter`.

**Changed**
- Classes `GetRecentEvents` and `GetRecentArticles` were updated due to backend changes. If using these classes, you have to update the module to this version, otherwise the calls will not work anymore.
- additional changes to support Python 2.x and Python 3.x were made.

**Removed**
- From all `Get*Info` classes (`GetSourceInfo`, `GetConceptInfo`, ...) we removed the `queryById()` methods. The methods are not supported anymore due to the backend changes.
- Removed methods `QueryArticle.queryById()`, `QueryStory.queryById()` and `QueryEvent.queryById()` since it's not supported anymore by the backend.
- Removed static method `QueryArticle.initWithArticleIdList()` since it's not supported anymore by the backend.
- Removed class `RequestArticlesIdList` that was one of the return types when making `QueryArticles` queries.

- Use Octokit::Client for both .com and Enterprise [\#455](https://github.com/skywinder/github-changelog-generator/pull/455) ([eliperkins](https://github.com/eliperkins))



## [v6.3.1](https://github.com/EventRegistry/event-registry-python/tree/6.3.1) (2016-03-22)
[Full Changelog](https://github.com/EventRegistry/event-registry-python/compare/6.3.0...6.3.1)

**Fixed**
- Iterator bug fixes
- Python 3 support


## [v6.3.0](https://github.com/EventRegistry/event-registry-python/tree/6.3.0) (2017-03-06)
[Full Changelog](https://github.com/EventRegistry/event-registry-python/compare/6.2.2...6.3.0)

**Added**
- Added method `setRequestedResult()` method to `QueryArticles`, `QueryEvents` and `QueryEvent` classes. The method overrides any previously set requested result (compared to method `addRequestedResult` that only adds an additional requested result).

**Changed**
- Changed constructor parameters in `GetRecentEvents` and `GetRecentArticles`.

**Removed**
- removed `EventRegistry.login()` method to login the user. The user should authenticate using the API key that he can obtain on [his settings page](http://eventregistry.org/me?tab=settings).



Template for change log:

**Added**

**Changed**

**Deprecated**

**Removed**

**Fixed**
