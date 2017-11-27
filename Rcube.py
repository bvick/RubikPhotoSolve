'''
Created on Oct 30, 2017

@author: bob vick

These are structures and functions for managing a Rubik's Cube.  A cube is an object of class Rcube.
Terminology:
side - one of the 6 faces of a cube.
facet - one of the 54 (9 for each side) surfaces.  (Lars Petrus calls them "stickers")
corner - one of the 8 corner pieces, each having 3 facets
edge - one of the 12 pieces between corners, each having 2 facets
center- the piece in the middle of each side, having 1 facet
turn- usually a turning of a single side, but can also be a reorientation of the cube, about a side (or better said, about an axis normal to a side)


'''
import numpy as np
from util import *
import copy

# the side turns are done by multiplying the location of each affected facet by a rotation matrix.
# this creates a matrix for a particular axis and rotation amount
def rotMat(axis,amt):
    amt=amt%4
    use=np.array([[1,2],[0,2],[0,1]],np.int8)
    # 2x2 's for each turn amount.  these get expanded to 3x3 depending on axis of rotation
    r22 = np.array([
            [[1,0],[0,1]],
            [[0,1],[-1,0]],
            [[-1,0],[0,-1]],
            [[0,-1],[1,0]]],np.int8)
    rmat=np.identity(3,np.int8)
    for i in [0,1]:
        for j in [0,1]:
            rmat[use[axis,i],use[axis,j]] = r22[amt,i,j]
    return(rmat)

rotMats=np.array([[rotMat(j,i) for i in range(4)] for j in range(3)],np.int8)


class Rcube(object):
    '''
    classdocs
    '''
    '''
    STRUCTURE 
    
    3 ways of addressing facets:

    addresses (adr) view the cube centered, with x,y,z in +/-[0,1,2]:
    a +/- 2 for the side coordinate , otherwise location on side
    These are mainly used for rotations (done by matrix multiplication) and rendering 
    
    side,pos  (referred to as spos or loc) is another scheme.  sides are numbered 0-5: UFRBLD in standard parlance.
    pos is 0-8 where 8 is center facet, 0 is facet closest to the 
    lower front left vertex, and the rest are numbered clockwise from 0.
    This scheme is the primary scheme for solving the cube
   
    for simplification purposes facets are numbered sequentially.  This is just a compression
    of the side,pos scheme into a single number.
   
    turns is a list of turn elements [side,amt,slice] where amt is 0-3 clockwise rotations
    and slice is 1 for normal side turn and 3 for turning entire cube about a side
    redTurns reduce turns by compressing or eliminating consecutive turns of the same
    side and also normalize away whole cube reorientations, so these are the actual side turns
    required to solve the cube. 
    '''
    
    facetHomes=np.array([[i,j]  for i in range(6) for j in range(9)],np.int8)  
    facetColors=np.array([[i+1]*9 for i in range(6)],np.int8).flatten()
    oppositeSide=np.array([5,3,4,1,2,0])

    @staticmethod
    def invertFloc(floc):
        fal=np.empty([6,9],np.int8)
        for i in range(54):
            s,p=floc[i]
            fal[s,p]=i
        return(fal)
    
    def __init__(self, startingFacetLoc=facetHomes):
        # facetLoc is the current location of a facet, the latter identified by it's "home" location
        self.facetLoc = np.copy(startingFacetLoc)
        # inverse of above, i.e. what facet is at a given location
        self.facetAtLoc=Rcube.invertFloc(self.facetLoc)
        # list of all turns that have been applied to a cube since it's initial configuration
        self.turns=[ ]
        # reduced turns are the above turns, but ignoring reorientations and reducing sequential
        # turns of the same side down to 1 or possible zero net turns
        self.redTurns= [ ]
        # each phase in a solution may append len(redTurns) here. Used in rendering phase-by-phase 
        self.phase=[ ]
        self.rawPhase=[ ]
        # also used in rendering.  Identifies how much pausing to do
        self.replayLevel=0
        # for debugging.  If true, output each turn as it is done
        self.printRot=False

    def copy(self):
        newCube=Rcube(self.facetLoc)
        newCube.turns=copy.deepcopy(self.turns)
        newCube.redTurns=copy.deepcopy(self.redTurns)
        newCube.phase=copy.deepcopy(self.phase)
        newCube.replayLevel = self.replayLevel
        newCube.printRot=self.printRot
        return(newCube)

    # make a cube with random turns applied to it
    @staticmethod
    def mkRandom(turns=30):
        a=Rcube()
        for _ in range(turns):
            f=np.random.randint(0,6)
            d=np.random.randint(1,4)
            a.rotateSide(f,d)
        a.turns= [ ]
        a.redTurns=[ ]
        return(a)

    def markPhase(self):
        self.phase.append(len(self.redTurns))
        self.rawphase.append(len(self.turns))

    '''
    ADDRESS MANIPULATION
    '''
    @staticmethod
    def facetHome(facet):
        return(facet//9,facet%9)
    
    @staticmethod
    def home2facet(spos):
        return(spos[0]*9+spos[1])
    
    @staticmethod
    def facetSide(facet): 
        return(facet//9)
    
    @staticmethod
    def facetPos(facet): 
        return(facet%9)
    
    @staticmethod
    def adr2spos(adr):
        side,nonSide=Rcube.adrSplitSide(adr)
        pos=Rcube.pos2xy(side).index(list(nonSide))
        return(side,pos)

    @staticmethod
    def spos2adr(spos):
        side,pos=spos
        xy=Rcube.pos2xy(side)[pos]
        ipoint=[2,1,0,1,0,2][side]
        fval=[2,-2,2,2,-2,-2][side]
        #print("f2",side,pos,xy,ipoint,fval)
        xy.insert(ipoint,fval)
        #print("f2",side,pos,xy,ipoint,fval)
        return(np.array(xy,np.int8))

    @staticmethod
    def facet2adr(facet):
        return(Rcube.spos2adr(Rcube.facetHome(facet)))

    @staticmethod
    def adr2facet(adr):
        return(Rcube.home2facet(Rcube.adr2spos(adr)))

    def homeAdr2cur(self,adr):
        facet = Rcube.adr2facet(np.array(adr,np.int8))
        nfp=tuple(self.facetLoc[facet])
        return(Rcube.spos2adr(nfp))
    
    def curAdr2home(self,adr):
        sp = Rcube.adr2spos(np.array(adr,np.int8))
        facet=self.facetAtLoc[sp]
        return(Rcube.facet2adr(facet))

    def sposAtSpos(self,spos):
        return(Rcube.facetHome(self.facetAtLoc[spos]))

    def sposOfSpos(self,spos):
        return(tuple(self.facetLoc[Rcube.home2facet(spos)]))

    # returns the side number given an address
    @staticmethod       
    def adrSide(adr):
        side=[[4,1,5],[2,3,0]]
        coord=np.argmax(abs(adr))
        s = (np.sign(adr[coord])+1)//2
        return(side[s][coord])

    @staticmethod
    def adrSplitSide(adr):
        return(Rcube.adrSide(adr),np.array([x for x in adr if abs(x)!=2],np.int8))
    
    @staticmethod
    def joinSide(side,xy):
        sideZ=[2,-2,2,2,-2,-2][side]
        if side in [2,4]: return([sideZ,xy[0],xy[1]])
        elif side in [1,3]: return([xy[0],sideZ,xy[1]])
        else: return(np.array([xy[0],xy[1],sideZ],np.int8))

    @staticmethod
    def sliceDist(toAdr,fromAdr): # assumes common side
        _,toWW=Rcube.adrSplitSide(toAdr)
        _,fromWW=Rcube.adrSplitSide(fromAdr)
        rmat=np.array([[0,-1],[1,0]],np.int8)
        r1=fromWW
        for i in [1,2,3]:
            r1=np.matmul(rmat,r1)
            if np.array_equal(r1,toWW): return(i)
        return(None)
     
     
    @staticmethod
    def pos2xy(side):
        if side <3: return([[-1,-1],[-1,0],[-1,1],[0,1],[1,1],[1,0],[1,-1],[0,-1],[0,0]])
        else: return([[-1,-1],[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[0,0]])
     
    # how are positions on side0 rotated if side0,side1 are now at 0, 1
    # 9 for impossible pairs
    posRot0=[
        [9,0,2,4,6,9],
        [4,9,2,9,6,0],
        [4,6,9,2,9,0],
        [2,9,4,9,0,6],
        [2,0,9,4,9,6],
        [9,6,4,2,0,9]
        ]

    posRot1=[
        [9,0,0,6,6,9],
        [4,9,2,9,4,2],
        [6,6,9,0,9,0],
        [0,9,6,9,0,6],
        [2,2,9,4,9,4],
        [9,4,4,2,2,9]
            ]    

    @staticmethod
    def side2center(side):
        return(Rcube.spos2adr((side,8)))
     
    def sideAdr(self,side):
        cside,_=Rcube.adr2spos(self.homeAdr2cur(Rcube.side2center(side)))
        return(cside)
    
    def sideAtSide(self,side):
        cside,_=Rcube.adr2spos(self.curAdr2home(Rcube.side2center(side)))
        return(cside)
        
    @staticmethod
    def edgeOtherLoc(spos):
        adr=Rcube.spos2adr(spos)
        for i in range(3):
            if abs(adr[i])==1: adr[i] = 2*adr[i]
            elif abs(adr[i])==2: adr[i] = adr[i]//2
        return(Rcube.adr2spos(adr))
        
    @staticmethod
    def edgeOtherFacet(facet):
        adr=Rcube.facet2adr(facet)
        for i in range(3):
            if abs(adr[i])==1: adr[i] = 2*adr[i]
            elif abs(adr[i])==2: adr[i] = adr[i]//2
        return(Rcube.adr2facet(adr))
        
    @staticmethod
    def cornerOtherLocs(spos):
        adr=Rcube.spos2adr(spos)
        aadr=abs(adr)
        sadr=np.sign(adr)
        rsign=np.prod(sadr)
        return(Rcube.adr2spos(np.roll(aadr,-rsign)*sadr),Rcube.adr2spos(np.roll(aadr,rsign)*sadr))

    @staticmethod
    def cornerOtherFacets(facet):
        adr=Rcube.facet2adr(facet)
        aadr=abs(adr)
        sadr=np.sign(adr)
        rsign=np.prod(sadr)
        return(Rcube.adr2facet(np.roll(aadr,-rsign)*sadr),Rcube.adr2facet(np.roll(aadr,rsign)*sadr))

    # for corner piece of facet return other facet of corner that is on side    
    @staticmethod
    def cornerSideLoc(spos,side):
        if spos[0]==side: return(spos)
        for loc in Rcube.cornerOtherLocs(spos):
#             printvars("loc","spos")
            if loc[0]==side: return(loc)
        return(None)
        
    @staticmethod
    def cornerSideFacet(facet,side):
        if Rcube.facetHome(facet)[0]==side: return(facet)
        for f in Rcube.cornerOtherFacets(facet):
            if  Rcube.facetHome(f)[0]==side: return(f)
        return(None)
 
    # 3 sides of a corner piece, and facets between them clockwise
    @staticmethod
    def cornerSidesPlus(cfHome):  
        cfHome=np.array(cfHome)
        signs=np.sign(cfHome)
        rotdir = -np.sign(np.prod(signs))
        side0,_ = Rcube.adr2spos(cfHome)
        cfAbs=np.abs(cfHome)
        side1,_ = Rcube.adr2spos(signs*np.roll(cfAbs,rotdir))
        center1=np.array(Rcube.side2center(side1))
        side2,_= Rcube.adr2spos(signs*np.roll(cfAbs,2*rotdir))
        center2=np.array(Rcube.side2center(side2))
        facet1=center1+center2//2
        facet2=center2+center1//2
        return(side0,side1,side2,facet1,facet2)
    
    #facet on side1 of corner between 3 sides
    def side3facet(self,side1,side2,side3):
        #print("faf",side1,cube.sideAtSide(side1),side2,cube.sideAtSide(side2),side3,cube.sideAtSide(side3))
        adr=Rcube.side2center(self.sideAtSide(side1)) + \
            Rcube.side2center(self.sideAtSide(side2))//2 + \
            Rcube.side2center(self.sideAtSide(side3))//2
        return(Rcube.adr2facet(adr))
    
    #facet on side1 of edge between side1 and side2
    def side2facet(self,side1,side2):
        adr=Rcube.side2center(self.sideAtSide(side1)) +\
            Rcube.side2center(self.sideAtSide(side2))//2
        return(Rcube.adr2facet(adr))
    
    # facets of corner between 3 sides
    def side3facets(self,side1,side2,side3):
        sides=[side1,side2,side3]
        facets=[ ]
        for i in range(3):
            rsides=tuple(sides[i:]+sides[:i])
            facets.append(self.side3facet(*rsides))
        return(facets)
        
    
    # the other facets of edges on side
    # i.e. those edge facets that also move when a side is turned
    @staticmethod
    def attachedEdgeFacets(side):
        def listRot(l,r):
            return(l[-r:]+l[:-r])
        center=Rcube.side2center(side)
        k = np.argwhere(abs(center)==2)[0][0]
        off=center[k]//2
        radr=np.array(list(map(lambda x: x[-k:]+x[:-k], [[off,0,-2],[off,0,2],[off,-2,0],[off,2,0]])),np.int8)
        facets = [Rcube.adr2facet(adr) for adr in radr]
        return(facets)

    @staticmethod
    def attachedEdgeLocs(side):
        def listRot(l,r):
            return(l[-r:]+l[:-r])
        center=Rcube.side2center(side)
        k = np.argwhere(abs(center)==2)[0][0]
        off=center[k]//2
        radr=np.array(list(map(lambda x: x[-k:]+x[:-k], [[off,0,-2],[off,0,2],[off,-2,0],[off,2,0]])),np.int8)
        sps = [Rcube.adr2spos(adr) for adr in radr]
        return(sps)

    # all facets not on side that also move when side is turned
    @staticmethod
    def attachedFacets(side):
        def listRot(l,r):
            return(l[-r:]+l[:-r])
        center=Rcube.side2center(side)
        k = np.argwhere(abs(center)==2)[0][0]
        off=center[k]//2
        adr=[[off,i,-2] for i in [-1,0,1]]+[[off,i,2] for i in [-1,0,1]]+[[off,-2,i] for i in [-1,0,1]]+[[off,2,i] for i in [-1,0,1]]
        radr=np.array(list(map(lambda x: x[-k:]+x[:-k], adr)),np.int8)
        facets = [Rcube.adr2facet(adr) for adr in radr]
        return(facets)
        
    # facets of corners of side rotated CW
    @staticmethod
    def attachedCorner1Facets(side):
        return([Rcube.cornerFacets((side,i))[0] for i in [0,2,4,6]])
 
    # facets of corners of side rotated CCW
    @staticmethod
    def attachedCorner2Facets(side):
        return([Rcube.cornerFacets((side,i))[1] for i in [0,2,4,6]])
 
    # rotation is amt*90 degrees clockwise about axis(0,1,2=x,y,z resp)
    # slices is 1 for just side, 2(not implemented) for side and center slice, 3 for whole cube
    def rotateSide(self,side,amt,slices=1):
        amt=amt%4
        if self.printRot: print("rotating",side,amt,"R" if slices==3 else "")
        if amt==0: return()
        gt = [3,.5,-.5,-3][slices]  # identifies which facets are moved
        sideSign=[1,-1,1,1,-1,-1][side]
        rotSign=[1,1,1,-1,-1,-1][side]
        axis=[2,1,0,1,0,2][side]
        self.turns.append([side,amt,slices])
        # normalized turns - compresses away consecutive turns of same side, and
        # adjusts away cube reorientations
        if (slices==1):
            nSide=self.sideAtSide(side)
            if len(self.redTurns)>0 and self.redTurns[-1][0]==nSide:
                newAmt=(self.redTurns[-1][1] + amt) %4
                if newAmt>0:
                    self.redTurns[-1][1] =newAmt
                else:
                    self.redTurns.pop()
            else:
                self.redTurns.append([nSide,amt]) 
        amt = (rotSign*amt)%4
        wFacetLoc=np.copy(self.facetLoc)
        rotMat=rotMats[axis,amt]

#         # the actual turn is done with matrix multiplication on addresses that are affected
        for i in range(54):
            adr=Rcube.spos2adr(self.facetLoc[i])
            if sideSign*adr[axis]>gt:
                wFacetLoc[i]=Rcube.adr2spos(np.matmul(rotMat,adr))
        self.facetLoc=wFacetLoc
        self.facetAtLoc=Rcube.invertFloc(self.facetLoc) 
        
      
    def collapseTurns(self):
        cturns=[ ]
        for turn in self.turns:
            side,amt,slices=turn
            if len(cturns)>0 and cturns[-1][0]==side and slices==cturns[-1][2]:
                newAmt=(cturns[-1][1] + amt) %4
                if newAmt>0:
                    cturns[-1][1] =newAmt
                else:
                    cturns.pop()
            else:
                cturns.append(turn)
#         print("collapse",len(self.turns),len(cturns),cturns)
        return(cturns)

    def rotateSides(self,famts):
        for fa in famts:
            self.rotateSide(*fa)

    # rotate a side to get facet from one position to another
    def rotatePos(self,side,fromPos,toPos):
        self.rotateSide(side,(toPos-fromPos)//2)
        return(toPos)
    
    # given facet colors, construct a cube with facet locations that result in those colors
    @staticmethod
    def cubeFromColors(facetColors):
        fLoc=np.copy(Rcube.facetHomes)
        cube=Rcube()
        for side in range(6):
            for pos in range(9):
                spos=(side,pos)
                sideOfFacet=facetColors[spos]-1
                if pos==8:
                    fLoc[sideOfFacet*9+8]=spos
                elif pos in [1,3,5,7]:
                    eoLoc=Rcube.edgeOtherLoc(spos)
                    eoSide=facetColors[eoLoc]-1
                    facet=cube.side2facet(sideOfFacet,eoSide)
                    fLoc[facet]=spos
                else:
                    coLoc1,coLoc2=Rcube.cornerOtherLocs(spos)
                    coSide1=facetColors[coLoc1]-1
                    coSide2=facetColors[coLoc2]-1
                    facet=cube.side3facet(sideOfFacet,coSide1,coSide2)
                    fLoc[facet]=spos
        #print(repr(fLoc))
        cube=Rcube(fLoc)
        return(cube)
        
    def printTurns(self,norm=True,colors=True):
        if colors: t1map = "WGRBOY"
        else: t1map="UFRBLD"
        t2map=['','','2',"'"]
        if (norm): turns=self.redTurns
        else: turns=self.turns
        print("\n",len(turns),"turns:")
        for i,turn in enumerate(turns):
            if i%30 == 0:
                print()
            print(t1map[turn[0]]+t2map[turn[1]],end=' ')
            if i%5==4: print("  ",end="")
        print()

    @staticmethod
    def standardToMoves(s):
        s=list("".join(s.split()))
        moves=[ ]
        sides="UFRBLD"
        while len(s)>0:
            c = s.pop(0)
            side=sides.index(c)
            if len(s)>0 and s[0] =="2":
                moves.append((side,2))
                s.pop(0)
            elif len(s)>0 and s[0]=="'":
                moves.append((side,3))
                s.pop(0)
            else:
                moves.append((side,1))
        return(moves)

    @staticmethod
    def movesToStandard(moves):
        sides="UFRBLD"
        marks=["","","2","'"]
        s = ""
        for i,move in enumerate(moves):
            s += sides[move[0]]+marks[move[1]]
            if i%5==4: s+=" "
        return(s)

    @staticmethod     
    def reverseMoves(mv):
        newmv=[]
        for m in mv[::-1]:
            if len(m)==2: newmv.append((m[0],(-m[1])%4))
            else: newmv.append((m[0],(-m[1])%4,(-m[2])%4))
        return(newmv)
    
    @staticmethod     
    def mirrorXmoves(mv):
        newmv=[]
        for m in mv:
            if m[0] in [2,4]: side=6-m[0]
            else: side=m[0]
            if len(m)==2: newmv.append((side,(-m[1])%4))
            else: newmv.append((side,(-m[1])%4,(-m[2])%4))
        return(newmv)
          
    @staticmethod     
    def mirrorYmoves(mv):
        newmv=[]
        for m in mv:
            if m[0] in [1,3]: side=4-m[0]
            else: side=m[0]
            if len(m)==2: newmv.append((side,(-m[1])%4))
            else: newmv.append((side,(-m[1])%4,(-m[2])%4))
        return(newmv)

    # cube is done if all facets are in the right place.
    # flists can be reduced to verify partial completion
    def checkDone(self,flists= [
            [0,[8,0,1,2,3,4,5,6,7]],
            [1,[8,5,6,7,0,1,2,3,4]],
            [2,[8,5,6,7,0,1,2,3,4]],
            [3,[8,0,1,2,3,4,5,6,7]],
            [4,[8,0,1,2,3,4,5,6,7]],
            [5,[8,0,1,2,3,4,5,6,7]]
            ]):
        for flist in flists:
            side,posList = flist
            side0,_=self.sposAtSpos((side,posList[0]))
            for pos in posList[1:]:
                siden,_=self.sposAtSpos((side,pos))
                if siden!=side0: 
                    print("mismatch at[",side,pos,"] ", siden,"should be",side0)
                    return(False)
        return(True)
