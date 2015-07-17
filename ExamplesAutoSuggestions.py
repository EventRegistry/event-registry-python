from EventRegistry import *

er = EventRegistry(host = "http://eventregistry.org", logging = True)

# get concept uris for concepts based on the concept labels:
conceptUrisMatchingObama = er.suggestConcepts("Obama")
# get only the top concept that best matches the prefix
conceptUriForBarackObama = er.getConceptUri("Obama")


businessRelated = er.suggestCategories("Business")
businessCategoryUri = er.getCategoryUri("Business")

locations = er.suggestLocations("Lond")
londonUri = er.getLocationUri("Lond")

classes = er.suggestConceptClasses("auto")