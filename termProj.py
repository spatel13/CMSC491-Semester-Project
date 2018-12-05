import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.chunk import ne_chunk
import wikipedia
import rdflib
import codecs
import requests
from bs4 import BeautifulSoup
import russell as ru
import json

def removeUnicode(text):
	asciiText = ""
	for char in text:
		if(ord(char)<128):
			asciiText = asciiText + char
	return asciiText

#define the topic
e = ""
topic = "Nvidia"
#topic = "nvidia"

try:
    #grab the wikipedia summary
    entity = str(wikipedia.summary(topic,sentences=4).encode('utf-8'))

    #apply NLP processes
    tokens = word_tokenize(removeUnicode(entity))
    gmrTags = pos_tag(tokens)
    gmrChunks = ne_chunk(gmrTags, binary=True)

    #print summary
    print("Topic summary{}".format(topic))
    print(entity)
    print("====")

    #noun phrases
    print("Topic has these noun phrases in 4 sentence summary:")
    gmrNouns = []
    gmrPrev = None
    gmrPhrase = []
    for (token, pos) in gmrTags:
        if pos.startswith('NN'):
            if pos == gmrPrev:
                gmrPhrase.append(token)
            else:
                if gmrPhrase:
                    gmrNouns.append((''.join(gmrPhrase),gmrPrev))
                gmrPhrase = [token]
        else:
            if gmrPhrase:
                gmrNouns.append((''.join(gmrPhrase),gmrPrev))
                gmrPhrase = []
                gmrPrev = pos
            if gmrPhrase:
                gmrNouns.append((''.join(gmrPhrase),pos))
            for noun in gmrNouns:
                print(noun[0])
            print("====")

    #get name entities
    print("Topic summary has these named entities, with description:")
    typeEntity = 'NE'
    gmrEntity = []
    for gmrNE in gmrChunks.subtrees():
        if gmrNE.label() == typeEntity:
            tokens = [t[0] for t in gmrNE.leaves()]
            gmrEntity.append(tokens[0])

    #undup the named entities
    gmrList = []
    for gmrNE in gmrEntity:
        gmrList.append(gmrNE)
    gmrSet = set(gmrList)

    #loop thru set and find meanings of the named entities
    for item in gmrSet:
        print item
        try:
            summary = wikipedia.summary(item, sentences=1)
            print("{}:{}".format(item, summary.encode('utf-8')))
        except wikipedia.exceptions.WikipediaException as e1:
            print "This NE has multiple meanings in Wikipedia"
            continue
except wikipedia.exceptions.WikipediaException as e:
    print e
    print"Wikipedia says to disambiguate"
    
### Dbpedia, augments wikipedia with semantic connections between concepts
dbpedia_url = 'http://dbpedia.org/resource/{}'.format(topic)

# create rdf graph and populate it with rdf triples
grf = rdflib.Graph()
grf.parse(dbpedia_url)

# find out if our topic refers to multiple topics
query = (rdflib.URIRef(dbpedia_url),
         rdflib.URIRef('http://dbpedia.org/ontology/wikiPageDisambiguates'),
         None)
multiples = list(grf.triples(query))

# print out multiple meanings
if len(multiples) > 1:
    print ("Your topic {}:".format(dbpedia_url))
    for subject, verb, object in multiples:
        print('-----can mean : {}'.format(object))
else:
    query = (rdflib.URIRef(dbpedia_url),
             rdflib.URIRef('http://dbpedia.org/ontology/abstract'),
             None)
    summary = list(grf.triples(query))
    for subject, verb, object in summary:
        if object.language == 'en':
            print(object.encode('utf-8'))

def summarizeAndBigram(filename, url):
    # Creating a file object and requesting the html from the link given
    headers = {'User-Agent':'Mozilla/5.0'}
    html = requests.get(url, headers=headers)
    soup = BeautifulSoup(html.text,'html5lib')

    all_paras = soup.find_all("div", {"class": "has-content-area"})

    data_2018=""
    for para in all_paras:
	data_2018 = data_2018 + para.text
	
    article_sum = ru.summarize(data_2018)

    # Print summary gathered above
    print "Summary of data mining article"
    print "Three sentence summary"
    for sent in article_sum['top_n_summary']:
	print removeUnicode(sent)

    
    # Take the data extracted from the site and
    # create the bigrams based on the datas.
    print "--------------------"
    print "Bigrams:"
    asc_2018 = removeUnicode(data_2018)
    bigWords = nltk.tokenize.word_tokenize(asc_2018)
    N = 25
    search = nltk.BigramCollocationFinder.from_words(bigWords)
    search.apply_freq_filter(2)
    search.apply_word_filter(lambda skips: skips in nltk.corpus.stopwords.words('english'))
    
    from nltk import BigramAssocMeasures
    idxJaccard = BigramAssocMeasures.jaccard
    bigrams = search.nbest(idxJaccard,N)
    
    # Print the bigrams after the filter have been applied
    for bigram in bigrams:
	print str(bigram[0]).encode('utf-8')," ", str(bigram[1]).encode('utf-8')

    print
    print

filename = "scientist.rtf"
url = "https://blogs.nvidia.com/blog/2018/06/20/nvidia-chief-scientist-bill-dally-on-how-gpus-ignitied-ai-and-where-his-teams-headed-next/"
summarizeAndBigram(filename, url)

filename = "radiology.rtf"
url = "https://blogs.nvidia.com/blog/2018/11/06/rsna-radiology-transformation-ai/"
summarizeAndBigram(filename, url)

filename = "deep_learning.rtf"
url = "https://blogs.nvidia.com/blog/2018/10/31/deep-learning-mammogram-assessment/"
summarizeAndBigram(filename, url)

filename = "planck.rtf"
url = "https://blogs.nvidia.com/blog/2018/10/29/planck-ai-ships-strikes-right-whales/"
summarizeAndBigram(filename, url)
