# Code modified from http://www.ardendertat.com/2012/01/11/implementing-search-engines/
# Our acknowledgements to Arden.

#!/usr/bin/env python

import sys
import re
import copy
import gzip
import pickle
import math
import time
from textProcessing import Stemmer
from collections import defaultdict
from testingQuery import  preprocessQuery as opt_query

stemmer = Stemmer()

class DocumentRetriever:

    def __init__(self):
        self.index = {}
        self.tf = {}
        self.idf = {}

    def ngramConversion(self, query):
        words = stemmer.tokenizeAndStemString(query)
        ngram = [ a+b for a,b in zip(words,words[1:]) ]
        return ngram


    def preprocessQuery(self, query):
        # optimize query process using synonym set
        return  opt_query(query)


    def readTrieIndex(self):
        f = gzip.open(self.trieIndexFile, 'rb')
        self.trieIndex = pickle.load(f)


    def dotProduct(self, vec1, vec2):
        if len(vec1) != len(vec2):
            return 0
        return sum([ float(x) * float(y) for x,y in zip(vec1,vec2) ])


    def trieRankDocuments(self, terms, docs):
        threshold = -1
        documentVectors = defaultdict(lambda: [0]*len(terms))
        queryVector = [0]*len(terms)
        for termIndex, term in enumerate(terms):
            try:
                if self.trieIndex.key(term[0]) != term[0]:
                    continue
                matchTermTuple = self.trieIndex.value(term[0])
                self.tf[term[0]] = matchTermTuple[1]
                self.idf[term[0]] = (matchTermTuple[2])
                queryVector[termIndex] = matchTermTuple[2]

                for docIndex, (doc, postings) in enumerate(matchTermTuple[0]):
                    if doc in docs:
                        documentVectors[doc][termIndex] = self.tf[term[0]][docIndex]
            except:
                pass

        docScores = [ [self.dotProduct(curDocVec, queryVector), doc] for doc, curDocVec in documentVectors.items() ]
        docScores.sort(reverse=True)
        resultDocs=[x[1] for x in docScores][:threshold]

        print( resultDocs)
        return resultDocs


    def getRelevantDocuments(self, q):
        q = self.preprocessQuery(q)
        print(q)
        if len(q) == 0:
            print( '')
            return

        documentList = set()


        for term in q:

            try:
                if self.trieIndex.key(term[0]) != term[0]:
                    continue
                print(term[0])
                termPage, (postingList, tf, idf) = self.trieIndex.item(term[0])
                docs = [x[0] for x in postingList]
                # if len(documentList) == 0:
                #    documentList = set(docs)
                if term[1]=='OR':
                    documentList = documentList | set(docs)
                else:
                    documentList = documentList & set(docs)
                # print(documentList)
            except:
                pass

        documentList = list(documentList)
        print(documentList)
        results = self.trieRankDocuments(q, documentList)

        return results


    def getParams(self):
        param = sys.argv
        self.trieIndexFile = param[1]


    def setupDocumentRetriever(self):
        self.getParams()
        self.readTrieIndex()
        while True:
            q = sys.stdin.readline()
        self.getRelevantDocuments(q)


    def parseMultiLine(self, dataset):
        # Parsing the dataset
        text = ""
        line = dataset.readline()
        while line != "" and line[0] != ".":
            text = text + line.strip()
            if text[-1] == "\n":
                text = text[:-1]

            text = text + " "
            line = dataset.readline()
        return text.rstrip(),line

    def evaluateOnQuerySet(self, queryFile, outputFile):
        self.getParams()
        self.readTrieIndex()

        document = {}
        dataset = open(queryFile)
        output = open(outputFile,'w')
        line = dataset.readline()
        while (line != ""):
            if line[:2] == ".I":
                segments = line.split()
                line = dataset.readline()

            elif line[:2] == ".W":
                document[segments[1]],line = self.parseMultiLine(dataset)

            else:
                line = dataset.readline()

        for id, q in document.items():
            print(id, q)
            # DEBUG (to compute MAP)
            if q != '':
                start = int(round(time.time() * 1000))
                results = self.getRelevantDocuments(q)
                stop = int(round(time.time() * 1000))
                t = "query#{}: {}\n {} second\n".format(id, q, stop-start)
                print(t)
                output.write(t)
                for doc_id in results:
                    doc = "HillaryEmails/HillaryEmails/{}.txt\n".format(doc_id)
                    print(doc)
                    output.write(doc)


if __name__=='__main__':
    q = DocumentRetriever()
    # q.setupDocumentRetriever()
    # DEBUG
    q.evaluateOnQuerySet("./query/query.txt", "./query/opt_results.text")
