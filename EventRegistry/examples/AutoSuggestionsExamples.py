"""
examples showing how to use the autosuggest functionalities for concepts, sources, categories, locations, ....
"""

import eventregistry as er

eventreg = er.EventRegistry()

# get concept uris for concepts based on the concept labels:
conceptUrisMatchingObama = eventreg.suggestConcepts("Obama")
# get only the top concept that best matches the prefix
conceptUriForBarackObama = eventreg.getConceptUri("Obama")

# return a list of categories that contain text "Business"
businessRelated = eventreg.suggestCategories("Business")
# return the top category that contains text "Business"
businessCategoryUri = eventreg.getCategoryUri("Business")

# get a list of locations that best match the prefix "Lond"
locations = eventreg.suggestLocations("Lond")
# get a top location that best matches the prefix "Lond"
londonUri = eventreg.getLocationUri("Lond")

usUri = eventreg.getLocationUri("united states", source= "country")
# get a top location for "lond" that is located in USA
londonUsUri = eventreg.getLocationUri("Lond", countryUri = usUri)

# suggest a list of concept classes that best match the text "auto"
classes = eventreg.suggestConceptClasses("auto")