"""
the Analytics class can be used for access the text analytics services provided by the Event Registry.
These include:
- text annotation: identifying the list of entities and non-entities mentioned in the provided text
- text categorization: identification of up to 5 categories that describe the topic of the given text.
    The list of available categories come from DMOZ open directory. Currently, only English text can be categorized!
- sentiment detection: what is the sentiment expressed in the given text
- language detection: detect in which language is the given text written

NOTE: the functionality is currently in BETA. The API calls or the provided outputs may change in the future.
"""

import json
from typing import Union, List
from eventregistry.EventRegistry import EventRegistry
from eventregistry.Base import *
from eventregistry.ReturnInfo import *

class Analytics:
    def __init__(self, eventRegistry: EventRegistry):
        """
        @param eventRegistry: instance of EventRegistry class
        """
        self._er = eventRegistry


    def annotate(self, text: str, lang: Union[str, None] = None, customParams: Union[dict, None] = None):
        """
        identify the list of entities and nonentities mentioned in the text
        @param text: input text to annotate
        @param lang: language of the provided document (can be an ISO2 or ISO3 code). If None is provided, the language will be automatically detected
        @param customParams: None or a dict with custom parameters to send to the annotation service
        @returns: dict
        """
        params = {"lang": lang, "text": text}
        if customParams:
            params.update(customParams)
        return self._er.jsonRequestAnalytics("/api/v1/annotate", params)


    def categorize(self, text: str, taxonomy: str = "dmoz", concepts: Union[List[str], None] = None):
        """
        determine the set of up to 5 categories the text is about. Currently, only English text can be categorized!
        @param text: input text to categorize
        @param taxonomy: which taxonomy use for categorization. Options "dmoz" (over 5000 categories in 3 levels, English language only)
            or "news" (general news categorization, 9 categories, any langauge)
        @returns: dict
        """
        params = { "text": text, "taxonomy": taxonomy }
        if isinstance(concepts, list) and len(concepts) > 0:
            params["concepts"] = concepts
        return self._er.jsonRequestAnalytics("/api/v1/categorize", params)


    def sentiment(self, text: str, method: str = "vocabulary", sentencesToAnalyze: int = 10, returnSentences: bool = True):
        """
        determine the sentiment of the provided text in English language
        @param text: input text to categorize
        @param method: method to use to compute the sentiment. possible values are "vocabulary" (vocabulary based sentiment analysis)
            and "rnn" (neural network based sentiment classification)
        @param sentencesToAnalyze: number of sentences in the provided text on which to compute the sentiment.
        @param returnSentences: should the output also contain the list of sentences on which we computed sentiment?
        @returns: dict
        """
        assert method == "vocabulary" or method == "rnn"
        return self._er.jsonRequestAnalytics("/api/v1/sentiment", { "text": text, "method": method, "sentences": sentencesToAnalyze, "returnSentences": returnSentences })


    def semanticSimilarity(self, text1: str, text2: str, distanceMeasure: str = "cosine"):
        """
        determine the semantic similarity of the two provided documents
        @param text1: first document to analyze
        @param text2: second document to analyze
        @param distanceMeasure: distance measure to use for comparing two documents. Possible values are "cosine" (default) or "jaccard"
        @returns: dict
        """
        return self._er.jsonRequestAnalytics("/api/v1/semanticSimilarity", { "text1": text1, "text2": text2, "distanceMeasure": distanceMeasure })


    def detectLanguage(self, text: str):
        """
        determine the language of the given text
        @param text: input text to analyze
        @returns: dict
        """
        return self._er.jsonRequestAnalytics("/api/v1/detectLanguage", { "text": text })


    def extractArticleInfo(self, url: str, proxyUrl: Union[str, None] = None, headers: Union[str, dict, None] = None, cookies: Union[dict, str, None] = None):
        """
        extract all available information about an article available at url `url`. Returned information will include
        article title, body, authors, links in the articles, ...
        @param url: article url to extract article information from
        @param proxyUrl: proxy that should be used for downloading article information. format: {schema}://{username}:{pass}@{proxy url/ip}
        @param headers: dict with headers to set in the request (optional)
        @param cookies: dict with cookies to set in the request (optional)
        @returns: dict
        """
        params = { "url": url }
        if proxyUrl:
            params["proxyUrl"] = proxyUrl
        if headers:
            if isinstance(headers, dict):
                headers = json.dumps(headers)
            params["headers"] = headers
        if cookies:
            if isinstance(cookies, dict):
                cookies = json.dumps(cookies)
            params["cookies"] = cookies
        return self._er.jsonRequestAnalytics("/api/v1/extractArticleInfo", params)


    def ner(self, text: str):
        """
        extract named entities from the provided text. Supported languages are English, German, Spanish and Chinese.
        @param text: text on wich to extract named entities
        @returns: dict
        """
        return self._er.jsonRequestAnalytics("/api/v1/ner", {"text": text})


    def trainTopicOnTweets(self, twitterQuery: str, useTweetText: bool = True, useIdfNormalization: bool = True,
            normalization: str = "linear", maxTweets: int = 2000, maxUsedLinks: int = 500, ignoreConceptTypes: Union[str, List[str]] = [],
            maxConcepts: int = 20, maxCategories: int = 10, notifyEmailAddress: Union[str, None] = None):
        """
        create a new topic and train it using the tweets that match the twitterQuery
        @param twitterQuery: string containing the content to search for. It can be a Twitter user account (using "@" prefix or user's Twitter url),
                a hash tag (using "#" prefix) or a regular keyword.
        @param useTweetText: do you want to analyze the content of the tweets and extract the concepts mentioned in them? If False, only content shared
            in the articles in the user's tweets will be analyzed
        @param useIdfNormalization: normalize identified concepts by their IDF in the news (punish very common concepts)
        @param normalization: way to normalize the concept weights ("none", "linear")
        @param maxTweets: maximum number of tweets to collect (default 2000, max 5000)
        @param maxUsedLinks: maximum number of article links in the tweets to analyze (default 500, max 2000)
        @param ignoreConceptTypes: what types of concepts you would like to ignore in the profile. options: person, org, loc, wiki or an array with those
        @param maxConcepts: the number of concepts to save in the final topic
        @param maxCategories: the number of categories to save in the final topic
        @param maxTweets: the maximum number of tweets to collect for the user to analyze
        @param notifyEmailAddress: when finished, should we send a notification email to this address?
        """
        assert maxTweets < 5000, "we can analyze at most 5000 tweets"
        params = {"twitterQuery": twitterQuery, "useTweetText": useTweetText,
            "useIdfNormalization": useIdfNormalization, "normalization": normalization,
            "maxTweets": maxTweets, "maxUsedLinks": maxUsedLinks,
            "maxConcepts": maxConcepts, "maxCategories": maxCategories }
        if notifyEmailAddress:
            params["notifyEmailAddress"] = notifyEmailAddress
        if len(ignoreConceptTypes) > 0:
            params["ignoreConceptTypes"] = ignoreConceptTypes
        return self._er.jsonRequestAnalytics("/api/v1/trainTopicOnTwitter", params)


    def trainTopicCreateTopic(self, name: str):
        """
        create a new topic to train. The user should remember the "uri" parameter returned in the result
        @returns object containing the "uri" property that should be used in the follow-up call to trainTopic* methods
        """
        return self._er.jsonRequestAnalytics("/api/v1/trainTopic", { "action": "createTopic", "name": name})


    def trainTopicClearTopic(self, uri: str):
        """
        if the topic is already existing, clear the definition of the topic. Use this if you want to retrain an existing topic
        @param uri: uri of the topic (obtained by calling trainTopicCreateTopic method) to clear
        """
        return self._er.jsonRequestAnalytics("/api/v1/trainTopic", { "action": "clearTopic", "uri": uri })


    def trainTopicAddDocument(self, uri: str, text: str):
        """
        add the information extracted from the provided "text" to the topic with uri "uri"
        @param uri: uri of the topic (obtained by calling trainTopicCreateTopic method)
        @param text: text to analyze and extract information from
        """
        return self._er.jsonRequestAnalytics("/api/v1/trainTopic", { "action": "addDocument", "uri": uri, "text": text})


    def trainTopicGetTrainedTopic(self, uri: str, maxConcepts: int = 20, maxCategories: int = 10, idfNormalization: bool = True):
        """
        retrieve topic for the topic for which you have already finished training
        @param uri: uri of the topic (obtained by calling trainTopicCreateTopic method)
        @param maxConcepts: number of top concepts to retrieve in the topic
        @param maxCategories: number of top categories to retrieve in the topic
        @param idfNormalization: should the concepts be normalized by punishing the commonly mentioned concepts
        @param returns: returns the trained topic: { concepts: [], categories: [] }
        """
        return self._er.jsonRequestAnalytics("/api/v1/trainTopic", { "action": "getTrainedTopic", "uri": uri, "maxConcepts": maxConcepts, "maxCategories": maxCategories, "idfNormalization": idfNormalization })