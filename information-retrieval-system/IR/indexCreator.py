# Code modified from http://www.ardendertat.com/2012/01/11/implementing-search-engines/
# Our acknowledgements to Arden.

#!/usr/bin/env python

import sys
import re
import pickle
import gzip
from collections import defaultdict
from array import array
import math
from textProcessing import Stemmer
from patricia import trie
import  time
stemmer = Stemmer()

# import nltk
# nltk.download("punkt")
# from nltk.stem import PorterStemmer
# # from nltk.tokenize import sent_tokenize, word_tokenize
# import nltk.tokenize as token
# ps = PorterStemmer()

class IndexBuilder:

    def __init__(self):
        self.index=defaultdict(list)    #the inverted index
        self.tf=defaultdict(list)       #term frequencies of terms in documents
                                        #documents in the same order as in the main index
        self.df=defaultdict(int)        #document frequencies of terms in the corpus
        self.docCount=0

    def parseArgs(self):
        param=sys.argv
        self.datasetFile=param[1]
        self.trieIndexFile=param[2]
        self.postingListFile=param[3]

    def ngramConversion(self, query):
        words = stemmer.tokenizeAndStemString(query)

        ngram = words
        ngram += [ a+b for a,b in zip(words,words[1:]) ]
        ngram += [ a+b+c for a,b,c in zip(words,words[1:],words[2:]) ]
        return ngram

    def getTokens(self, line):
        line=line.lower()
        # replace weird chars by spaces
        line=re.sub(r'[^a-z0-9 ]',' ',line)
        line = stemmer.tokenizeAndStemString(line)
        # line = self.ngramConversion(line)
        return line


    def parseDataset(self):
        # Parsing the XML file to get relevant fields in the document
        doc=[]
        for line in self.dataset:
            if line.strip()=='</document>':
                break
            doc.append(line)

        curPage=''.join(doc)
        pageid=re.search('<id>(.*?)</id>', curPage, re.DOTALL)
        pagefrom=re.search('<from>(.*?)</from>', curPage, re.DOTALL)
        pageto=re.search('<to>(.*?)</to>', curPage, re.DOTALL)
        pagesubject=re.search('<subject>(.*?)</subject>', curPage, re.DOTALL)
        pagemessage= re.search('<message>(.*?)</message>', curPage, re.DOTALL)

        if pageid==None:
            return {}

        d={}
        d['id']=pageid.group(1)

        if pagefrom != None:
            d['from']=pagefrom.group(1)
        else:
            d['from']=''

        if pageto != None:
            d['to']=pageto.group(1)
        else:
            d['to']=''

        if pagesubject != None:
            d['subject']=pagesubject.group(1)
        else:
            d['subject']=''
        if pagemessage != None:
            d['message'] = pagemessage.group(1)
        else:
            d['message'] = ''
        return d

    def writePostingListToFile(self):
        # Writes the posting list to file for evaluation
        # Gzip enables an improvement in the size requirement
        # f=open(self.postingListFile, 'w')
        f=gzip.GzipFile(self.postingListFile, 'w')

        # first line is the number of documents
        # print >>f, self.docCount

        f.write(str(self.docCount).encode())
        # print(str.encode(str(self.docCount)), file=f)
        self.docCount=float(self.docCount)
        for term in self.index.keys():
            postinglist=[]
            for p in self.index[term]:
                docID=p[0]
                positions=p[1]
                postinglist.append(':'.join([str(docID) ,','.join(map(str,positions))]))
            postingData=';'.join(postinglist)
            # print >> f, '|'.join((term, postingData))
            # print(bytes('|'.join((term, postingData))),  f)
            f.write(('|'.join((term, postingData)).encode()))
        f.close()


    def constructTrieIndex(self):
        self.trieIndex = trie('root')
        with open("./output/items.txt", "w") as f:
            f.write("{}\n{}\n{}\n{}\n".format("term","postingList", "tf", "df"))
            for termPage, postingList in self.index.items():
                idfData = math.log(float(self.docCount)/float(self.df[termPage]), 10)
                self.trieIndex[termPage] = (postingList, self.tf[termPage], idfData)
                f.write("{}\n{}\n{}\n{}\n".format(termPage,postingList, self.tf[termPage], idfData))


    def saveTrieIndexToFile(self):
        pickleDumpProtocol = -1
        # dumpFile = open(self.trieIndexFile, "wb")
        dumpFile = gzip.GzipFile(self.trieIndexFile, "wb")
        print(self.trieIndex)
        pickle.dump(self.trieIndex, dumpFile, pickleDumpProtocol)
        dumpFile.close()

    def findNormalizationConst(self, termdictPage):
        normalizationConst=0
        for term, posting in termdictPage.items():
            normalizationConst+=len(posting[1])**2
        normalizationConst=math.sqrt(normalizationConst)
        return normalizationConst

    def buildIndex(self):
        start = time.time()
        self.parseArgs()
        self.dataset=open(self.datasetFile,'r')

        count = 0
        pagedict=self.parseDataset()
        while pagedict != {}:
            lines='\n'.join((pagedict['from'],pagedict['to'],pagedict['subject'], pagedict["message"]))
            pageid=int(pagedict['id'])
            terms=self.getTokens(lines)

            self.docCount+=1

            # current page
            termdictPage={}
            for position, term in enumerate(terms):
                try:
                    termdictPage[term][1].append(position)
                except:
                    termdictPage[term]=[pageid, array('I',[position])]

            normalizationConst=self.findNormalizationConst(termdictPage)

            # Find TFs and DFs
            for term, posting in termdictPage.items():
                self.tf[term].append('%.4f' % (len(posting[1])/normalizationConst))
                self.df[term]+=1

            # current page now being added to main index
            for termPage, postingPage in termdictPage.items():
                self.index[termPage].append(postingPage)

            # Increments and reads and parses the next doc
            pagedict=self.parseDataset()
            count += len(termdictPage.keys())

        self.constructTrieIndex()
        self.writePostingListToFile()
        self.saveTrieIndexToFile()
        end = time.time()
        print("index number:{}\n".format(count))
        print("total time: {}; time for each index:{} milli second\n".format(int(1000*(end-start), int(1000*(end-start)/count))))


if __name__=="__main__":
    invertedIndex = IndexBuilder()
    invertedIndex.buildIndex()
