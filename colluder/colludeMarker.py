#! /usr/bin/python2.4


__author__ = 'jhebert@cs.washington.edu (Jack Hebert)'

import relation
import stopWorder
import porterStemmer
from relationReader import RelationReader



class Marker:
    def __init__(self):
        #self.inputFileName = 'relations2.dat'
        self.inputFileName = 'relations3.dat'
        self.relationReader = RelationReader()
        self.stopWorder = stopWorder.StopWorder()
        self.stemmer = porterStemmer.PorterStemmer()
        self.articleMatches = {}
        self.articleToRelation = {}
        self.magicMatchNumber = 2

    def Init(self):
        print 'Initing CollusionMarker...'
        self.stopWorder.Init()
        self.relationReader.Open(self.inputFileName)

    def run(self):
        print 'Running CollusionMarker...'
        self.GetRelationMatches()
        self.GetArticleToRelations()
        self.MarkAllGoodRelations()

    def GetRelationMatches(self):
        print 'Getting relation matches...'
        data=open('out-articleMatches.dat').read().split('\n')
        for line in data:
            if(len(line)<3):
                continue
            items = line.split('\t')
            key, rest = items[0], items[1:]
            self.articleMatches[key] = rest

    def GetArticleToRelations(self):
        print 'Getting article to relation map...'
        rel = self.relationReader.ReadNextRelation()
        while(rel != None):
            url = rel.articleURL
            relationText = rel.RelationAsText().lower() # stopword?
            relationText = self.stopWorder.CleanText(relationText)
            relationText = self.stemmer.stem(relationText,0,len(relationText)-1)
            if(not (url in self.articleToRelation)):
                self.articleToRelation[url] = []
            self.articleToRelation[url].append((relationText, rel.RelationAsText()))
            rel = self.relationReader.ReadNextRelation()

    def MarkAllGoodRelations(self):
        print 'Marking all good relations...'
        toSort, toWrite = [], []
        count, oldPercent = 0, None
        for article in self.articleMatches:
            count += 1
            percent=int(100*float(count) / len(self.articleMatches))
            if(percent != oldPercent):
                print str(percent)+'% done.'
                oldPercent = percent
            maxCount, matches = self.GetImportantRelations(article)
            toSort.append((maxCount, article, matches))

        toSort.sort()
        toSort.reverse()
        for item in toSort:
            count, article, matches = item
            toWrite.append('Article: '+str(article))
            toWrite.append('\n'.join(['\t'+str(a) for a in matches]))
            toWrite.append('\n'*2)
        f = open('out-finalOutput.dat', 'w')
        f.write('\n'.join(toWrite))
        f.close()
        print '\n'.join(toWrite)

    def GetImportantRelations(self, article):
        """ This needs to mark which relations overlap most. """
        hits, maxCount = {}, 0
        # Loops should probably be structure the other way.
        for rp1 in self.articleToRelation[article]:
            r1, r1orig = rp1
            relationCount = 0
            for art in self.articleMatches[article]:
                for rp2 in self.articleToRelation[art]:
                    r2, r2orig = rp2
                    relationCount += 1
                    if(self.GoodMatch(r1, r2)):
                        if(not(r1orig in hits)):
                            hits[r1orig] = 0
                        hits[r1orig] += 1
            if(r1orig in hits):
                #hits[r1orig] = float(hits[r1orig]) / relationCount
                if(hits[r1orig] > maxCount):
                    maxCount = hits[r1orig]
        toSort = [(hits[a], a) for a in hits]
        toSort.sort()
        toSort.reverse()
        return (maxCount, [str(a[0])+': '+str(a[1]) for a in toSort])


    def GoodMatch(self, r1, r2):
        words, count = {}, 0
        for word in r1.split():
            words[word] = None
        for word in r2.split():
            if(word in words):
                count += 1
        return (count > self.magicMatchNumber)


def main():
    m = Marker()
    m.Init()
    m.run()


if(__name__ == '__main__'):
    main()
