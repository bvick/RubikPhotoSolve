'''
Created on Nov 10, 2017

@author: bob vick

reads Rubik cube and renders it

'''


import copy
import math
import time

import cv2

import numpy as np
import statistics as stat
from drawRcube import  *


def nothing(x):pass

ESCAPE=27
PI=math.pi
r2d=180/PI
d2r=1/r2d


def rotateList(l,n=1) :
    if (len(l)<2):
        return(l)
    n= n % len(l)
    return(l[-n:] + l[:-n])

def gotEscapeKey():
    return(cv2.waitKey(1) & 0xFF in (ESCAPE, ord('q'),ord(' ')))

def escapeWait():
    while True:    
        if gotEscapeKey(): break
        time.sleep(.1)            
    cv2.destroyAllWindows()    

    
def rotX(angle):
    return(np.array([
        [1,0,0],
        [0,math.cos(angle),-math.sin(angle)],
        [0,math.sin(angle),math.cos(angle)]
        ]))
    
def rotY(angle):
    return(np.array([
        [math.cos(angle),0,-math.sin(angle)],
        [0,1,0],
        [math.sin(angle),0,math.cos(angle)]
        ]))
    
def rotZ(angle):
    return(np.array([
        [math.cos(angle),-math.sin(angle),0],
        [math.sin(angle),math.cos(angle),0],
        [0,0,1]
        ]))
 
def rotPoint(point,angles):
    return(np.matmul(rotZ(angles[2]),
              np.matmul(rotY(angles[1]),
                        np.matmul(rotX(angles[0]),point))))
    
def objToImg(obj):
    pixelsPerMM=np.array([5,-5])  # here's where we make y axis go down
    imgOff= np.array([320,240])  # put image in center of a 640x480 window
    img=np.empty(obj.shape,dtype=int)
    for i,o in enumerate(obj):
        img[i]=np.round(o*pixelsPerMM + imgOff)  
    return(img)
        
def pointsToPerspective(points,f,Z):
    persp = np.empty([len(points),2])
    for p,c in zip(persp,points):
        p[0] = c[0]*f/(Z+c[1])
        p[1] = c[2]*f/(Z+c[1])
    return(objToImg(persp))

def rotToCorner(points):
    rotPoints=np.array([np.matmul(rotX(30*d2r),np.matmul(rotZ(-PI/4),c)) for c in points])
    return(rotPoints)

def rotToEdge(points):
    rotPoints=np.array([np.matmul(rotX(45*d2r),c) for c in points])
    return(rotPoints)

def idealCubeCorners(img,f=154,Z=180,doCorner=True,show=True):  # points on image for rotated cube
    W = 58# width of cube in mm
    w = W/2
    
    corners = np.array([
        [-w,-w,-w],
        [w,-w,-w],
        [w,-w,w],
        [-w,-w,w],
        [-w,w,w],
        [w,w,w],
        [w,w,-w],
        [-w,w,-w]
        ])

    foff=W/3
    
    topFacets=[
        [-foff,-foff,w],
        [-foff,0,w],
        [-foff,foff,w],
        [0,foff,w],
        [foff,foff,w],
        [foff,0,w],
        [foff,-foff,w],
        [0,-foff,w],
        [0,0,w]
        ]
    facerots=[[0,0,0],[PI/2,0,0],[0,-PI/2,0],[-PI/2,0,0],[0,PI/2,0],[PI,0,0]]
    facets=[rotPoint(facet,angles) for angles in facerots for facet in topFacets ]

    if doCorner:
        rotCorners=rotToCorner(corners)
        rotFacets = rotToCorner(facets)
    else:
        rotCorners=rotToEdge(corners)
        rotFacets = rotToEdge(facets)
    
    imgPts=pointsToPerspective(rotCorners,f,Z)
    perspFacets=pointsToPerspective(rotFacets,f,Z)
    if doCorner: fcount=27
    else:fcount=18
    if not show:   return(perspFacets[:fcount])    
    #print("imgPts",imgPts)
    lineColor=(255,0,0)
    for i in range(3):
        x1,y1=imgPts[i]
        x2,y2=imgPts[i+1]
        cv2.line(img,pt1=(x1,y1),pt2=(x2,y2),color=lineColor,thickness=2)
    cv2.line(img,tuple(imgPts[3]),tuple(imgPts[0]),color=lineColor,thickness=2)
        
    cv2.line(img,tuple(imgPts[3]),tuple(imgPts[4]),color=lineColor,thickness=2)
    cv2.line(img,tuple(imgPts[5]),tuple(imgPts[4]),color=lineColor,thickness=2)
    cv2.line(img,tuple(imgPts[2]),tuple(imgPts[5]),color=lineColor,thickness=2)
    if doCorner:
        cv2.line(img,tuple(imgPts[1]),tuple(imgPts[6]),color=lineColor,thickness=2)
        cv2.line(img,tuple(imgPts[5]),tuple(imgPts[6]),color=lineColor,thickness=2)
    for c in perspFacets[:fcount]:
            cv2.circle(img,tuple(c),5,[255,0,0],-1)
    cv2.imshow('ideal lines',img)
    return(perspFacets[:fcount])    

def calibrateCameraPos():
    cv2.namedWindow("calibrate")
    cv2.createTrackbar('f','calibrate',0,500,nothing)
    cv2.createTrackbar('fZ1000','calibrate',0,3000,nothing)
    img=cv2.imread('rubeWB.jpg')
    while True:
        thisImg=copy.deepcopy(img)
        time.sleep(.01)
        cv2.imshow('calibrate',img)
        if (gotEscapeKey()): break
        f=cv2.getTrackbarPos('f','calibrate')
        fZ=cv2.getTrackbarPos('fZ1000','calibrate')
        if fZ>0:Z=f*1000/fZ
        else: Z=f
        idealCubeCorners(thisImg,f=f,Z=Z,doCorner=False) 
    cv2.destroyAllWindows()
    print("Z=",Z,"f=",f)

colorFilters={
        'red1': np.array([[0,90,50],[5,255,255]]),
        'red2': np.array([[170,90,30],[255,255,255]]),
        'blue': np.array([[90,90,61],[120,255,255]]),
        'orange': np.array([[6,90,25],[18,255,255]]),
        'green': np.array([[40,77,21],[85,255,255]]),
        'yellow': np.array([[21,85,25],[35,255,255]]),
        'white': np.array([[0,0,100],[255,70,255]])
        }  


def pointColor(i,point):
    
    for c in colorFilters:
        if cv2.inRange(np.array([[point]]),colorFilters[c][0],colorFilters[c][1])!=0:
            if c in ['red1','red2']: return('red') 
            else: return(c)
    else:
        #print("color identification failed",i,point,"colorizer=",point*[2.,100./255,100./255])
        return("")


def getPointColors(img,points):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    mimg=cv2.medianBlur(hsv,13)
    #k=mimg[tuple(points[0][::-1])]
    #print("gpc",k,points[0],pointColor(k))
    colors=[]
    facetHSV=[]
    for i in range(len(points)):
        ptHSV=mimg[(points[i,1],points[i,0])]
        facetHSV.append(ptHSV)
        ptColor=pointColor(i,ptHSV)
        colors.append(ptColor)
#         printvars("i","ptHSV","ptColor")
    return(colors,facetHSV)
   
def rubecapture(name,saveImg=False,doCorner=False,fromFile=False):
    #print(name)
    if fromFile:
        img=cv2.imread("rubik"+name+".jpg")
        facets=idealCubeCorners(copy.deepcopy(img),doCorner=doCorner,show=False)
        return(img,facets)
    cap = cv2.VideoCapture(0)
    while(True):
        time.sleep(.01)
        _, img = cap.read()
        cv2.imshow('frame',img)
        facets=idealCubeCorners(copy.deepcopy(img),doCorner=doCorner)
        if gotEscapeKey():
            if saveImg: cv2.imwrite("rubik"+name+".jpg",img)
            break
    cap.release()
    cv2.destroyAllWindows()    
    return(img,facets)

# gets facet colors from 3 images of cube
def readRubikCube(fromFiles=False):
    facetRots=[4,2,0,2,4,0]
    rcolors=('black','white','green','red','blue','orange','yellow')
    shots={
            "GO": ["top Green, front Orange",1,4],
            "WB": ["top White, front Blue", 0,3],
            "RY": ["top Red, front Yellow",2,5]
            }
    facetColors = np.empty([6,9],dtype=np.int8)
    for key in shots:
        prompt, topSide, frontSide=   shots[key]
        gotAll=False
        while not gotAll:
            if fromFiles:
                img,facets=rubecapture(key,fromFile=True)
            else:
                print("place cube where face center colors are", prompt, " and hit escape when all dots are inside facets")
                img,facets=rubecapture(key,saveImg=True)
            colors,facetHSV=getPointColors(img,facets[:18])
            if (key=="WB"): colors[8]='white'  # workaround to Rubik logo on center of white face
            for i,c in enumerate(colors):
                if c not in rcolors:
                    print("missing color on face",i//9,"facet",i%9, facetHSV[i])
                    break
            else:
                colors[0:8]=rotateList(colors[0:8],facetRots[topSide])
                colors[9:17]=rotateList(colors[9:17],facetRots[frontSide])
                #print(key,colors)
                for i,c in enumerate(colors):
                    facetColors[topSide]=list(map(rcolors.index,colors[:9]))
                    facetColors[frontSide]=list(map(rcolors.index,colors[9:]))
                gotAll=True
    colorCounts=np.bincount(facetColors.flatten())
    if np.any(colorCounts!=[0,9,9,9,9,9,9]):
        print("color identification failure")
    #print("cube is ", repr(facetColors))
    cube=Rcube.cubeFromColors(facetColors)
    drawRubik(cube)

 
if __name__ == '__main__':
    readRubikCube(fromFiles=False)
