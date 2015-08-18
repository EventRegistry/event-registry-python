from EventRegistry import *

er = EventRegistry(host = "http://eventregistry.org", logging = True)

# get concept uris for concepts based on the concept labels:
conceptUrisMatchingObama = er.suggestConcepts("Obama")
# get only the top concept that best matches the prefix
conceptUriForBarackObama = er.getConceptUri("Obama")

# return a list of categories that contain text "Business"
businessRelated = er.suggestCategories("Business")
# return the top category that contains text "Business"
businessCategoryUri = er.getCategoryUri("Business")

# get a list of locations that best match the prefix "Lond"
locations = er.suggestLocations("Lond")
# get a top location that best matches the prefix "Lond"
londonUri = er.getLocationUri("Lond")

# suggest a list of concept classes that best match the text "auto"
classes = er.suggestConceptClasses("auto")