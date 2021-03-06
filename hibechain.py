#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from singlechain import SingleChain
from ips import IPList
import threading
import time
import gethnode

class HIBEChain():
    '''
    Data structure for a Hierarchical IBE Chain.
    ''' 
    #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    def __init__(self, IDList, threshList, IPlist, passwd='Blockchain17'):

        # Check if the input params are legal
        if not len(IDList) == len(threshList):
            raise ValueError("length of IDList should match length of threshList")
        if sum(nodeCount for (nodeCount, _) in threshList) > IPlist.getFullCount():
            raise ValueError("not enough IPs")

        self._chains = []
        self._IDList = IDList
        self._maxLevel = len(IDList[-1])
        self._ifSetNumber = False
        self._ifSetLevel = False
        self._ifSetID = False
        threadlist = []
        for index, name in enumerate(IDList):
            level = len(name)
            nodeCount, threshold = threshList[index][0], threshList[index][1]
            blockchainid = 120 + index
            tmp = SingleChain(name, level, nodeCount, threshold, blockchainid, IPlist, passwd)
            tmp.SinglechainStart()
            t = threading.Thread(target=tmp.constructChain,args=())
            t.start()
            self._chains.append(tmp)
        for t in threadlist:
            t.join()

    def constructHIBEChain(self):
        '''
        Construct the hierarchical construction of the HIBEChain.
        Connect blockchain nodes with their parent blockchain nodes.
        '''
        threadlist = []
        for chain in self._chains[::-1]:
            if chain.getID() != '':
                parentChain = self._chains[self._IDList.index(chain.getID()[:-1])]
                # print(chain.getID(), parentChain.getID())
                # parentChain.connectLowerChain(chain)
                t = threading.Thread(target=parentChain.connectLowerChain,args=(chain,))
                t.start()
        for t in threadlist:
            t.join()
    def destructHIBEChain(self):
        '''
        Stop all the nodes in the HIBEChain.
        '''
#        threadlist = []
#        for chain in self._chains:
#            t = threading.Thread(target=chain.destructChain,args=())
#            t.start()
#            threadlist.append(t)
#        for t in threadlist:
#            t.join()
        for chain in self._chains:
            chain.destructChain()

    def getChain(self, ID):
        '''
        Return a list of blockchain nodes with a given ID.
        '''
        try:
            index = self._IDList.index(ID)
            return self._chains[index]
        except ValueError:
            print("ID %s is not in the HIBEChain" % ID)

    def setNumber(self):
        '''
        set (n, t) value for all the chains in HIBEChain.
        '''
        threadlist = []
        for chain in self._chains:
            t = threading.Thread(target = chain.setNumber,args = ())
            t.start()
            threadlist.append(t)
            # chain.setNumber()
        for t in threadlist:
            t.join()
        self._ifSetNumber = True

    def setLevel(self):
        '''
        set level value for all the chains in HIBEChain.
        '''
        threadlist = []
        for chain in self._chains:
            # chain.setLevel(self._maxLevel)
            t = threading.Thread(target=chain.setLevel,args=(self._maxLevel,))
            t.start()
            threadlist.append(t)
        for t in threadlist:
            t.join()
        self._ifSetLevel = True

    def setID(self):
        '''
        set ID for all the chains in HIBEChain.
        '''
        if not self._ifSetNumber and self._ifSetLevel:
            raise RuntimeError("number and level info should be set previously")
        threadlist = []
        for chain in self._chains:
            t = threading.Thread(target=chain.setID,args=())
            t.start()
            threadlist.append(t)
        for t in threadlist:
            t.join()
        self._ifSetID = True


if __name__ == "__main__":
    IPlist = IPList('ip.txt')
    IDList = ["", "1", "11", "12", "13"]
    threshList = [(3, 2), (2, 1), (1, 1), (1,1), (1,1)]
    startTime = time.time()
    hibe = HIBEChain(IDList, threshList, IPlist)
    hibe.constructHIBEChain()
    hibe.setNumber()#门限
    hibe.setLevel()#层次
    hibe.setID()#id
    endTime = time.time()

    a, b, c, d = hibe.getChain(''), hibe.getChain('1'), hibe.getChain('11'), hibe.getChain("12")
    ap1 = a.getPrimer()
    bp1 = b.getPrimer()
    cp1 = c.getPrimer()
    dp1 = d.getPrimer()
    print(ap1.getPeerCount(), bp1.getPeerCount(), cp1.getPeerCount(), dp1.getPeerCount()) # 4 7 2 2

    a1 = cp1.newAccount()
    a2 = dp1.newAccount()
    cp1.unlockAccount(a1)
    dp1.unlockAccount(a2)

    time.sleep(2)
    hibe.destructHIBEChain()
    print("HIBEChain construction time:", endTime - startTime)
