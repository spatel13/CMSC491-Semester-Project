
from nltk.tokenize import word_tokenize
from mltk import pos_tag
from nltk.chunk import ne_chunk
import wikipedia

#define the topic
e = ""
topic = "Nvidia"
#topic = "nvidia"

try:
    #grab the summary
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
