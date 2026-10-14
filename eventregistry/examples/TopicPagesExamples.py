"""
examples that show how to create, load, save and use the topic pages
"""
import os
import sys

from eventregistry import EventRegistry, TopicPage, TopicPages, ReturnInfo, ArticleInfoFlags


def getMyTopicPages(er):
    """
    simple call that just retrieves the list of the topics that the user has generated and are owned by him
    For each topic it also prints the uri of the topic and it's label
    """
    topicPages = TopicPages(er)
    topics = topicPages.getMyTopicPages()
    for topic in topics:
        print("%s\t%s" % (topic.get("uri"), topic.get("label", {}).get("eng")))


def createTopicPage1(er):
    """
    create a topic page directly
    """
    topic = TopicPage(er)
    topic.addKeyword("renewable energy", 30)
    topic.addConcept(er.getConceptUri("biofuel"), 50)
    topic.addConcept(er.getConceptUri("solar energy"), 50)
    topic.addCategory(er.getCategoryUri("renewable"), 50)

    # skip articles that are duplicates of other articles
    topic.setArticleHasDuplicateFilter("skipHasDuplicates")
    # return only articles that are about some event that we have detected
    topic.setArticleHasEventFilter("skipArticlesWithoutEvent")

    # get first 2 pages of articles sorted by relevance to the topic page
    arts1 = topic.getArticles(page=1, sortBy="rel")
    arts2 = topic.getArticles(page=2, sortBy="rel")

    # get first page of events
    events1 = topic.getEvents(page=1)

    for res in (arts1, arts2, events1):
        print(er.format(res))


def createTopicPage2(er):
    """
    create a topic page directly, set the article threshold, restrict results to set concepts and keywords
    """
    topic = TopicPage(er)

    topic.addCategory(er.getCategoryUri("renewable"), 50)

    topic.addKeyword("renewable energy", 30)
    topic.addConcept(er.getConceptUri("biofuel"), 50)
    topic.addConcept(er.getConceptUri("solar energy"), 50)
    # require that the results will mention at least one of the concepts and keywords specified
    # (even though they might have the category about renewable energy, that will not be enough
    # for an article to be among the results)
    topic.restrictToSetConceptsAndKeywords(True)

    # limit results to English, German and Spanish results
    topic.setLanguages(["eng", "deu", "spa"])

    # get results that are at most 3 days old
    topic.setMaxDaysBack(3)

    # require that the articles that will be returned should get at least a total score of 30 points or more
    # based on the specified list of conditions
    topic.setArticleThreshold(30)

    # get first page of articles sorted by date (from most recent backward) to the topic page
    arts1 = topic.getArticles(page=1,
        sortBy="date",
        returnInfo=ReturnInfo(
            articleInfo = ArticleInfoFlags(concepts=True, categories=True)
        ))
    for art in arts1.get("articles", {}).get("results", []):
        print(art)


def loadERTopicPage(er):
    """
    load a topic page that was created using the web interface and get the articles and events that match it
    NOTE: change the uri to the uri of one of your topic pages (see getMyTopicPages)
    """
    topic = TopicPage(er)

    # load some topic page that I have created using the web interface
    topic.loadTopicPageFromER("31470f07-0e70-41e6-ba3d-22e92a12b58b")

    arts = topic.getArticles(page=1, sortBy = "date")
    events = topic.getEvents(page=1, count = 50)

    print(er.format(arts))
    print(er.format(events))


def saveAndLoadTopicPage(er):
    """
    get the definition of a topic page as a python dict and create another topic page from it
    """
    topic = TopicPage(er)
    topic.addKeyword("renewable energy", 30)

    arts1 = topic.getArticles(page=1)

    # get the definition of the topic page as a python dict
    # you can save this dict and later load it
    definition = topic.saveTopicPageDefinition()

    topic2 = TopicPage(er)
    topic2.loadTopicPageFromDefinition(definition)

    arts2 = topic2.getArticles(page=1)

    # arts1 and arts2 should be (almost) the same
    for res in (arts1, arts2):
        print("%d matching articles" % res.get("articles", {}).get("totalResults", 0))


def saveAndLoadTopicPageFromFile(er):
    """
    save the definition of a topic page to a file (topic.json in the current folder) and load it from there
    """
    topic = TopicPage(er)
    topic.addKeyword("renewable energy", 30)

    arts1 = topic.getArticles(page=1)

    # save the definition to a file and later load it
    topic.saveTopicPageDefinitionToFile("topic.json")

    topic2 = TopicPage(er)
    topic2.loadTopicPageFromFile("topic.json")

    arts2 = topic2.getArticles(page=1)

    # arts1 and arts2 should be (almost) the same
    for res in (arts1, arts2):
        print("%d matching articles" % res.get("articles", {}).get("totalResults", 0))


# the examples in this file, in the order in which they are run when "all" is used
EXAMPLES = [
    getMyTopicPages,
    createTopicPage1,
    createTopicPage2,
    loadERTopicPage,
    saveAndLoadTopicPage,
    saveAndLoadTopicPageFromFile,
]


def main():
    """
    run the examples that are named on the command line, for example:
        python TopicPagesExamples.py getMyTopicPages
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
            print("  %-28s %s" % (name, (example.__doc__ or "").strip().split("\n")[0]))
        sys.exit(1 if unknown else 0)

    # the API key is read from the EVENTREGISTRY_API_KEY environment variable or from the settings.json file
    # (see README.md in this folder). The examples make real requests, which use the tokens of your account
    er = EventRegistry()
    for name in names:
        print("\n===== %s =====" % name)
        examples[name](er)


if __name__ == "__main__":
    main()
