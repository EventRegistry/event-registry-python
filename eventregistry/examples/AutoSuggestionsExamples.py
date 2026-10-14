"""
examples showing how to use the autosuggest functionalities for concepts, sources, categories, locations, ....
"""
import os
import sys

from eventregistry import EventRegistry


def conceptSuggestions(er):
    """
    get the list of concepts that match the given label prefix
    """
    # get concept uris for concepts based on the concept labels:
    conceptUrisMatchingObama = er.suggestConcepts("Obama", lang = "eng", conceptLang = ["eng", "deu"])
    print(conceptUrisMatchingObama)
    # example of the returned output (shortened):
    # [
    #     {"uri": "http://en.wikipedia.org/wiki/Barack_Obama", "type": "person", "score": 7697113, "label": {"eng": "Barack Obama", "deu": "Barack Obama"}},
    #     {"uri": "http://en.wikipedia.org/wiki/Presidency_of_Barack_Obama", "type": "org", "score": 1480934, "label": {"eng": "Presidency of Barack Obama", "deu": "Kabinett Obama"}},
    #     ...
    # ]


def topConceptUri(er):
    """
    get the URI of the concept that best matches the given label
    """
    # get only the top concept that best matches the prefix
    conceptUriForBarackObama = er.getConceptUri("Obama")
    # "http://en.wikipedia.org/wiki/Barack_Obama"
    print("A URI of the top concept that contains the term 'Obama': " + conceptUriForBarackObama)


def categorySuggestions(er):
    """
    get the list of categories that contain the given text
    """
    # return a list of categories that contain text "Business"
    businessRelated = er.suggestCategories("Business")
    print(businessRelated)
    # example of the returned output (shortened):
    # [
    #     {"uri": "dmoz/Business", "label": "dmoz/Business", "parentUri": "dmoz"},
    #     {"uri": "iptc/economy,_business_and_finance", "label": "iptc/economy, business and finance", "parentUri": "iptc"},
    #     ...
    # ]


def topCategoryUri(er):
    """
    get the URI of the category that best matches the given text
    """
    # return the top category that contains text "Business"
    businessCategoryUri = er.getCategoryUri("Business")
    # "dmoz/Business"
    print("A URI of the top category that contains the term 'Business': " + businessCategoryUri)


def locationSuggestions(er):
    """
    get the list of locations that match the given label prefix
    """
    # get a list of locations that best match the prefix "Lond"
    locations = er.suggestLocations("Lond")
    print(locations)
    # example of the returned output (shortened):
    # [
    #     {"type": "place", "wikiUri": "http://en.wikipedia.org/wiki/City_of_London", "label": {"eng": "City of London"}, "lat": 51.51, "long": -0.09, "country": {"type": "country", "wikiUri": "http://en.wikipedia.org/wiki/United_Kingdom", "label": {"eng": "United Kingdom"}, "lat": 54.76, "long": -2.7}, "score": 7556900},
    #     {"type": "place", "wikiUri": "http://en.wikipedia.org/wiki/London", "label": {"eng": "London"}, "lat": 51.51, "long": -0.13, "country": {...}, "score": 7556900},
    #     ...
    # ]


def topLocationUri(er):
    """
    get the URI of the location that best matches the given label prefix
    """
    # get a top location that best matches the prefix "Lond"
    londonUri = er.getLocationUri("Lond")
    # "http://en.wikipedia.org/wiki/City_of_London"
    print("A top location that contains text 'Lond': " + londonUri)


def topLocationUriInCountry(er):
    """
    get the URI of a country and then the URI of the top matching location inside that country
    """
    usUri = er.getLocationUri("united states", sources = "country")
    # "http://en.wikipedia.org/wiki/United_States"
    print(usUri)

    # get a top location for "lond" that is located in USA
    londonUsUri = er.getLocationUri("Lond", countryUri = usUri)
    # "http://en.wikipedia.org/wiki/New_London_County,_Connecticut"
    print("A top US location that contains text 'Lond': " + londonUsUri)


# the examples in this file, in the order in which they are run when "all" is used
EXAMPLES = [
    conceptSuggestions,
    topConceptUri,
    categorySuggestions,
    topCategoryUri,
    locationSuggestions,
    topLocationUri,
    topLocationUriInCountry,
]


def main():
    """
    run the examples that are named on the command line, for example:
        python AutoSuggestionsExamples.py conceptSuggestions
    Use "all" to run all of them. Without arguments we only list the available examples and make no requests
    """
    examples = {example.__name__: example for example in EXAMPLES}
    names = list(examples) if sys.argv[1:] == ["all"] else sys.argv[1:]
    unknown = [name for name in names if name not in examples]
    if unknown or not names:
        if unknown:
            print("Unknown example(s): %s\n" % ", ".join(unknown))
        print("Usage: python %s <example> [<example> ...] | all\n\nAvailable examples:" % os.path.basename(__file__))
        for name, example in examples.items():
            print("  %-23s %s" % (name, (example.__doc__ or "").strip().split("\n")[0]))
        sys.exit(1 if unknown else 0)

    # the API key is read from the EVENTREGISTRY_API_KEY environment variable or from the settings.json file
    # (see README.md in this folder). The examples make real requests, which use the tokens of your account
    er = EventRegistry()
    for name in names:
        print("\n===== %s =====" % name)
        examples[name](er)


if __name__ == "__main__":
    main()
