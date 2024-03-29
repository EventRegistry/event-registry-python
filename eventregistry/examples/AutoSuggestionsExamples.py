﻿"""
examples showing how to use the autosuggest functionalities for concepts, sources, categories, locations, ....
"""

from eventregistry import *

er = EventRegistry()

# get concept uris for concepts based on the concept labels:
conceptUrisMatchingObama = er.suggestConcepts("Obama", lang = "eng", conceptLang = ["eng", "deu"])
print(conceptUrisMatchingObama)

# get only the top concept that best matches the prefix
conceptUriForBarackObama = er.getConceptUri("Obama")
print("A URI of the top concept that contains the term 'Obama': " + conceptUriForBarackObama)


# return a list of categories that contain text "Business"
businessRelated = er.suggestCategories("Business")
print(businessRelated)

# return the top category that contains text "Business"
businessCategoryUri = er.getCategoryUri("Business")
print("A URI of the top category that contains the term 'Business': " + businessCategoryUri)


# get a list of locations that best match the prefix "Lond"
locations = er.suggestLocations("Lond")
print(locations)

# get a top location that best matches the prefix "Lond"
londonUri = er.getLocationUri("Lond")
print("A top location that contains text 'Lond': " + londonUri)


usUri = er.getLocationUri("united states", sources = "country")
print(usUri)

# get a top location for "lond" that is located in USA
londonUsUri = er.getLocationUri("Lond", countryUri = usUri)
print("A top US location that contains text 'Lond': " + londonUsUri)


# suggest a list of concept classes that best match the text "auto"
classes = er.suggestConceptClasses("auto")
print(classes)