
from nltk.tokenize import word_tokenize
from mltk import pos_tag
from nltk.chunk import ne_chunk
import wikipedia
import rdflib

#define the topic
e = ""
topic = "Nvidia"
#topic = "nvidia"

try:
    #grab the wikipedia summary
    entity = str(wikipedia.summary(topic,sentences=4).encode('utf-8'))

    #apply NLP processes
    tokens = word_tokenize(entity)
    gmrTags = pos_tag(token)
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
        gmrlist.append(gmrNE)
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
except wikipedia.exceptions.WikipediaExceptionas e:
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

