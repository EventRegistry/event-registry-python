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
from typing import Union, List, Dict, Any
from eventregistry.EventRegistry import EventRegistry

# the names exported by "from eventregistry import *"
__all__ = ["Analytics"]


class Analytics:
    def __init__(self, eventRegistry: EventRegistry):
        """
        Args:
            eventRegistry: instance of EventRegistry class
        """
        self._er = eventRegistry


    def annotate(self, text: str, lang: Union[str, None] = None, customParams: Union[dict, None] = None):
        """
        identify the list of entities and nonentities mentioned in the text

        Args:
            text: input text to annotate
            lang: language of the provided document (can be an ISO2 or ISO3 code). If None is provided, the language will be automatically detected
            customParams: None or a dict with custom parameters to send to the annotation service

        Returns:
            dict
        """
        params = {"lang": lang, "text": text}
        if customParams:
            params.update(customParams)
        return self._er.jsonRequestAnalytics("/api/v1/annotate", params)


    def categorize(self, text: str, taxonomy: str = "dmoz", concepts: Union[List[str], None] = None):
        """
        determine the set of up to 5 categories the text is about. Currently, only English text can be categorized!

        Args:
            text: input text to categorize
            taxonomy: which taxonomy use for categorization. Options "dmoz" (over 5000 categories in 3 levels, English language only)
                or "news" (general news categorization, 9 categories, any langauge)

        Returns:
            dict
        """
        params: Dict[str, Any] = { "text": text, "taxonomy": taxonomy }
        if isinstance(concepts, list) and len(concepts) > 0:
            params["concepts"] = concepts
        return self._er.jsonRequestAnalytics("/api/v1/categorize", params)


    def sentiment(self, text: str, method: str = "vocabulary", sentencesToAnalyze: int = 10, returnSentences: bool = True):
        """
        determine the sentiment of the provided text in English language

        Args:
            text: input text to categorize
            method: method to use to compute the sentiment. possible values are "vocabulary" (vocabulary based sentiment analysis)
                and "rnn" (neural network based sentiment classification)
            sentencesToAnalyze: number of sentences in the provided text on which to compute the sentiment.
            returnSentences: should the output also contain the list of sentences on which we computed sentiment?

        Returns:
            dict
        """
        if not (method == "vocabulary" or method == "rnn"):
            raise ValueError("method should be one of: vocabulary, rnn")
        return self._er.jsonRequestAnalytics("/api/v1/sentiment", { "text": text, "method": method, "sentences": sentencesToAnalyze, "returnSentences": returnSentences })


    def semanticSimilarity(self, text1: str, text2: str, distanceMeasure: str = "cosine"):
        """
        determine the semantic similarity of the two provided documents

        Args:
            text1: first document to analyze
            text2: second document to analyze
            distanceMeasure: distance measure to use for comparing two documents. Possible values are "cosine" (default) or "jaccard"

        Returns:
            dict
        """
        return self._er.jsonRequestAnalytics("/api/v1/semanticSimilarity", { "text1": text1, "text2": text2, "distanceMeasure": distanceMeasure })


    def detectLanguage(self, text: str):
        """
        determine the language of the given text

        Args:
            text: input text to analyze

        Returns:
            dict
        """
        return self._er.jsonRequestAnalytics("/api/v1/detectLanguage", { "text": text })


    def extractArticleInfo(self, url: str, proxyUrl: Union[str, None] = None, headers: Union[str, dict, None] = None, cookies: Union[dict, str, None] = None):
        """
        extract all available information about an article available at url `url`. Returned information will include
        article title, body, authors, links in the articles, ...

        Args:
            url: article url to extract article information from
            proxyUrl: proxy that should be used for downloading article information. format: {schema}://{username}:{pass}@{proxy url/ip}
            headers: dict with headers to set in the request (optional)
            cookies: dict with cookies to set in the request (optional)

        Returns:
            dict
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

        Args:
            text: text on wich to extract named entities

        Returns:
            dict
        """
        return self._er.jsonRequestAnalytics("/api/v1/ner", {"text": text})
