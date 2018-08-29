import unittest, time
import eventregistry as ER
from DataValidator import DataValidator

class TestAnalytics(DataValidator):

    def testConcepts(self):
        analytics = ER.Analytics(self.er)
        annInfo = analytics.annotate("Microsoft released a new version of Windows OS.")
        self.assertTrue("annotations" in annInfo, "Annotations were not provided for the given text")
        anns = annInfo["annotations"]
        self.assertTrue(len(anns) == 2)
        self.assertTrue("url" in anns[0])
        self.assertTrue("title" in anns[0])
        self.assertTrue("lang" in anns[0])
        self.assertTrue("secLang" in anns[0])
        self.assertTrue("secUrl" in anns[0])
        self.assertTrue("secTitle" in anns[0])
        self.assertTrue("wgt" in anns[0])
        self.assertTrue("wikiDataItemId" in anns[0])
        self.assertTrue("adverbs" in annInfo)
        self.assertTrue("adjectives" in annInfo)
        self.assertTrue("verbs" in annInfo)
        self.assertTrue("nouns" in annInfo)
        self.assertTrue("ranges" in annInfo)
        self.assertTrue("language" in annInfo)


    def testCategories(self):
        analytics = ER.Analytics(self.er)
        res = analytics.categorize("Microsoft released a new version of Windows OS.")
        self.assertTrue("categories" in res)
        for catInfo in res["categories"]:
            self.assertTrue("label" in catInfo)
            self.assertTrue("score" in catInfo)


    def testSentiment(self):
        analytics = ER.Analytics(self.er)
        res = analytics.sentiment("""Residents and tourists enjoy holiday weekend even as waves start to pound; beaches remain closed due to dangerous rip currents.
            Despite a state of emergency declared by the governor and warnings about dangerous surf and the possibility of significant coastal flooding, residents and visitors to the Jersey Shore spent Saturday making the most of the calm before the storm.
            Cloudy skies in the morning gave way to sunshine in the afternoon, and despite winds that already were kicking up sand and carving the beach, people flocked to the boardwalk in both Seaside Heights and Point Pleasant Beach, where children rode amusement rides and teens enjoyed ice cream cones. """)
        self.assertTrue("avgSent" in res)
        self.assertTrue("sentimentPerSent" in res)


    def testLanguage(self):
        analytics = ER.Analytics(self.er)
        langInfo = analytics.detectLanguage("Microsoft released a new version of Windows OS.")
        self.assertTrue("languages" in langInfo)
        self.assertTrue("code" in langInfo["languages"][0])
        self.assertTrue("name" in langInfo["languages"][0])
        self.assertTrue("percent" in langInfo["languages"][0])


    def testSemanticSimilarity(self):
        doc1 = "The editor, Carrie Gracie, who joined the network 30 years ago, said she quit her position as China editor last week to protest pay inequality within the company. In the letter posted on her website, she said that she and other women had long suspected their male counterparts drew larger salaries and that BBC management had refused to acknowledge the problem."
        doc2 = "Paukenschlag bei der britischen BBC: Die China-Expertin Carrie Gracie hat aus Protest gegen die illegale Gehaltskultur und damit verbundene Heimlichtuerei ihren Job bei dem öffentlich-rechtlichen Sender hingeworfen. Zwei ihrer männlichen Kollegen in vergleichbaren Positionen würden nachweislich wesentlich besser bezahlt."
        analytics = ER.Analytics(self.er)
        ret = analytics.semanticSimilarity(doc1, doc2)
        self.assertTrue("similarity" in ret)


    def testExtractArticleInfo(self):
        analytics = ER.Analytics(self.er)
        info = analytics.extractArticleInfo("https://www.theguardian.com/world/2018/jan/31/this-is-over-puigdemonts-catalan-independence-doubts-caught-on-camera")
        self.assertTrue("title" in info)
        self.assertTrue("body" in info)
        self.assertTrue("date" in info)
        self.assertTrue("datetime" in info)
        self.assertTrue("image" in info)
        # there can be other additional properties available, depending on what is available in the article


    def testTrainTopic(self):
        analytics = ER.Analytics(self.er)
        ret = analytics.trainTopicCreateTopic("my topic")
        assert ret and "uri" in ret
        uri = ret["uri"]
        analytics.trainTopicAddDocument(uri, "Facebook has removed 18 accounts and 52 pages associated with the Myanmar military, including the page of its commander-in-chief, after a UN report accused the armed forces of genocide and war crimes.")
        analytics.trainTopicAddDocument(uri, "Emmanuel Macron’s climate commitment to “make this planet great again” has come under attack after his environment minister dramatically quit, saying the French president was not doing enough on climate and other environmental goals.")
        analytics.trainTopicAddDocument(uri, "Theresa May claimed that a no-deal Brexit “wouldn’t be the end of the world” as she sought to downplay a controversial warning made by Philip Hammond last week that it would cost £80bn in extra borrowing and inhibit long-term economic growth.")
        # finish training of the topic
        ret = analytics.trainTopicFinishTraining(uri)
        assert ret and "topic" in ret
        topic = ret["topic"]
        assert "concepts" in topic and len(topic["concepts"]) > 0
        assert "categories" in topic and len(topic["categories"]) > 0
        # check that we can also get the topic later on
        ret = analytics.trainTopicGetTrainedTopic(uri)
        assert ret and "topic" in ret
        topic = ret["topic"]
        assert "concepts" in topic and len(topic["concepts"]) > 0
        assert "categories" in topic and len(topic["categories"]) > 0


    def testTrainTopicOnTwitter(self):
        analytics = ER.Analytics(self.er)
        ret = analytics.trainTopicOnTweets("@SeanEllis", maxConcepts = 50, maxCategories = 20, maxTweets = 400)
        assert ret and "uri" in ret
        uri = ret["uri"]
        # here we should sleep more than 5 seconds
        time.sleep(5)
        ret = analytics.trainTopicGetTrainedTopic(uri)
        assert ret and "topic" in ret



if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAnalytics)
    unittest.TextTestRunner(verbosity=2).run(suite)
