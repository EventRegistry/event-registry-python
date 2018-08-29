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

from eventregistry.Base import *
from eventregistry.ReturnInfo import *

class Analytics:
    def __init__(self, eventRegistry):
        """
        @param eventRegistry: instance of EventRegistry class
        """
        self._er = eventRegistry


    def annotate(self, text, lang = None):
        """
        identify the list of entities and nonentities mentioned in the text
        @param text: input text to annotate
        @param lang: language of the provided document (can be an ISO2 or ISO3 code). If None is provided, the language will be automatically detected
        @returns: dict
        """
        return self._er.jsonRequestAnalytics("/api/v1/annotate", { "lang": lang, "text": text })


    def categorize(self, text, taxonomy = "dmoz"):
        """
        determine the set of up to 5 categories the text is about. Currently, only English text can be categorized!
        @param text: input text to categorize
        @param taxonomy: which taxonomy use for categorization. Options "dmoz" (over 5000 categories in 3 levels, English language only)
            or "news" (general news categorization, 9 categories, any langauge)
        @returns: dict
        """
        return self._er.jsonRequestAnalytics("/api/v1/categorize", { "text": text, "taxonomy": taxonomy })


    def sentiment(self, text, method = "vocabulary"):
        """
        determine the sentiment of the provided text in English language
        @param text: input text to categorize
        @param method: method to use to compute the sentiment. possible values are "vocabulary" (vocabulary based sentiment analysis)
            and "rnn" (neural network based sentiment classification)
        @returns: dict
        """
        assert method == "vocabulary" or method == "rnn"
        endpoint = method == "vocabulary" and "sentiment" or "sentimentRNN"
        return self._er.jsonRequestAnalytics("/api/v1/" + endpoint, { "text": text })


    def semanticSimilarity(self, text1, text2, distanceMeasure = "cosine"):
        """
        determine the semantic similarity of the two provided documents
        @param text1: first document to analyze
        @param text2: second document to analyze
        @param distanceMeasure: distance measure to use for comparing two documents. Possible values are "cosine" (default) or "jaccard"
        @returns: dict
        """
        return self._er.jsonRequestAnalytics("/api/v1/semanticSimilarity", { "text1": text1, "text2": text2, "distanceMeasure": distanceMeasure })


    def detectLanguage(self, text):
        """
        determine the language of the given text
        @param text: input text to analyze
        @returns: dict
        """
        return self._er.jsonRequestAnalytics("/api/v1/detectLanguage", { "text": text })


    def extractArticleInfo(self, url, proxyUrl = None):
        """
        extract all available information about an article available at url `url`. Returned information will include
        article title, body, authors, links in the articles, ...
        @param url: article url to extract article information from
        @param proxyUrl: proxy that should be used for downloading article information. format: {schema}://{username}:{pass}@{proxy url/ip}
        @returns: dict
        """
        params = { "url": url }
        if proxyUrl:
            params["proxyUrl"] = proxyUrl
        return self._er.jsonRequestAnalytics("/api/v1/extractArticleInfo", params)


    def ner(self, text):
        """
        extract named entities from the provided text. Supported languages are English, German, Spanish and Chinese.
        @param text: text on wich to extract named entities
        @returns: dict
        """
        return self._er.jsonRequestAnalytics("/api/v1/ner", {"text": text})


    def trainTopicOnTweets(self, twitterQuery, useTweetText = True, maxConcepts = 20, maxCategories = 10, maxTweets = 2000, notifyEmailAddress = None):
        """
        create a new topic and train it using the tweets that match the twitterQuery
        @param twitterQuery: string containing the content to search for. It can be a Twitter user account (using "@" prefix or user's Twitter url),
                a hash tag (using "#" prefix) or a regular keyword.
        @param useTweetText: do you want to analyze the content of the tweets and extract the concepts mentioned in them? If False, only content shared
            in the articles in the user's tweets will be analyzed
        @param maxConcepts: the number of concepts to save in the final topic
        @param maxCategories: the number of categories to save in the final topic
        @param maxTweets: the maximum number of tweets to collect for the user to analyze
        @param notifyEmailAddress: when finished, should we send a notification email to this address?
        """
        assert maxTweets < 5000, "we can analyze at most 5000 tweets"
        params = {"twitterQuery": twitterQuery,
            "useTweetText": useTweetText, "maxConcepts": maxConcepts, "maxCategories": maxCategories,
            "maxTweets": maxTweets}
        if notifyEmailAddress:
            params["notifyEmailAddress"] = notifyEmailAddress
        return self._er.jsonRequestAnalytics("/api/v1/trainTopicOnTwitter", params)


    def trainTopicCreateTopic(self, name):
        """
        create a new topic to train. The user should remember the "uri" parameter returned in the result
        @returns object containing the "uri" property that should be used in the follow-up call to trainTopic* methods
        """
        return self._er.jsonRequestAnalytics("/api/v1/trainTopic", { "action": "createTopic", "name": name})


    def trainTopicAddDocument(self, uri, text):
        """
        add the information extracted from the provided "text" to the topic with uri "uri"
        @param uri: uri of the topic (obtained by calling trainTopicCreateTopic method)
        @param text: text to analyze and extract information from
        """
        return self._er.jsonRequestAnalytics("/api/v1/trainTopic", { "action": "addDocument", "uri": uri, "text": text})


    def trainTopicFinishTraining(self, uri, maxConcepts = 20, maxCategories = 10, idfNormalization = True):
        """
        add the information extracted from the provided "text" to the topic with uri "uri"
        @param uri: uri of the topic (obtained by calling trainTopicCreateTopic method)
        @param maxConcepts: number of top concepts to save in the topic
        @param maxCategories: number of top categories to save in the topic
        @param idfNormalization: should the concepts be normalized by punishing the commonly mentioned concepts
        @param returns: returns the trained topic: { concepts: [], categories: [] }
        """
        return self._er.jsonRequestAnalytics("/api/v1/trainTopic", {"action": "finishTraining", "uri": uri, "maxConcepts": maxConcepts, "maxCategories": maxCategories, "idfNormalization": idfNormalization})


    def trainTopicGetTrainedTopic(self, uri):
        """
        retrieve topic for the topic for which you have already finished training
        @param uri: uri of the topic (obtained by calling trainTopicCreateTopic method)
        @param returns: returns the trained topic: { concepts: [], categories: [] }
        """
        return self._er.jsonRequestAnalytics("/api/v1/trainTopic", { "action": "getTrainedTopic", "uri": uri })