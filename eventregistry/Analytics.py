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
        """
        resData = self._er.jsonRequestAnalytics("/api/v1/annotate", { "lang": lang, "text": text })
        return resData


    def categorize(self, text):
        """
        determine the set of up to 5 categories the text is about. Currently, only English text can be categorized!
        @param text: input text to categorize
        """
        resData = self._er.jsonRequestAnalytics("/api/v1/categorize", { "text": text })
        return resData


    def sentiment(self, text):
        """
        determine the sentiment of the provided text
        @param text: input text to categorize
        """
        resData = self._er.jsonRequestAnalytics("/api/v1/sentiment", { "text": text })
        return resData


    def semanticSimilarity(self, text1, text2, distanceMeasure = "cosine"):
        """
        determine the semantic similarity of the two provided documents
        @param text1: first document to analyze
        @param text2: second document to analyze
        @param distanceMeasure: distance measure to use for comparing two documents. Possible values are "cosine" (default) or "jaccard"
        """
        resData = self._er.jsonRequestAnalytics("/api/v1/semanticSimilarity", { "text1": text1, "text2": text2, "distanceMeasure": distanceMeasure })
        return resData


    def detectLanguage(self, text):
        """
        determine the language of the given text
        @param text: input text to analyze
        """
        resData = self._er.jsonRequestAnalytics("/api/v1/detectLanguage", { "text": text })
        return resData