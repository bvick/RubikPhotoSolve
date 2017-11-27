'''
Created on Nov 16, 2017

@author: bob

Data taken from Bernard Helmstetter's solutions to final layer.  
See http://www.ai.univ-paris8.fr/~bh/cube
These are routines to load the data and solve the final layer with it

'''
from Rcube import *
import re
from drawRcube import *
import pickle

# a few routines to convert between my side,position method to his location-orientation one
# for the following spos must be on side 0 or attached to 0
_cor0 = [(0,0),(0,2),(0,4),(0,6)]
_cor1 = [(1,2),(4,4),(3,4),(2,2)]
_cor2= [(4,6),(3,6),(2,4),(1,4)]
_cor=[_cor0,_cor1,_cor2]
_eor0 = [(0,7),(0,1),(0,3),(0,5)]
_eor1 = [(1,3),(4,5),(3,5),(2,3)]
_eor = [_eor0,_eor1]

def sposToLori(spos):
    for ors in [_cor,_eor]:
        ori = [i for i in range(len(ors)) if spos in ors[i]]
        if len(ori)>0:
            orient = ori[0]
            loc= ors[orient].index(spos)
            return(loc,orient)
    return(None)

def cornerLoriToSpos(lori):
    spos=_cor[lori[1]][lori[0]]
    return(spos)

def edgeLoriToSpos(cube,lori):
    spos=_eor[lori[1]][lori[0]]
    return(spos)

# assumes web page raw html is saved to file
# initial (Ux) is implemented as a reorientation
# moves are extended to ensure no net change to upper face    
# there are two different options here.  The fullHelm option also solves the orientation of the edges
# if that is selected, the Petrus step 3 only needs to fix the 3 edges not on the final layer
# "Hic sunt dracones" - lots of unreadable regular expressions   
def convertHelmstetter(fullHelm=True):
    state="out"
    combinations = {}
    if fullHelm:
        filename='solutions_567'
        statelen=16
    else: 
        filename='solutions_tout'
        statelen=12
    with open(filename+'.html','r') as f:
        for s in f:
            #printvars("state")
            s=s.strip()
            if state=='out':
                if re.match('<img',s):
                    state="between"
                    postimg=re.sub('<img.*<br>' , "",s)
                    nums=re.sub("[^\d ]","",postimg)
                    nlist=[int(n) for n in nums.split()]
                    case=nlist[0]
                    printvars("case")
                    cubestate=nlist[1:(1+statelen)]
                    dkey="".join(str(x) for x in cubestate)
                    if not fullHelm:
                        dkey=dkey+'0000'
            elif state=="moves":
                    rawmovestr=re.sub("^[^\d]+[ \d*]+","",s)
                    movestr=re.sub("²","2",rawmovestr)
                    removals=["&gt;","&lt;"]
                    for x in removals:
                        movestr=re.sub(x,"",movestr)
                    while True:
                        # look for those {foo as bar}
                        m=re.match(r'^[^{]*\{([^\s]+)[^}]+\}',movestr)
                        if m==None:
                            break
                        else:
                            movestr=re.sub(r'(^[^{]*)\{([^\s]+)[^}]+\}(.*)',r'\1\2\3',movestr)
#                         printvars("movestr")
                    # leading (Ux) is a reorientation
                    m= re.match(r'^[(]([^)]*)[)](.+)',movestr)
                    if m!=None:
                        orient,movestr=m.groups()
                        orientMoves=Rcube.standardToMoves(orient)[0]
                        orientMoves=[orientMoves+(3,)]
                    else: orientMoves=[ ]
                    movestr=re.sub(r'[\-\ ]','',movestr)
                    # get rid of other (xxx) which cancel out
                    movestr=re.sub(r'\([^\(]+\)','',movestr)
                    moves=orientMoves+Rcube.standardToMoves(movestr)  
                    # adjust for net change to the top .  Needed to ensure mirrors and inverses work
                    cube=Rcube()
                    cube.rotateSides(moves)
                    facet=(0,0)
                    spos=Rcube.cornerSideFacet(cube.facetLoc[facet],0)
                    adjMove=(0,((-spos[1])//2)%4)
                    combinations[dkey]=moves+[adjMove]
#                     printvars("case","facet","movestr","moves","adjMove")
                    state='out'
            elif state=='between':
                    state='moves'
    pickle.dump(combinations,open(filename+".p","wb"))
    return(combinations)


# relative locations are sometimes handy...
def relState(state):
    return(tuple((np.array(state,int)- [0,1,2,3,0,0,0,0,0,1,2,3,0,0,0,0])%4))

def stateStr(state):
    s=""
    for i,v in enumerate(state):
        s+=str(v)
        if i%4 == 3: s+=" "
    return(s)



def topState(cube):
    cloc,crot,eloc,erot=decat([9]*16,4)
    topSide=cube.sideAtSide(0)
    
    for pos in range(8):
        thisLoc=sposToLori((0,pos))[0]
        facet=cube.facetAtLoc[0,pos]
        if pos%2==0: #always relative to front-left
            sbTopFacet=Rcube.cornerSideFacet(facet,topSide)
        elif Rcube.facetSide(facet)==topSide: sbTopFacet=facet
        else: sbTopFacet=Rcube.edgeOtherFacet(facet)
        sbtfOri=sposToLori(tuple(cube.facetLoc[sbTopFacet]))[1]
        if pos==0:
            f0pos=Rcube.facetPos(sbTopFacet)
        sbPos=(Rcube.facetPos(sbTopFacet)-f0pos)%8
        lori=sposToLori((0,sbPos))
        if pos%2==0:
            cloc[thisLoc] = lori[0]
            crot[thisLoc] = sbtfOri
        else:
            eloc[thisLoc]=lori[0]
            erot[thisLoc]=sbtfOri
    return(tuple(cloc+crot+eloc+erot))

def renumberState(state):
    cloc,crot,eloc,erot=decat(np.array(state,int),4)
    rel=cloc[0]
    ncloc=(cloc-rel)%4
    neloc=(eloc-rel)%4
    return(tuple(np.array([ncloc,crot,neloc,erot],int).flatten()))
            

def mirrorXTopState(ts):
    cloc,crot,eloc,erot=decat(list(ts),4)
    ncloc=[3-cloc[3-i] for i in range(4)]
    ncrot=[swapab(crot[swapabcd(i,1,2,0,3)],1,2) for i in range(4)]
    neloc=[swapab(eloc[swapab(i,1,3)],1,3) for i in range(4)]
    nerot=[erot[swapab(i,1,3)] for i in range(4)]
    state=tuple(ncloc+ncrot+neloc+nerot)
    return(state)
    
def mirrorYTopState(ts):
    cloc,crot,eloc,erot=decat(list(ts),4)
    ncloc=[swapabcd(cloc[swapabcd(i,0,1,2,3)],0,1,2,3) for i in range(4)]
    ncrot=[swapab(crot[swapabcd(i,0,1,2,3)],1,2) for i in range(4)]
    neloc=[swapab(eloc[swapab(i,0,2)],0,2) for i in range(4)]
    nerot=[erot[swapab(i,0,2)] for i in range(4)]
    state=tuple(ncloc+ncrot+neloc+nerot)
    return(state)
    
def mirrorXYTopState(ts):
    return(mirrorYTopState(mirrorXTopState(ts)))

def invertTopState(ts):
    cloc,crot,eloc,erot=decat(list(ts),4)
    ncrot=[9]*4
    nerot=[9]*4
    ncloc=[cloc.index(i) for i in range(4)]
    neloc=[eloc.index(i) for i in range(4)]
    for i in range(4):
        ncrot[cloc[i]] = swapab(crot[i],1,2)
        nerot[eloc[i]] = erot[i]
    state=tuple(ncloc+ncrot+neloc+nerot)
    return(state)
        
  
def helmSolve(cube,debug=False,fullHelm=False):
    if fullHelm:
        filename='solutions_567'
    else:
        filename='solutions_tout'
    comb=pickle.load(open(filename+".p","rb"))
    for r in range(4):
        cube.rotateSide(0,r,3)
        state0=topState(cube)
        if debug:
            drawRubik(cube,"rotated "+str(r)+" "+stateStr(state0))
        for xmirror in [False,True]:
            if xmirror: state1=renumberState(mirrorXTopState(state0))
            else:state1=state0
            for ymirror in [False,True]:
                if ymirror: state2=renumberState(mirrorYTopState(state1))
                else: state2=state1
                for invert in [False,True]:
                    if invert: state3=renumberState(invertTopState(state2))
                    else: state3=state1
                    sstate="".join(str(x) for x in state3)
                    if debug: 
                        vstate=stateStr(state3)
                        printvars('r','xmirror','ymirror','invert','vstate')
                    if sstate in comb:
                        if debug: print("found combo")
                        moves=comb[sstate]
                        if invert: moves=Rcube.reverseMoves(moves)
                        if xmirror: moves=Rcube.mirrorXmoves(moves)
                        if ymirror: moves=Rcube.mirrorYmoves(moves)
                        cube.rotateSides(moves)
                        facet=cube.side3facet(0,1,4)
                        spos=cube.facetLoc[facet]
                        adjMove=(0,((-spos[1])//2)%4)
                        cube.rotateSide(*adjMove)
                        return(True)
        cube.rotateSide(0,-r,3)
    if debug: print("********* no combo found")
    return(False)
            

if __name__ == '__main__':
    convertHelmstetter(fullHelm=True)