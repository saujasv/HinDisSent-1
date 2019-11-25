#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

import os 
import codecs
from operator import itemgetter

import folderWalk as fw

class discourseRelation() :
    ''' Discourse Relation class. This class includes all the components of a discourse relation. '''

    def __init__(self, relationType , connSpan , arg1Span , arg2Span , sense) :
        ''' Takes Type of the Relation, connective Span, Argument Spans and Sense as input '''
        self.relationType = relationType
        self.connSpan = connSpan
        self.arg1Span = arg1Span
        self.arg2Span = arg2Span
        self.sense = sense
        self.arg1 = None
        self.arg2 = None
        self.conn = None
        self.isPaired = False
        self.connTrees = []
        self.arg1Trees = []
        self.arg2Trees = []
        self.arg1Sentence = []
        self.arg2Sentence = []
        self.fileName = None
        
    def updateSense(self , sense) :
        ''' Update the sense field '''
        self.sense = sense
        
    def updateArg1Span(self , arg1Span) :
        ''' Update the span value for Argument-1 '''
        self.arg1Span = arg1Span
        
    def updateArg2Span(self , arg2Span) :
        ''' Update the span value for Argument-2 '''
        self.arg2Span = arg2Span
        
    def updateRelationType(self , relationType) :
        ''' Update the type of the discourse relation '''
        self.relationType = relationType

    def populateRelationText(self,data) :
        ''' Takes Raw Text as data and populates the argument-texts from the already stored span values ''' 
        self.conn = ''
        if self.relationType in ['Explicit', 'AltLex'] :
                self.conn = seekPrint(data,self.connSpan)
        self.arg1 = seekPrint(data,self.arg1Span)
        self.arg2 = seekPrint(data,self.arg2Span)
        return 1

    def printValue(self) : 
        ''' Prints the disourse relation with text and tree(s) in the arguments and connective '''
        returnString = ''
        returnString += 'ARG1 : ' + self.arg1 + '\n'
        returnString += '\n'.join(tree.printValue(tree.rootNode) for tree in self.arg1Trees)
        returnString += 'ARG2 : ' + self.arg2 + '\n'
        returnString += '\n'.join(tree.printValue(tree.rootNode) for tree in self.arg2Trees)
        returnString += 'CONN : ' + self.conn + '\n'
        returnString += '\n'.join(tree.printValue(tree.rootNode) for tree in self.connTrees)
        returnString += '\n-----------\n'
        return returnString


def seekPrint(data,pos) :
    ''' Given Text and PDTB-style offset format, extracts the desired text '''
    returnString=''
    posList=pos.split(';')
    delimiter = ''
    for posPart in posList :
            [posInit,posFinal]=posPart.split('..')
            returnString = returnString + delimiter + data[int(posInit):int(posFinal)]
            if len(posList) > 1 :
                    delimiter = '..'
    return returnString


def getPOSList(span) :
    ''' Given the PDTB-style offset format, extracts the different discontiguous offset mentions and returns a list of tuple(startPOS,endPOS) for each part ''' 
    POSList = []
    spanList = span.split(';')
    for spanPart in spanList :
        [startPOS ,endPOS] = spanPart.split('..')
        POSList.append((int(startPOS) , int(endPOS)))
    return POSList

def updateSenseIndex(index, conn , sense) :
    ''' Update a 2-level dictionary "index" for a particular sense and connective '''
    if conn not in index.keys() :
            index[conn] = {}
            index[conn][sense] = 1
    else :
            if sense not in index[conn].keys() :
                    index[conn][sense] = 1
            else :
                    index[conn][sense] += 1
    return index

def analyseRelation(relation,data) :
    ''' Checks the relation for particular characteristics such as adjacency, sentence difference etc. '''

    if relation.connSpan!='' :
        return isBetween(relation.connSpan , relation.arg1Span , relation.arg2Span) 

def processAnnFile( relationList , connTypeCounts , explicitConnDict, implicitConnDict , altlexConnDict, senseDict , connSenseIndex ,annFD,rawFD,type='full') :
    print("Processing annotation file:", annFD.name)
    ''' Given the annotation file and raw file descriptor, process the ann file and populate the discourse relations '''

#   connTypeCounts = {'Explicit':0 , 'Implicit':0 ,'AltLex':0 , 'EntRel':0 , 'NoRel':0}
#    connTypeCounts = [0,0,0,0,0]
#    senseDict = {}
#    explicitConnDict = {}
#    altlexConnDict = {}
#    implicitConnDict = {}
#    connSenseIndex = {}

    temp = rawFD.read()
#    relationList = []
    for line in annFD :
            fields=line.split('|')
            tempDR = discourseRelation(fields[0], fields[1],fields[14],fields[20] , fields[8])
            tempDR.fileName = rawFD.name

            if tempDR.sense == '' :
                    tempDR.sense = '_Without_sense'
                    
            if type=='full' : 

                connTypeCounts[tempDR.relationType] += 1
                senseDict[tempDR.sense] = senseDict.setdefault(tempDR.sense,0) + 1

                if tempDR.relationType=='Explicit' :
                        tempDR.conn = seekPrint(temp,tempDR.connSpan)
                        explicitConnDict[tempDR.conn] = explicitConnDict.setdefault(tempDR.conn,0) + 1
                        index = updateSenseIndex(connSenseIndex, tempDR.conn , tempDR.sense)

                elif tempDR.relationType=='AltLex' :
                        tempDR.conn = seekPrint(temp,tempDR.connSpan)
                        altlexConnDict[tempDR.conn] = altlexConnDict.setdefault(tempDR.conn , 0) + 1

                elif tempDR.relationType=='Implicit' :
                        tempDR.conn = fields[7]
                        implicitConnDict[tempDR.conn] = implicitConnDict.setdefault(tempDR.conn , 0 ) + 1

            relationList.append(tempDR)
    return [relationList, connTypeCounts, [explicitConnDict , implicitConnDict , altlexConnDict] , senseDict, connSenseIndex]

if __name__ == '__main__' :

    # Specify the input directory as first argument
    dataPath = sys.argv[1]
    annPath = os.path.join(sys.argv[1],'ann')
    rawPath = os.path.join(sys.argv[1],'raw')

    # Specify the outputFile-prefix as second argument
    outPath = sys.argv[2]
    outFile = outPath + '.statistics.txt'
    outRelationFile = outPath + '.relationList.txt'
    adjRelationFile = outPath + '.adjRelationList.txt'

    annFileDict = fw.fileListToFileNameDict(fw.folderWalk(annPath))
    rawFileDict = fw.fileListToFileNameDict(fw.folderWalk(rawPath))

    outFD=codecs.open(outFile,'w',encoding='utf-8')
    outRelationFD = codecs.open(outRelationFile,'w',encoding='utf-8')
    adjRelationFD = codecs.open(adjRelationFile,'w',encoding='utf-8')

    
    connTypeCounts = {'Explicit':0 , 'Implicit':0 ,'AltLex':0 , 'EntRel':0 , 'NoRel':0}
    senseDict = {}
    explicitConnDict = {}
    altlexConnDict = {}
    implicitConnDict = {}
    connSenseIndex = {}
    relationList=[]
    
    for inpFile in annFileDict.keys() :
        annFD = open(annFileDict[inpFile],'r')
        rawFD = codecs.open(rawFileDict[inpFile],'rb',encoding='utf-8')
        outRelationFD.write(annFD.name + '\n')
        [relationList , connTypeCounts, [explicitConnDict , implicitConnDict , altlexConnDict] , senseDict, connSenseIndex ] = processAnnFile( relationList , connTypeCounts , explicitConnDict, implicitConnDict , altlexConnDict, senseDict , connSenseIndex ,annFD , rawFD)
        annFD.close()

    # Producing the statistics File 

    outFD.write('Total Connective Frequency :\n')
    outFD.write( 'Explicit Connectives\t%d\nImplicit Connectives\t%d\nAltLex\t%d\nEntRel\t%d\nNoRel\t%d\n\n' % (connTypeCounts['Explicit'] , connTypeCounts['Implicit'] , connTypeCounts['AltLex'] , connTypeCounts['EntRel'] , connTypeCounts['NoRel']))
    outFD.write('Sense Frequency :\n')
    senseList = sorted(senseDict.items() , key=itemgetter(0))
    outFD.write('\n'.join(x[0] + '\t' + str(x[1]) for x in senseList) + '\n')
    outFD.write('\nExplicit Connective Frequency :\n')

    for conn in explicitConnDict.keys() :
            outFD.write(conn + '\t' + str(explicitConnDict[conn]) + '\n')
    outFD.write('\nAltLex Connective Frequency :\n')
    for conn in altlexConnDict.keys() :
            outFD.write(conn + '\t' + str(altlexConnDict[conn]) + '\n')
    outFD.write('\nImplicit Connective Frequency :\n')
    for conn in implicitConnDict.keys() :
            outFD.write(conn + '\t' + str(implicitConnDict[conn]) + '\n')

    # Producing the Connective-Sense Mapping Statistics File

    # connSenseFD = codecs.open(outPath + '.mappings.txt' , 'w' , encoding = 'utf-8')
    # connMappings = sorted(connSenseIndex.items() , key=itemgetter(1) , reverse=True)
    # for conn in connMappings :
    #         connective = conn[0]
    #         senses = sorted(conn[1].items() , key=itemgetter(0) , reverse=True)
    #         connSenseFD.write('Connective : ' + connective + '\n' + 'Types of Sense : ' + str(len(senses)) + '\n' + '\n'.join(('Sense : ' + x[0] + ' - ' + str(x[1])) for x in senses) + '\n\n')
    
