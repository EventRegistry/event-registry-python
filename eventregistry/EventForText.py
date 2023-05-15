"""
the GetEventForText class can be used to find the event(s) that best matches the given input text.
The request is performed asynchronously.

Note: The functionality can only be used to find the events in the last 5 days. Older events cannot
be matched in this way

Return info from the compute() method is in the form:
[
    {
        "cosSim": 0.07660648086468567,
        "eventUri": "4969",
        "storyUri": "eng-af6ce79f-cb91-4010-8ddf-7ad924bc5638-40591"
    },
    {
        "cosSim": 0.05851939237670918,
        "eventUri": "5157",
        "storyUri": "eng-af6ce79f-cb91-4010-8ddf-7ad924bc5638-56286"
    },
    ...
]

where
* cosSim represents the cosine similarity of the document to the cluster
* eventUri is the uri of the corresponding event in the Event Registry
* storyUri is the uri of the story in the Event Registry
You can use QueryEvent or QueryStory to obtain more information about these events/stories
"""

from eventregistry.Base import *
from eventregistry.ReturnInfo import *
from eventregistry.EventRegistry import EventRegistry

class GetEventForText(QueryParamsBase):
    def __init__(self,
                 eventRegistry: EventRegistry,             # instance of EventRegistry class
                 nrOfEventsToReturn: int = 5):   # number of events to return for the given text
        QueryParamsBase.__init__(self)
        self._er = eventRegistry
        self._nrOfEventsToReturn = nrOfEventsToReturn


    def compute(self, text: str, lang: str = "eng"):
        """
        compute the list of most similar events for the given text
        @param text: text for which to find the most similar event
        @param lang: language in which the text is written
        """
        params = { "lang": lang, "text": text, "topClustersCount": self._nrOfEventsToReturn }
        res = self._er.jsonRequest("/api/v1/getEventForText/getEventForText", params)
        if "topStories" in res:
            return res.get("topStories", [])
        return res

