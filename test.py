'''
Created on Sep 30, 2017

@author: bob
'''
from Rcube import *
from PetrusSolver import * 
from drawRcube import *
from util import *
from HelmstetterSolver import *

flocs=np.array([[[2, 0], [0, 5], [3, 0], [2, 5], [2, 6], [0, 1], [0, 2], [0, 3], [0,
8]], [[0, 0], [3, 1], [5, 2], [3, 5], [3, 6], [1, 1], [2, 4], [1, 3], [1, 8]],
[[0, 4], [4, 7], [4, 4], [4, 5], [5, 4], [2, 1], [0, 6], [5, 1], [2, 8]], [[1,
0], [5, 3], [2, 2], [1, 5], [3, 2], [3, 3], [5, 6], [5, 7], [3, 8]], [[4, 6],
[4, 3], [5, 0], [4, 1], [4, 2], [2, 3], [1, 6], [5, 5], [4, 8]], [[1, 2], [0,
7], [3, 4], [1, 7], [1, 4], [2, 7], [4, 0], [3, 7], [5, 8]]],
               np.int8)
    

runSaved = 0
pairDone=[ ]

if runSaved==0: runCount=10000
else: runCount=1
notfound=0
total=step1Total=step2Total=step3Total=step4Total=step567Total=0
tmax=step1max=step2max=step3max=step4max=step567max=0
step1=step2=step3=step4=step567=0
for i in range(runCount):
#     print(i)
    if runSaved!=0:
        cube=Rcube(flocs)
    else:     
        cube=Rcube.mkRandom()
#         printrepr(cube.facetLoc)
    startingFlocs=cube.facetLoc
    if runSaved!=0: 
        drawRubik(cube,"starting cube")
        success=helmSolve(cube,debug=True,fullHelm=True)
        drawRubik(cube,"after Helm")
    else:
        cube,step1,step2,step3,step4,step567=PetrusSolve(cube)
        step1Total+=step1
        step2Total+=step2
        step3Total+=step3
        step4Total+=step4
        step567Total+=step567
        step1max=max(step1,step1max)
        step2max=max(step2,step2max)
        step3max=max(step3,step3max)
        step4max=max(step4,step4max)
        step567max=max(step567,step567max)
    if not cube.checkDone():
        print("********************FAILED")
        printrepr(startingFlocs)
        break
    else:
        thisTotal=len(cube.redTurns)
        total+=thisTotal
        tmax=max(thisTotal,tmax)

        printvars("step1","step2","step3","step4","step567","thisTotal",label="done "+ str(i+1) )
        printvars("step1max","step2max","step3max","step4max","step567max","tmax",label="done "+ str(i+1) )
        print("average of", i+1, "samples: "
              "step1=",round(step1Total/(i+1),1),
              "step2=",round(step2Total/(i+1),1),
              "step3=",round(step3Total/(i+1),1),
              "step4=",round(step4Total/(i+1),1),
              "step567=",round(step567Total/(i+1),1),
              "  total",  round(total/(i+1),1)
              )        
printvars("notfound")
    