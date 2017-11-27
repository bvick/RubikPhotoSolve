'''

Created on Oct 29, 2017

@author: Bob Vick

Solves Rubik's Cube using Lars Petrus method
Steps are found at http://lar5.com/cube/index.html 
Also took Bernard Helmstetter's solutions to final layer.  
See http://www.ai.univ-paris8.fr/~bh/cube


'''

import numpy as np 
import copy
from Rcube import  *
from drawRcube import *
import re
from util import *
import pickle
from HelmstetterSolver import *

#Match move corner to match edge in upper front right  
def step1pairCE(cube):
    ef=cube.facetAtLoc[(0,7)]
    cf= Rcube.home2facet(tuple((Rcube.facetSide(ef),(Rcube.facetPos(ef)-1)%8)))
    floc = cube.facetLoc[cf]
    fnum = floc[0]*9+floc[1]
    moves=step1pairCEmoves[fnum]
    cube.rotateSides(moves)
    cfHomeAdr=Rcube.facet2adr(cf)
    efHomeAdr=Rcube.facet2adr(ef)
    return(cfHomeAdr,efHomeAdr)

step1pairCEmoves={
    0: [(4,3),(3,3),(2,3)],
    2: [(1,2),(4,2),(1,2,3)],
    4:[(3,3),(5,3),(2,1)],
    6:[],
    9:[(4,2),(3,3),(2,3)],
    11:[(4,1),(0,2),(4,2),(0,2,3)],
    13:[(2,3),(0,1),(1,2),(0,3,3)],
    15:[(2,1)],
    18:[(2,3),(0,3),(3,1),(0,1,3)],
    20:[(2,2),(0,3),(3,1),(0,1,3)],
    22:[(3,3),(2,2)],
    24: [(0,3),(3,1),(0,1,3)],
    27: [(3,2),(2,3)],
    29:[(3,1),(2,3)],
    31: [(2,3)],
    33:[(3,3),(2,3)],
    36: [(0,1),(1,1),(0,3,3)],
    38: [(4,3),(0,1),(1,1),(0,3,3)],
    40: [(4,2),(5,1),(2,1)],
    42: [(4,1),(5,1),(2,1)],
    45: [(0,2),(4,2),(0,2,3)],
    47: [(0,1),(1,2),(0,3,3)],
    49: [(2,2)],
    51: [(0,3),(3,2),(0,1,3)]
    }


def finish221(cube,cfHomeAdr,doneEfHomeAdr):
    turns=len(cube.turns)
    if cube.printRot: print("\nworking 221")
    tarSide,defPos = Rcube.adr2spos(doneEfHomeAdr)
    
    tarEfPos=(defPos-2) %8
    tarEfHomeAdr=Rcube.spos2adr((tarSide,tarEfPos))
    tarEfCurAdr=cube.homeAdr2cur(tarEfHomeAdr)
    #cxyz=Rcube.joinSide(tarSide,[0,0])
    #print("cxyz",cxyz)
    centerHomeAdr=Rcube.joinSide(tarSide,[0,0])
    centerCurAdr=cube.homeAdr2cur(centerHomeAdr)
    toSide = Rcube.adrSide(centerCurAdr)
    curSide,curPos= Rcube.adr2spos(tarEfCurAdr)
    moveRules=[
        [
            [[1,1],[9,5],[1,3]], #0 0 
            [[1,1],[9,1],[4,1],[2,3],[1,2],[5,3],[22,1]], #0 1
            [[1,1],[9,3],[3,3],[1,1],[2,1],[1,3],[23,1]], # 0 2
            [[1,1],[9,1],[4,3],[2,3],[5,1],[24,1],[20,2]], #0 3 
            [[1,1],[9,3],[3,1],[4,1],[1,2],[21,1]], #0 4
            [[1,1],[9,1],[4,2],[1,1],[22,2],[20,2]] #0 5
        ],[
            [[0,3],[9,1],[4,3],[2,1],[0,1],[2,3],[20,1]], # 1 0
            [[0,3],[9,3],[2,3],[22,1],[20,1]], # 1 1
            [[0,3],[9,7], [5,1],[0,1],[1,1],[23,1]], # 1 2
            [[0,3],[9,7],[5,2],[2,1],[24,1],[20,1]], # 1 3
            [[0,3],[9,7], [5,3],[0,3],[3,1],[21,1],[20,2]], # 1 4 
            [[0,3],[9,1],[4,1],[5,1],[2,2],[22,2],[20,1]]  # 1 5
        ], [
            [[0,1],[9,5],[3,1],[4,1],[0,2],[4,3],[25,1]], # 2 0 
            [[0,1],[9,7],[5,3],[4,1],[22,1],[25,1]], # 2 1
            [[0,1],[9,7],[0,3],[1,1],[23,1]],# 2,2 
            [[0,1],[9,7],[5,1],[3,2],[4,3],[24,1],[25,1]], # 2 3
            [[0,1],[9,7],[5,2],[0,1],[3,1],[21,1],[20,2]], # 2 4
            [[0,1],[9,5],[3,3],[4,2],[24,2],[25,1]] # 2 5
        ],[
            [[9,7],[4,1],[1,1],[0,2],[1,3]], # 3 0
            [[9,7],[4,2],[0,3],[1,1],[2,3],[22,1],[20,1]], # 3 1
            [[9,1],[5,3],[1,1],[23,1]], # 3 2
            [[9,1],[0,3],[2,1],[24,1],[20,1]],  # 3 3
            [[9,1],[5,1],[4,2],[1,3],[21,1]], # 3 4
            [[9,7],[4,3],[1,2],[21,2]] # 3 5
        ],[
            [[9,3],[3,3],[1,1],[0,1],[1,3]], # 4 0
            [[9,1],[5,1],[0,3],[1,2],[2,3],[22,1],[20,1]], # 4 1
            [[9,1],[5,2],[1,1],[23,1]], # 4 2
            [[9,1],[5,3],[0,3],[2,1],[24,1],[20,1]], # 4 3
            [[9,5],[1,3],[21,1]], # 4 4
            [[9,3],[3,1],[0,1],[4,2],[22,2],[25,1]] # 4 5
        ],[
            [[9,7],[4,2],[1,1],[0,2],[1,3]], # 5 0
            [[9,7],[4,3],[0,3],[1,1],[2,3],[22,1],[20,1]], # 5 1
            [[9,5],[3,1],[1,3],[2,1],[1,2],[23,1]], # 5 2
            [[9,7],[4,1],[3,1],[0,3],[2,1],[24,1],[20,1]], # 5 3
            [[9,5],[3,3],[4,1],[1,3],[21,1]],# 5 4
            [[9,7],[1,2],[21,2]] # 5 5
        ]
    ] 
    if cube.printRot: print("tarSide",tarSide,"curPos",curPos,"curSide, toSide",curSide,toSide)
    rule=moveRules[curSide][toSide]
    if cube.printRot: print("rule",rule)
    if curSide==2 and curPos==3:
        rule=[[1,3],[2,1],[1,1]]+rule
        curPos = 5
    for move in rule:
        #print("working move",move[0],move[1])
        if move[0] >=20: # whole cube reorient
            cube.rotateSide(move[0]-20,move[1],3)
        elif move[0] == 9: # reposition curSide
            cube.rotateSide(curSide,((move[1]-curPos)//2)%4)
        else:
            cube.rotateSide(move[0],move[1])
    return(curSide,toSide,cfHomeAdr)
  
def solveThis222(cube,cfHomeAdr):
    if cube.printRot: print("\nworking 222 *******************************", cfHomeAdr)
    side0,side1,side2,facet1,facet2=Rcube.cornerSidesPlus(cfHomeAdr)
    if cube.printRot: print("sides +",side0,side1,side2,facet1,facet2)
    # move target sides to front and right and 221 to back corner
    reor=cube.sideAdr(side2)-1
    if cube.printRot: print("center2",side2,reor)
    cube.rotateSide(0,reor,3)
    cube.rotateSide(0,2-reor)

    # move completion edge between centers
    f1cur=cube.homeAdr2cur(facet1)
    f2cur=cube.homeAdr2cur(facet2)
    f1side,f1pos=Rcube.adr2spos(f1cur)
    f2side,f2pos=Rcube.adr2spos(f2cur)
    if cube.printRot: print("f1",f1side,f1pos,f2side,f2pos)
    if f2side==1:
        cube.rotateSide(1,(5-f2pos)//2)
        cube.rotateSide(0,2)
        return(f1side,f2side)
    elif f1side==2:
        cube.rotateSide(2,(1-f1pos)//2)
        cube.rotateSide(0,2)
        return(f1side,f2side)
    else:
        if (f2side==0):
            if f2pos==5:
                cube.rotateSide(2,-1)
            else:
                cube.rotateSide(1,2)
                cube.rotateSide(5,1)
                cube.rotateSide(2,1)
            cube.rotateSide(0,2)
            return(f1side,f2side)
        if (f2side==5):
            cube.rotateSide(5,(3-f2pos)//2)
            cube.rotateSide(2,1)
            cube.rotateSide(0,2)
            return(f1side,f2side)
        # in all other cases, move f1 to bottom
        if (f2side==2):
            cube.rotateSide(2,(7-f2pos)//2)
        elif (f2side==0):
            cube.rotateSide(1,2)
        else:
            cube.rotateSide(0,2)
            cube.rotateSide(f2side,(1-f2pos)//2)
            cube.rotateSide(0,2)
        _,f1posn=Rcube.adr2spos(cube.homeAdr2cur(facet1))
        cube.rotateSide(5,(1-f1posn)//2)
        cube.rotateSide(1,3)
        cube.rotateSide(0,2)
        return(f1side,f2side)

# try several different orientations, use the one with the fewest moves
def solve222(cube):
    aTopFace=[(0,0,3),(1,1,3),(1,2,3),(1,3,3),(2,1,3),(2,3,3)]
    aRot = [(0,0,3),(0,1,3),(0,2,3),(0,3,3)]
    bestTC=999
    for frot in aTopFace:
        for rot in aRot:
            thisOri=[frot,rot]
            thisCube=Rcube(cube.facetLoc)
            thisCube.rotateSides(thisOri)
            cfHome,efHome=step1pairCE(thisCube)
            curSide,toSide,cfHome=finish221(thisCube,cfHome,efHome)
            f1,f2=solveThis222(thisCube,cfHome)
            thisTC = len(thisCube.redTurns)
#             printvars("frot","rot","thisTC")
            if thisTC<bestTC:
                bestTC=thisTC
                bestCube=thisCube
    cube.rotateSides(bestCube.turns)
    cube.phase.append(len(cube.redTurns))
    return(len(cube.redTurns))

def solveThis223(cube):
    turnCount=len(cube.redTurns)
    if cube.printRot: print("working 223 ***********************")
    cube.rotateSide(1,2,3)
    cube.rotateSide(0,1,3)
    
    # 222 in back left bottom corner
    # steps: pair corner with edge
    # pair other edge with center
    # pair pairs
    # rotate into place
    cfacet=cube.side3facet(0,3,4)
    efacet=cube.side2facet(0,4)
    eCurSide,eCurPos=cube.facetLoc[efacet]
    eofacet=cube.side2facet(4,0)
    eoCurSide,eoCurPos=cube.facetLoc[eofacet]
    if cube.printRot: print("eo",eCurSide,eCurPos,eoCurSide,eoCurPos)
    
    # move efacet to place
    if eoCurSide==0:
        cube.rotateSide(0,(5-eoCurPos)//2)
        cube.rotateSide(2,3)
        cube.rotateSide(1,3)
        cube.rotateSide(0,2)
    elif eoCurSide in [1,2]:
        cube.rotateSide(eoCurSide,(3-eoCurPos)//2)
    elif eCurSide == 1:
        cube.rotateSide(1,(5-eCurPos)//2)
        cube.rotateSide(2,1)
    elif eCurSide==2:
        cube.rotateSide(2,(1-eCurPos)//2)
        cube.rotateSide(1,3)
        cube.rotateSide(0,2)
    # now must be on top
    eCurSide,eCurPos=cube.facetLoc[efacet]
    if (eCurSide!=0):
        print('should have been 0',eCurSide,eCurPos)
        return(len(cube.redTurns)-turnCount)
    cube.rotateSide(0,(3-eCurPos)//2)
    
    # pair corner with eside
    cCurSide,cCurPos=cube.facetLoc[cfacet]
    if cube.printRot: print("placing corner",cCurSide,cCurPos)
    def do1(cCurPos):
        cube.rotateSides([[1,(4-cCurPos)//2],[2,1]])
    if cCurSide==1:
        do1(cCurPos)
    elif cCurSide==0:
        if cCurPos in [0,2]:
            cube.rotateSide(4,1)
            do1(cCurPos)
            cube.rotateSide(4,3)
        elif cCurPos==6:
            cube.rotateSides([[1,1],[0,1],[1,3],[0,3]])
    elif cCurSide==2:
        cube.rotateSides([[2,(-cCurPos)//2],[0,1],[1,3],[0,3]])
    elif cCurSide==3:
        if cCurPos==6:
            cube.rotateSides([[0,3],[1,2],[0,2],[1,3],[0,3]])
        elif cCurPos==2:
            cube.rotateSide(2,3)
        else: # cCurPos==4
            cube.rotateSide(2,2)
            do1(6)
    elif cCurSide==5:
        if cCurPos==4:
            cube.rotateSide(2,1)
            do1(6)
        else:
            cube.rotateSides([[5,(2-cCurPos)//2],[2,2],[5,(cCurPos-2)//2]])
    else:   # cCurSide==4
        if cCurPos in [0,6]:
            if cube.printRot: print("46")
            cube.rotateSides([[1,3],[5,-cCurPos//2],[2,2],[5,cCurPos//2],])
        else: # cCurPos==4
            cube.rotateSides([[0,3],[1,2],[0,1],[1,3],[2,1]])
            
    # now pair other edge with top center
    
    efacet=cube.side2facet(0,3)
    eCurSide,eCurPos=cube.facetLoc[efacet]
    if eCurSide==1:
        cube.rotateSide(1,(7-eCurPos)//2)
    elif eCurSide==4 and eCurPos==7:
        cube.rotateSide(1,2)
    cube.rotateSides([[0,2],[1,3]]) # corner now lfd
    efacet=cube.side2facet(0,3)
    eCurSide,eCurPos=cube.facetLoc[efacet]
    if cube.printRot: print("last edge",eCurSide,eCurPos)
    if eCurSide==0:
        cube.rotateSides([[0,(1-eCurPos)//2],[1,1],[0,1]])
    elif eCurSide==1:
        cube.rotateSides([[2,1],[0,2],[1,1],[0,1]]) 
    elif eCurSide==2:
        cube.rotateSides([[2,(5-eCurPos)//2],[3,1],[0,3],[3,3],[1,1],[0,1]])
    elif eCurSide==3:
        cube.rotateSides([[3,(3-eCurPos)//2],[2,3],[3,(eCurPos-3)//2],[0,2],[1,1],[0,1]])
    elif eCurSide==4:
        if eCurPos==7:
            cube.rotateSides([[1,1],[0,(1-eCurPos)//2],[1,1],[0,1]])
        else:
            cube.rotateSides([[0,1],[3,3],[2,3],[3,1],[0,2],[1,1],[0,1]])
    elif eCurSide==5:
        cube.rotateSides([[2,2],[0,2],[1,1],[0,1]])
    return(len(cube.redTurns)-turnCount)

# find best 2x2x3 solution, trying all the 2x2x2 orientations
def solve223(cube):
    rots=[[],[(0,1,3),(1,1,3)],[(4,1,3),(3,1,3)]]
    bestTurns=999
#     drawRubik(cube,"into 223")
    for rot in rots:
        thisCube=cube.copy()
        thisCube.rotateSides(rot)
#         drawRubik(thisCube,rot)
        turnCount=solveThis223(thisCube)
        if turnCount<bestTurns:
            bestCube=thisCube
            bestTurns=turnCount
#     drawRubik(bestCube,"best 223")
    bestCube.phase.append(len(bestCube.redTurns))
    return(bestCube,turnCount)

# fixes twisting of remaining edges.  If we're using Helmstetter's full solution,
# we only need to fix the edges not on the final side
def fixTwisted(cube,debug=False,fullHelm=True):
    turnCount=len(cube.redTurns)
    cube.rotateSide(1,3,3)
    if debug: drawRubik(cube,"fixTwisted start")
    at0=Rcube.attachedEdgeLocs(0)
    at1=Rcube.attachedEdgeLocs(1)
    side0=cube.sideAtSide(0)
    side1=cube.sideAtSide(1)
    posRot=[Rcube.posRot0[side0][side1],Rcube.posRot1[side0][side1]]
    #print("twist sides",side0,side1,posRot)
    unfinished=True
    totalFound=0
    n=0
    firstBad=True
    while unfinished:
        n+=1
        found=False
        for p in [1,5,7,3]:
            pos=(p-posRot[1])%8
            spos=cube.sposOfSpos((side1,pos))
            if debug: drawRubik(cube,printvars("p","pos","spos",label="front",out=False))
            if fullHelm and (p==3) and firstBad: continue
            if spos[0]==1 or spos in at0 : continue
            #print("bad  [1,",p,"] = [",side1,",", pos,"] at ", spos,(spos[0],spos[1]) in at1)
            if spos in at1:
                xspos=Rcube.edgeOtherLoc(spos)
                if firstBad:
                    cube.rotateSides([[1,(3-xspos[1])//2],[0,2]])
                    totalFound+=1
                    found=True
                    firstBad=False
                else:
                    cube.rotateSide(1,(1-xspos[1])//2)
                    cube.rotateSides([[4,3],[0,3],[4,1]])
                    totalFound+=1
                    found=True
                    firstBad=True
            else: # must be on side0
                if firstBad:
                    cube.rotateSide(0,(3-spos[1])//2)
                    totalFound+=1
                    found=True
                    firstBad=False
                else:
                    cube.rotateSides([[0,(7-spos[1])//2],[1,3],[0,(spos[1]-7)//2]])
                    cube.rotateSides([[4,3],[0,3],[4,1]])
                    totalFound+=1
                    found=True
                    firstBad=True
        # for fullHelm, we are either done or we still have one bad one in place
        if (not firstBad) or not fullHelm:
            for p in [1,3,5,7]:
                pos=(p-posRot[0])%8
                spos=cube.sposOfSpos((side0,pos))
                if debug: drawRubik(cube,printvars("p","pos","spos",label="top",out=False))
                if spos[0]==0 or spos in at1: continue
                #print("bad  [0,",p,"] = [",side0,",", pos,"] at ", spos,(spos[0],spos[1]) in at1)
                if spos in at0:
                    xspos=Rcube.edgeOtherLoc(spos)
                    if firstBad:
                        cube.rotateSide(0,(3-xspos[1])//2)
                        totalFound+=1
                        found=True
                        firstBad=False
                    else:
                        cube.rotateSides([[0,(7-xspos[1])//2],[1,3],[0,(xspos[1]-7)//2]])
                        cube.rotateSides([[4,3],[0,3],[4,1]])
                        totalFound+=1
                        found=True
                        firstBad=True
                else: # must be on side1
                    if firstBad:
                        cube.rotateSides([[1,(3-spos[1])//2],[0,2]])
                        totalFound+=1
                        found=True
                        firstBad=False
                    else:
                        cube.rotateSide(1,(1-spos[1])//2)
                        cube.rotateSides([[4,3],[0,3],[4,1]])
                        totalFound+=1
                        found=True
                        firstBad=True
                if firstBad and fullHelm: break
            if firstBad and fullHelm: break
        if firstBad and fullHelm: break
        if not found:
            unfinished=False
        if n>4: unfinished=False
    if debug: drawRubik(cube,"done twist")
    return(len(cube.redTurns)-turnCount)

doubleLaCE =  [[[(1, 4, 1, 5)], [(5, 2, 2, 3), (4, 0, 2, 3), (0, 0, 2, 3)], [(5, 2, 1, 3), (5, 2, 4, 5), (5, 2, 3, 5), (4, 0, 1, 3), (
4, 0, 4, 5), (4, 0, 3, 5), (0, 2, 1, 3), (0, 4, 4, 5), (0, 6, 3, 5)], [(4, 0, 1, 5), (0, 0, 1, 7), (2, 2, 1, 1), (0, 0,
4, 5), (2, 2, 4, 5), (0, 0, 3, 5), (2, 2, 3, 5), (0, 0, 1, 5), (2, 2, 1, 7), (5, 2, 1, 1), (0, 2, 1, 5), (0, 2, 1, 7), (
0, 2, 1, 1), (2, 0, 3, 5), (5, 0, 3, 5), (4, 6, 3, 5)], [(1, 2, 1, 1), (4, 4, 1, 1), (3, 4, 1, 1), (0, 2, 3, 5), (0, 4,
2, 3), (0, 6, 1, 3), (1, 2, 3, 5), (4, 4, 2, 3), (3, 4, 1, 3), (0, 2, 2, 3), (0, 4, 1, 3), (0, 6, 4, 5), (1, 2, 2, 3), (
4, 4, 1, 3), (3, 4, 4, 5), (0, 4, 1, 5), (0, 6, 1, 5), (1, 2, 1, 7), (4, 4, 1, 7), (3, 4, 1, 7), (0, 4, 1, 1), (0, 6, 1,
1), (0, 0, 1, 1), (2, 0, 2, 3), (2, 0, 1, 3), (2, 0, 4, 5)], [(1, 4, 1, 3), (1, 6, 1, 5), (1, 0, 1, 7), (4, 4, 1, 5), (3
, 4, 1, 5), (1, 4, 2, 3), (1, 6, 2, 3), (1, 0, 2, 3), (2, 0, 1, 7), (5, 0, 1, 1), (4, 6, 1, 3), (2, 2, 1, 3), (5, 2, 1,
5), (4, 0, 1, 7)], [(3, 6, 4, 5), (2, 4, 3, 5)]], [[(2, 2, 2, 3)], [(4, 6, 1, 5), (3, 6, 1, 5), (2, 4, 1, 5)], [(0, 6, 1
, 7), (2, 0, 1, 1), (5, 0, 1, 3), (3, 6, 1, 7), (3, 6, 1, 1), (3, 6, 1, 3), (2, 4, 1, 7), (2, 4, 1, 1), (2, 4, 1, 3)], [
(0, 4, 1, 7), (5, 0, 4, 5), (5, 0, 2, 3), (1, 4, 1, 7), (4, 6, 1, 7), (1, 4, 1, 1), (4, 6, 1, 1), (2, 4, 4, 5), (1, 4, 3
, 5), (4, 6, 2, 3), (1, 4, 4, 5), (3, 6, 2, 3)], [(4, 6, 4, 5), (0, 6, 2, 3), (1, 6, 1, 1), (1, 0, 1, 3), (1, 2, 1, 5),
(5, 0, 1, 5), (1, 6, 1, 3), (1, 0, 1, 5), (2, 0, 1, 5), (5, 0, 1, 7), (1, 6, 3, 5), (1, 0, 3, 5), (1, 6, 4, 5), (1, 0, 4
, 5), (1, 2, 4, 5)], [(3, 6, 3, 5), (2, 4, 2, 3), (0, 0, 1, 3), (0, 2, 4, 5), (0, 4, 3, 5), (2, 2, 1, 5), (4, 4, 3, 5),
(3, 4, 2, 3)], [(5, 2, 1, 7), (4, 0, 1, 1)]]]

doubleLaMoves=[[[[]], [[(1, 3)], [(1, 2)], [(1, 1)]], [[(0, 3), (1, 3)], [(0, 2), (1, 3)], [(0, 1), (1, 3)], [(0, 3), (1, 2)], [(0, 2)
, (1, 2)], [(0, 1), (1, 2)], [(0, 3), (1, 1)], [(0, 2), (1, 1)], [(0, 1), (1, 1)]], [[(1, 3), (0, 3), (1, 3)], [(1, 2),
(0, 3), (1, 3)], [(1, 1), (0, 3), (1, 3)], [(1, 2), (0, 2), (1, 3)], [(1, 1), (0, 2), (1, 3)], [(1, 2), (0, 1), (1, 3)],
[(1, 1), (0, 1), (1, 3)], [(1, 3), (0, 3), (1, 2)], [(1, 2), (0, 3), (1, 2)], [(1, 1), (0, 3), (1, 2)], [(1, 3), (0, 3),
(1, 1)], [(1, 2), (0, 3), (1, 1)], [(1, 1), (0, 3), (1, 1)], [(1, 3), (0, 1), (1, 1)], [(1, 2), (0, 1), (1, 1)], [(1, 1)
, (0, 1), (1, 1)]], [[(0, 3), (1, 1), (0, 3), (1, 3)], [(0, 2), (1, 1), (0, 3), (1, 3)], [(0, 1), (1, 1), (0, 3), (1, 3)
], [(0, 3), (1, 2), (0, 2), (1, 3)], [(0, 2), (1, 2), (0, 2), (1, 3)], [(0, 1), (1, 2), (0, 2), (1, 3)], [(0, 3), (1, 1)
, (0, 2), (1, 3)], [(0, 2), (1, 1), (0, 2), (1, 3)], [(0, 1), (1, 1), (0, 2), (1, 3)], [(0, 3), (1, 2), (0, 1), (1, 3)],
[(0, 2), (1, 2), (0, 1), (1, 3)], [(0, 1), (1, 2), (0, 1), (1, 3)], [(0, 3), (1, 1), (0, 1), (1, 3)], [(0, 2), (1, 1), (
0, 1), (1, 3)], [(0, 1), (1, 1), (0, 1), (1, 3)], [(0, 2), (1, 3), (0, 3), (1, 2)], [(0, 1), (1, 3), (0, 3), (1, 2)], [(
0, 3), (1, 2), (0, 3), (1, 2)], [(0, 2), (1, 2), (0, 3), (1, 2)], [(0, 1), (1, 2), (0, 3), (1, 2)], [(0, 3), (1, 1), (0,
3), (1, 1)], [(0, 2), (1, 1), (0, 3), (1, 1)], [(0, 1), (1, 1), (0, 3), (1, 1)], [(0, 3), (1, 3), (0, 1), (1, 1)], [(0,
2), (1, 3), (0, 1), (1, 1)], [(0, 1), (1, 3), (0, 1), (1, 1)]], [[(1, 3), (0, 3), (1, 1), (0, 3), (1, 3)], [(1, 2), (0,
3), (1, 1), (0, 3), (1, 3)], [(1, 1), (0, 3), (1, 1), (0, 3), (1, 3)], [(1, 2), (0, 2), (1, 1), (0, 3), (1, 3)], [(1, 2)
, (0, 1), (1, 1), (0, 3), (1, 3)], [(1, 3), (0, 3), (1, 1), (0, 1), (1, 3)], [(1, 2), (0, 3), (1, 1), (0, 1), (1, 3)], [
(1, 1), (0, 3), (1, 1), (0, 1), (1, 3)], [(1, 3), (0, 1), (1, 3), (0, 3), (1, 2)], [(1, 2), (0, 1), (1, 3), (0, 3), (1,
2)], [(1, 1), (0, 1), (1, 3), (0, 3), (1, 2)], [(1, 3), (0, 1), (1, 1), (0, 3), (1, 1)], [(1, 2), (0, 1), (1, 1), (0, 3)
, (1, 1)], [(1, 1), (0, 1), (1, 1), (0, 3), (1, 1)]], [[(0, 2), (1, 3), (0, 3), (1, 1), (0, 1), (1, 3)], [(0, 1), (1, 3)
, (0, 3), (1, 1), (0, 1), (1, 3)]]], [[[]], [[(0, 3)], [(0, 2)], [(0, 1)]], [[(1, 3), (0, 3)], [(1, 2), (0, 3)], [(1, 1)
, (0, 3)], [(1, 3), (0, 2)], [(1, 2), (0, 2)], [(1, 1), (0, 2)], [(1, 3), (0, 1)], [(1, 2), (0, 1)], [(1, 1), (0, 1)]],
[[(0, 1), (1, 3), (0, 3)], [(0, 3), (1, 1), (0, 3)], [(0, 1), (1, 1), (0, 3)], [(0, 2), (1, 3), (0, 2)], [(0, 1), (1, 3)
, (0, 2)], [(0, 2), (1, 2), (0, 2)], [(0, 1), (1, 2), (0, 2)], [(0, 3), (1, 1), (0, 2)], [(0, 2), (1, 1), (0, 2)], [(0,
1), (1, 1), (0, 2)], [(0, 3), (1, 1), (0, 1)], [(0, 1), (1, 1), (0, 1)]], [[(1, 3), (0, 3), (1, 1), (0, 3)], [(1, 2), (0
, 1), (1, 1), (0, 3)], [(1, 3), (0, 2), (1, 3), (0, 2)], [(1, 2), (0, 2), (1, 3), (0, 2)], [(1, 1), (0, 2), (1, 3), (0,
2)], [(1, 1), (0, 1), (1, 3), (0, 2)], [(1, 3), (0, 2), (1, 2), (0, 2)], [(1, 2), (0, 2), (1, 2), (0, 2)], [(1, 2), (0,
1), (1, 2), (0, 2)], [(1, 1), (0, 1), (1, 2), (0, 2)], [(1, 3), (0, 2), (1, 1), (0, 2)], [(1, 2), (0, 2), (1, 1), (0, 2)
], [(1, 3), (0, 3), (1, 1), (0, 1)], [(1, 2), (0, 3), (1, 1), (0, 1)], [(1, 1), (0, 3), (1, 1), (0, 1)]], [[(0, 3), (1,
3), (0, 3), (1, 1), (0, 3)], [(0, 2), (1, 3), (0, 3), (1, 1), (0, 3)], [(0, 3), (1, 2), (0, 1), (1, 1), (0, 3)], [(0, 2)
, (1, 2), (0, 1), (1, 1), (0, 3)], [(0, 1), (1, 2), (0, 1), (1, 1), (0, 3)], [(0, 1), (1, 1), (0, 2), (1, 3), (0, 2)], [
(0, 3), (1, 1), (0, 3), (1, 1), (0, 1)], [(0, 2), (1, 1), (0, 3), (1, 1), (0, 1)]], [[(1, 2), (0, 3), (1, 2), (0, 1), (1
, 1), (0, 3)], [(1, 1), (0, 3), (1, 2), (0, 1), (1, 1), (0, 3)]]]]


# first part of Lar's step 4a , creating L-shaped solution
def doubleLa1(cube):
    cHome=cube.side3facet(1,5,4)
    eHome=cube.side2facet(1,4)
    cloc=tuple(cube.facetLoc[cHome])
    eloc=tuple(cube.facetLoc[eHome])
    if eloc[0]==cloc[0] and (((eloc[1]-cloc[1])%8)==1): return(True)
    ce = cloc+eloc
    for sce,smv in zip(doubleLaCE,doubleLaMoves):
        for mce, mmv in zip(sce,smv):
            if ce in mce:
                mv = mmv[mce.index(ce)]
                cube.rotateSides(mv)
                return(True)
    print("doubleLa1 ce not found!!!",ce)        
    printvars("cHome","eHome","cloc","eloc")
    return(False)

# second part of Lar's step 4a , creating L-shaped solution
def doubleLa2(cube):
    cHome=cube.side3facet(1,5,4)
    eHome=cube.side2facet(1,5)      
    cloc=cube.facetLoc[cHome]
    eloc=cube.facetLoc[eHome]
#     printvars("cHome","eHome","cloc",'eloc')
#     drawRubik(cube,"d2")
    if cloc[0]!=1:
        toploc=Rcube.cornerSideLoc(cloc,0)
        cube.rotatePos(0,toploc[1],6)
        cloc=cube.facetLoc[cHome]
        eloc=cube.facetLoc[eHome]
        #print("eloc",eloc)
        if eloc[0]==1:
            if eloc[1]!=3:
                cube.rotateSides([[0,3],[1,(1-eloc[1])//2],[0,2],[1,3]])
            else:
                cube.rotateSides([[0,1],[1,3],[0,3],[1,1],[0,1],[1,2],[0,3],[1,3]])
        else:
            toploc=Rcube.edgeOtherLoc(eloc)
            cube.rotateSides([[0,(7-toploc[1])//2],[1,3],[0,(toploc[1]-5)//2],[1,3]])
    else:
        cube.rotatePos(1,cloc[1],4)
        eloc=cube.facetLoc[eHome]
        #print("cloc on 1, eloc=",eloc)        
        if eloc[0]==1:
            cube.rotateSides([[1,3],[0,1],[1,(3-eloc[1])//2],[0,3],[1,3]])
        else:
            toploc=Rcube.edgeOtherLoc(eloc)
            cube.rotateSides([[1,1],[0,(7-toploc[1])//2],[1,2],[0,1],[1,1],[0,3],[1,3]])
    return()                        
  
s4bCE=[(1, 6, 1, 5), (0, 6, 4, 5), (3, 6, 3, 5), (2, 4, 2, 3), (0, 0, 3, 5), (0, 2, 2, 3), (0, 4, 1, 3), (1, 4, 1, 3), (4, 6,
4, 5), (0, 6, 2, 3), (0, 2, 3, 5), (2, 2, 1, 5), (4, 4, 4, 5), (4, 4, 1, 5), (0, 0, 2, 3), (0, 0, 1, 5), (0, 0, 4, 5), (
0, 4, 1, 5), (2, 0, 4, 5), (2, 2, 3, 5), (2, 0, 1, 3), (2, 2, 1, 3), (0, 2, 1, 3), (4, 4, 1, 3), (3, 4, 1, 3), (5, 2, 1,
3), (4, 6, 3, 5), (4, 6, 2, 3), (4, 6, 1, 5), (0, 0, 1, 3), (0, 2, 4, 5), (0, 4, 3, 5), (0, 4, 2, 3), (0, 6, 1, 3), (1,
2, 1, 5), (3, 4, 1, 5), (3, 4, 3, 5), (2, 2, 2, 3), (1, 2, 1, 3), (0, 4, 4, 5), (0, 6, 3, 5), (0, 2, 1, 5), (0, 6, 1, 5)
, (2, 0, 3, 5), (2, 0, 2, 3), (1, 2, 2, 3), (3, 4, 4, 5), (1, 2, 4, 5), (4, 4, 3, 5), (3, 4, 2, 3), (2, 2, 4, 5), (1, 2,
3, 5), (4, 4, 2, 3), (5, 2, 4, 5), (5, 2, 3, 5), (5, 2, 2, 3), (3, 6, 2, 3), (2, 4, 1, 3), (1, 4, 4, 5), (3, 6, 1, 3), (
2, 4, 4, 5), (1, 4, 3, 5), (3, 6, 1, 5), (2, 4, 1, 5), (1, 4, 1, 5), (1, 6, 3, 5), (1, 6, 2, 3), (1, 6, 1, 3), (4, 6, 1,
3), (2, 0, 1, 5), (1, 4, 2, 3), (1, 6, 4, 5), (5, 2, 1, 5), (3, 6, 4, 5), (2, 4, 3, 5)]

s4bMoves=  [[], [(1, 3), (0, 3), (1, 1)], [(1, 3), (0, 2), (1, 1)], [(1, 3), (0, 1), (1, 1)], [(0, 3), (1, 3), (0, 3), (1, 1)], [(0
, 2), (1, 3), (0, 3), (1, 1)], [(0, 1), (1, 3), (0, 3), (1, 1)], [(0, 2), (1, 3), (0, 2), (1, 1)], [(0, 1), (1, 3), (0,
2), (1, 1)], [(1, 1), (0, 2), (1, 2), (0, 3), (1, 2), (0, 3), (1, 3)], [(1, 2), (0, 3), (1, 1), (0, 3), (1, 3), (0, 2),
(1, 2)], [(1, 2), (0, 3), (1, 2), (0, 3), (1, 2), (0, 2), (1, 2)], [(1, 2), (0, 2), (1, 1), (0, 1), (1, 3), (0, 1), (1,
2)], [(1, 2), (0, 2), (1, 2), (0, 1), (1, 2), (0, 1), (1, 2)], [(1, 3), (0, 3), (1, 1), (0, 3), (1, 3), (0, 3), (1, 1)],
[(1, 3), (0, 2), (1, 1), (0, 3), (1, 3), (0, 3), (1, 1)], [(1, 3), (0, 1), (1, 1), (0, 3), (1, 3), (0, 3), (1, 1)], [(1,
3), (0, 3), (1, 1), (0, 2), (1, 3), (0, 3), (1, 1)], [(1, 3), (0, 2), (1, 1), (0, 2), (1, 3), (0, 3), (1, 1)], [(1, 3),
(0, 1), (1, 1), (0, 2), (1, 3), (0, 3), (1, 1)], [(1, 3), (0, 3), (1, 1), (0, 1), (1, 3), (0, 3), (1, 1)], [(1, 3), (0,
2), (1, 1), (0, 1), (1, 3), (0, 3), (1, 1)], [(1, 3), (0, 1), (1, 1), (0, 1), (1, 3), (0, 3), (1, 1)], [(1, 3), (0, 3),
(1, 1), (0, 2), (1, 3), (0, 2), (1, 1)], [(1, 3), (0, 2), (1, 1), (0, 2), (1, 3), (0, 2), (1, 1)], [(1, 3), (0, 1), (1,
1), (0, 2), (1, 3), (0, 2), (1, 1)], [(1, 3), (0, 3), (1, 1), (0, 1), (1, 3), (0, 2), (1, 1)], [(1, 3), (0, 2), (1, 1),
(0, 1), (1, 3), (0, 2), (1, 1)], [(1, 3), (0, 1), (1, 1), (0, 1), (1, 3), (0, 2), (1, 1)], [(0, 3), (1, 1), (0, 2), (1,
2), (0, 3), (1, 2), (0, 3), (1, 3)], [(0, 2), (1, 1), (0, 2), (1, 2), (0, 3), (1, 2), (0, 3), (1, 3)], [(0, 1), (1, 1),
(0, 2), (1, 2), (0, 3), (1, 2), (0, 3), (1, 3)], [(0, 3), (1, 2), (0, 3), (1, 1), (0, 3), (1, 3), (0, 2), (1, 2)], [(0,
2), (1, 2), (0, 3), (1, 1), (0, 3), (1, 3), (0, 2), (1, 2)], [(0, 3), (1, 2), (0, 3), (1, 2), (0, 3), (1, 2), (0, 2), (1
, 2)], [(0, 1), (1, 2), (0, 3), (1, 2), (0, 3), (1, 2), (0, 2), (1, 2)], [(0, 3), (1, 2), (0, 2), (1, 1), (0, 1), (1, 3)
, (0, 1), (1, 2)], [(0, 2), (1, 2), (0, 2), (1, 1), (0, 1), (1, 3), (0, 1), (1, 2)], [(0, 1), (1, 2), (0, 2), (1, 1), (0
, 1), (1, 3), (0, 1), (1, 2)], [(0, 2), (1, 3), (0, 3), (1, 1), (0, 3), (1, 3), (0, 3), (1, 1)], [(0, 1), (1, 3), (0, 3)
, (1, 1), (0, 3), (1, 3), (0, 3), (1, 1)], [(0, 3), (1, 3), (0, 2), (1, 1), (0, 3), (1, 3), (0, 3), (1, 1)], [(0, 1), (1
, 3), (0, 2), (1, 1), (0, 3), (1, 3), (0, 3), (1, 1)], [(0, 3), (1, 3), (0, 2), (1, 1), (0, 2), (1, 3), (0, 3), (1, 1)],
[(0, 2), (1, 3), (0, 2), (1, 1), (0, 2), (1, 3), (0, 3), (1, 1)], [(0, 3), (1, 3), (0, 1), (1, 1), (0, 2), (1, 3), (0, 3
), (1, 1)], [(0, 1), (1, 3), (0, 1), (1, 1), (0, 2), (1, 3), (0, 3), (1, 1)], [(0, 3), (1, 3), (0, 2), (1, 1), (0, 1), (
1, 3), (0, 3), (1, 1)], [(0, 2), (1, 3), (0, 2), (1, 1), (0, 1), (1, 3), (0, 3), (1, 1)], [(0, 1), (1, 3), (0, 2), (1, 1
), (0, 1), (1, 3), (0, 3), (1, 1)], [(0, 3), (1, 3), (0, 2), (1, 1), (0, 2), (1, 3), (0, 2), (1, 1)], [(0, 2), (1, 3), (
0, 2), (1, 1), (0, 2), (1, 3), (0, 2), (1, 1)], [(0, 1), (1, 3), (0, 2), (1, 1), (0, 2), (1, 3), (0, 2), (1, 1)], [(0, 3
), (1, 3), (0, 1), (1, 1), (0, 2), (1, 3), (0, 2), (1, 1)], [(0, 2), (1, 3), (0, 1), (1, 1), (0, 2), (1, 3), (0, 2), (1,
1)], [(0, 1), (1, 3), (0, 1), (1, 1), (0, 2), (1, 3), (0, 2), (1, 1)], [(0, 3), (1, 3), (0, 3), (1, 1), (0, 1), (1, 3),
(0, 2), (1, 1)], [(0, 2), (1, 3), (0, 3), (1, 1), (0, 1), (1, 3), (0, 2), (1, 1)], [(0, 1), (1, 3), (0, 3), (1, 1), (0,
1), (1, 3), (0, 2), (1, 1)], [(0, 3), (1, 3), (0, 2), (1, 1), (0, 1), (1, 3), (0, 2), (1, 1)], [(0, 2), (1, 3), (0, 2),
(1, 1), (0, 1), (1, 3), (0, 2), (1, 1)], [(0, 1), (1, 3), (0, 2), (1, 1), (0, 1), (1, 3), (0, 2), (1, 1)], [(0, 3), (1,
3), (0, 1), (1, 1), (0, 1), (1, 3), (0, 2), (1, 1)], [(0, 2), (1, 3), (0, 1), (1, 1), (0, 1), (1, 3), (0, 2), (1, 1)], [
(0, 1), (1, 3), (0, 1), (1, 1), (0, 1), (1, 3), (0, 2), (1, 1)], [(1, 1), (0, 1), (1, 1), (0, 1), (1, 3), (0, 3), (1, 3)
, (0, 3), (1, 3)], [(1, 1), (0, 1), (1, 1), (0, 1), (1, 2), (0, 3), (1, 3), (0, 3), (1, 3)], [(1, 1), (0, 1), (1, 1), (0
, 1), (1, 1), (0, 3), (1, 3), (0, 3), (1, 3)], [(1, 1), (0, 2), (1, 1), (0, 3), (1, 1), (0, 1), (1, 3), (0, 2), (1, 3)],
[(1, 3), (0, 2), (1, 3), (0, 3), (1, 1), (0, 3), (1, 3), (0, 2), (1, 2)], [(1, 3), (0, 1), (1, 3), (0, 2), (1, 2), (0, 1
), (1, 2), (0, 1), (1, 2)], [(1, 1), (0, 1), (1, 2), (0, 1), (1, 2), (0, 2), (1, 2), (0, 3), (1, 1)], [(1, 2), (0, 2), (
1, 1), (0, 1), (1, 3), (0, 1), (1, 1), (0, 2), (1, 1)], [(0, 3), (1, 1), (0, 2), (1, 1), (0, 3), (1, 1), (0, 1), (1, 3),
(0, 2), (1, 3)], [(0, 2), (1, 1), (0, 2), (1, 1), (0, 3), (1, 1), (0, 1), (1, 3), (0, 2), (1, 3)]]

  
#  4b solution is a lookup of the reverse-engineered solutions to each possible starting point  
def solve4B(cube):
    cHome=cube.side3facet(1,2,5)
    eHome=cube.side2facet(1,2)
    cloc=tuple(cube.facetLoc[cHome])
    eloc=tuple(cube.facetLoc[eHome])
    ce = cloc+eloc
    if ce in s4bCE:
        mv = s4bMoves[s4bCE.index(ce)]
        cube.rotateSides(mv)
        return(True)
    print("ce not found!!!",ce)
    printvars("cloc","eloc","cHome","eHome","ce")        
    return(False)
    
    
             
# generates all possible 4a solutions      
def allDoubleLaMoves():
    cube = Rcube()
    clocs=[(2,2),(1,4)]
    elocs=[(2,3),(1,5)]
    
    #sols [side][mvnum][cenum] = ce
    sols=  [      [              [(1,4,1,5)] ],  [[ (2,2,2,3)]] ]
    allsols=[(1,0,1,1), (2,2,2,3),(1,2,1,3),(1,4,1,5),(1,6,1,7),(3,4,3,5),(4,4,4,5)]
    moves=[    [              [ []         ] ], [ [ [] ] ] ]
    rmoves=[    [              [ []         ] ], [ [ [] ] ] ]
    turnsides=[0,1]

    for i in range(1,7):
        for s in [0,1]:
            sols[s].append([])
            moves[s].append([])
            rmoves[s].append([])
            turnsides[s]=1-turnsides[s]
            for p in range(len(sols[s][i-1])):
                for amt in [1,2,3]:
                    cube=Rcube()
                    theseMoves=copy.deepcopy(moves[s][i-1][p])
                    print("working",i,s,amt,p,theseMoves)
                    theseMoves.append([turnsides[s],amt])
                    cube.rotateSides(theseMoves)
                    cloc=cube.sposOfSpos(clocs[s])
                    eloc=cube.sposOfSpos(elocs[s])
                    ce=cloc+eloc
                    if ce in allsols: continue
                    allsols.append(ce)
                    sols[s][i].append(ce)
                    moves[s][i].append(theseMoves)
                    rmoves[s][i].append(Rcube.reverseMoves(theseMoves))
    print("sols",repr(sols))
    print("rmoves", repr(rmoves))
    cube=Rcube()
    if False:
        drawRubik(cube)
        for s in [0,1]:
            for m in range(len(sols[s])):
                for ce,mv in zip(sols[s][m],moves[s][m]):
                    cube=Rcube()
                    print("sm",s,m,ce,mv)
                    if (len(mv)):
                        cube.rotateSides(mv)
                        drawRubik(cube)
    
    at0=Rcube.attachedLocs(0)
    
    at1=Rcube.attachedLocs(1)
    cs0=[(0,i) for i in range(0,8,2)]
    cs1=[(1,i) for i in range(0,8,2)]
    es1=[(1,i) for i in range(1,8,2)]
    clocs=cs0+cs1
    clocs+=[at0[i] for i in range(len(at0)) if at0[i][1] in [0,2,4,6] and not at0[i] in clocs ]
    clocs+=[at1[i] for i in range(len(at1)) if at1[i][1] in [0,2,4,6] and not at1[i] in clocs]
    elocs=es1
    elocs+=[at0[i] for i in range(len(at0)) if at0[i][1] in [1,3,5,7] and not at0[i] in elocs ]
    print("got this many", len(allsols))
    print("cf",len(clocs),clocs)
    print("ef",len(elocs),elocs)
    if True:
        missing=[]
        for cloc in clocs:
            for eloc in elocs:
                ce = cloc+eloc
                if not ce in allsols:
                    missing.append(ce)
        print("missing",len(missing),missing)
 
# generate solutions to all possible 4b configurations
def all4Bmoves(): 
    cube = Rcube()
    tarf = [(1,6),(1,5),(1,7),(1,0),(1,1)]

    facetlist=       [ [(1,6, 1,5, 1,7, 1,0, 1,1)] ]
    flatfacetlist=[    (1,6, 1,5, 1,7, 1,0, 1,1)]
    solutionFacets= [ (1,6, 1,5)]
    moves= [ [ [ ] ] ]
    solutionMoves=[ [ ] ]
    rmoves=[ [ ] ]
    turnside=0
    ss=0
    
    for i in range(1,11):
        print("working on ",i)
        facetlist.append([])
        moves.append([])
        turnside=1-turnside
        for p in range(len(facetlist[i-1])):
            for amt in [1,2,3]:
                cube=Rcube()
                #cube.printRot=True
                theseMoves=copy.deepcopy(moves[i-1][p])
                theseMoves.append([turnside,amt])
                #print("working",i,amt,p,theseMoves)
                cube.rotateSides(theseMoves)
                cf = cube.sposOfSpos(tarf[0])
                ef = cube.sposOfSpos(tarf[1])
                f0 = cube.sposOfSpos(tarf[2])
                f1 = cube.sposOfSpos(tarf[3])
                f2 = cube.sposOfSpos(tarf[4])
                fs=cf+ef+f0+f1+f2
                ce=cf+ef
                #print("fs=",fs,f0,f1,f2)
                if fs in flatfacetlist: continue
                flatfacetlist.append(fs)
                facetlist[i].append(fs)
                moves[i].append(theseMoves)
                if  f0==(1,7) and f1==(1,0) and f2==(1,1):
                    solutionFacets.append(ce)
                    solutionMoves.append(theseMoves)
                    rmoves.append(Rcube.reverseMoves(theseMoves))
                    ss=len(solutionFacets)
                    print("added solution of",i,"moves",ss)
                    if ss==75: break
            if ss==75: break
        if ss==75: break
    print("sols",repr(solutionFacets))
    print("rmoves", repr(rmoves))
    cube=Rcube()
    if False:
        drawRubik(cube)
        for ce,mv in zip(solutionFacets,solutionMoves):
            cube=Rcube()
            print("sm",ce,mv)
            if (len(mv)):
                cube.rotateSides(mv)
                drawRubik(cube)
    
    at0=Rcube.attachedFacets(0)
    cs0=[(0,i) for i in range(0,8,2)]
    clocs=cs0+[(0,6),(2,0),(5,2)]
    clocs+=[at0[i] for i in range(len(at0)) if at0[i][1] in [0,2,4,6] ]
    elocs=[at0[i] for i in range(len(at0)) if at0[i][1] in [1,3,5,7]] + [(1,5)]
    print("got this many", len(solutionFacets))
    print("cf",len(clocs),clocs)
    print("ef",len(elocs),elocs)
    if True:
        missing=[]
        for cloc in clocs:
            for eloc in elocs:
                ce = cloc+eloc
                if not ce in solutionFacets:
                    missing.append(ce)
        print("missing",len(missing),missing)
  
def positionFinalCorners(cube):
    def findSwaps():
        cf = [cube.sposAtSpos((0,i)) for i in [0,2,4,6]]
        csp=[Rcube.cornerSideFacet(cf[i],topside)[1]//2 for i in range(4)]
        #print("cf",cf,"topside",topside,"csp",csp)
        swap=np.empty(4,bool)
        for i in range(4):
            swap[i] = ((csp[i] -csp[(i-1)%4])%4 != 1) and ((csp[(i+1)%4] -csp[i])%4 != 1)
        #print("csp",csp,"swap",swap,sum(swap))
        return(swap)

    topside=cube.sideAtSide(0)
    niklas=[[3,1],[0,3],[1,3],[0,1],[3,3],[0,3],[1,1]]
    swap=findSwaps()
    badcount=sum(swap)
    if badcount==4:
        cube.rotateSides(niklas)
        cube.rotateSides(niklas)
    elif badcount==2:
        for i in range(4):
            if swap[i] and swap[(i-1)%4]:
                #print("swapping", i, (i-1)%4)
                cube.rotateSide(0,-i,3)
                cube.rotateSides(niklas)
    
    a=cube.side3facet(0,1,4)
    b=cube.sposOfSpos(a)
    pos = Rcube.cornerSideFacet(b,0)[1]
    #print("pos",a,b,pos)
    cube.rotateSide(0,-pos//2)
    swap=findSwaps()
    cube.phase.append(len(cube.redTurns))
    if sum(swap)>0:
        print("failed to swap")
        return(False)
    else: return(True)
        
def twistFinalCorners(cube):
    sune=          [[1,1],[0,1],[1,3],[0,1],[1,1],[0,2],[1,3],[0,2]]
    antisune=    Rcube.reverseMoves(sune)
    def locateGoodies():
        topf = [cube.side3facet(0,1,4),cube.side3facet(0,4,3),cube.side3facet(0,3,2),cube.side3facet(0,2,1)]
        cf = [cube.sposOfSpos(topf[i]) for i in range(4)]
        #print("topf",topf)
        goodies=[Rcube.cornerSideFacet(cf[i],0) for i in range(4) if cf[i][0] ==0]
        badies=[Rcube.cornerSideFacet(cf[i] ,0) for i in range(4) if cf[i][0] !=0]
        #drawRubik(cube)
        return(goodies,len(goodies),badies,cf)

    goodies,goodCount,badies,cf=locateGoodies()
    if goodCount==4:
        return(0)
    elif goodCount==0:
        #print("zero", cf)
        #drawRubik(cube)
        if cf[1][0]==4:
            cube.rotateSides(antisune)
        else:
            cube.rotateSides(sune)
        #print("1?")
        #drawRubik(cube)
    elif goodCount==2:
        cube.rotateSide(0,(2-badies[0][1])//2,3)
        goodies,goodCount,badies,cf=locateGoodies()
        #drawRubik(cube)
        if cf[1][0]==3:
            cube.rotateSides(antisune)
        else:
            cube.rotateSides(sune)
        #drawRubik(cube)
    goodies,goodCount,badies,cf=locateGoodies()
    cube.rotateSide(0,(2-goodies[0][1])//2,3)
    goodies,goodCount,badies,cf=locateGoodies()
    #drawRubik(cube)
    if cf[0][0]==4:
        cube.rotateSides(sune)
    else:
        cube.rotateSides(antisune)
    return()

def positionFinalEdges(cube):
    allan=[[1,2],[0,3],[2,3],[4,1],[1,2],[2,1],[4,3],[0,3],[1,2]]
    antiallan=Rcube.reverseMoves(allan)
    bert=[[1,2],[3,2],[5,1],[2,2],[1,2],[3,2],[4,2],[1,2],[3,2],[5,3],[1,2],[3,2]]
    arne=[[2,2],[1,2],[3,2],[4,2],[5,1],[4,2],[3,2],[1,2],[2,2],[0,3]]
 
    def findStuff():
        side0=cube.sideAtSide(0)
        side1=cube.sideAtSide(1)
        posRot=Rcube.posRot0[side0][side1]
        facetTgt=np.array([[0,i] for i in [1,3,5,7]],np.int8)
        #print("facetTgt",facetTgt)
        facetCur=np.array([cube.facetLoc[side0,(i-posRot)%8] for i in [1,3,5,7]],np.int8)
        #print("facetCur", facetCur)
        facetDist = np.array([abs(facetTgt[i,1] - facetCur[i,1]) for i in range(4)],np.int8)
        #print(facetDist)
        return(facetDist,facetCur,facetTgt)
    facetDist,facetCur,facetTgt=findStuff()
    
    good=np.argwhere(facetDist==0)
    #print("good",good)
    #drawRubik(cube)
        
    if len(good)==4: return()
    elif len(good)==1:
        #print("allan")
        cube.rotateSide(0,(3-facetCur[good[0][0]][1])//2,3)
        facetDist,facetCur,facetTgt=findStuff()
        #drawRubik(cube)
        if (facetCur[0,1]==facetTgt[3,1]):
            cube.rotateSides(antiallan)
        else:
            cube.rotateSides(allan)
    elif  (facetCur[2,1]==facetTgt[0,1]):
        #print("arne")
        #drawRubik(cube)
        cube.rotateSides(arne)
        #drawRubik(cube)
    elif (facetCur[1,1]==facetTgt[0,1]):
        # print("bert")
        cube.rotateSides(bert)
    else:
        #print("rotbert")
        #drawRubik(cube)
        cube.rotateSide(0,1,3)
        #drawRubik(cube)
        cube.rotateSides(bert)
        #cube.rotateSide(0,2)
        #drawRubik(cube)
    return()

def solve233(cube):
    turnCount=len(cube.redTurns)
    doubleLa1(cube)
    doubleLa2(cube)
    solve4B(cube)
    cube.phase.append(len(cube.redTurns))
    return(len(cube.redTurns)-turnCount)

def PetrusSolve(xcube,debug=False,helmType='double'):
    useHelm=(helmType !='none')
    fullHelm=helmType in ('double','full')
    cube,step1TC,step2TC,step3TC,step4TC=solveThrough4(xcube,debug,helmType)
    turnCount=len(cube.redTurns)
#     drawRubik(cube,"after 233")
    if useHelm:
        success=helmSolve(cube,debug=debug,fullHelm=fullHelm)
        if success:
            cube.phase.append(len(cube.redTurns))
            turnCount=len(cube.redTurns)-turnCount
            return(cube,step1TC,step2TC,step3TC,step4TC,turnCount)
    success=positionFinalCorners(cube)
    twistFinalCorners(cube)
    cube.phase.append(len(cube.redTurns))
    positionFinalEdges(cube)
    cube.phase.append(len(cube.redTurns))
    turnCount=len(cube.redTurns)-turnCount
    return(cube,step1TC,step2TC,step3TC,step4TC,turnCount)

def solveThrough4(cube,debug=False, helmType='full'):
#     turns,cfHome,efHome=step1pairCE(cube)
#     curSide,toSide,cfHome=finish221(cube,cfHome,efHome)
#     f1,f2=solveThis222(cube,cfHome)
    fullHelm=helmType in ('double','full')
    step1TC=solve222(cube)
    ncube,step2TC=solve223(cube)
    if debug: drawRubik(ncube,"after 223")
    rots=[[],[(1,2,3),(0,3,3)]]
    bestTurns=9999
    for rot in rots:
        thisCube=ncube.copy()
    #         drawRubik(thisCube,"pre")
        thisCube.rotateSides(rot)
    #         drawRubik(thisCube,"post")
        step3TC=fixTwisted(thisCube,debug=debug,fullHelm=fullHelm)
        step4TC=solve233(thisCube)
        thisTurns=len(thisCube.redTurns)
#         printvars("thisTurns")
        if thisTurns<bestTurns:
            bestCube=thisCube
            bestTurns=thisTurns
    return(bestCube,step1TC,step2TC,step3TC,step4TC)

    
    
if __name__ == '__main__':
    pass
   
    
   