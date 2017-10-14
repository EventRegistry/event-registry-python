# Change Log

## [v6.6.0]() (2017-XX-XX)

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
