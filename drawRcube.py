'''
Created on Oct 31, 2017

@author: bob
'''

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import os
import time
#import numpy as np
from Rcube import  *
import PetrusSolver
import copy

CUBE_SIZE=3.
CUBE_SIZE=4.
SPACE=.015*CUBE_SIZE
FACET_SIZE=(CUBE_SIZE-4*SPACE)/3

rcolors=('black','white','green','red','blue','orange','yellow')
ESCAPE = b'\033'
helpText='q-quit   s-solve   x-randomize    n-clean   ufrbld-rotate sides   0123-replay level' 
colorToRGB=[
    [0.,0.,0.0],  # black
    [1.0,1.0,1.0], # white
    [0.0,0.5,0.0], # green
    [1.0,0.0,0.0], # red
    [0.0,0.0,1.0], # blue
    [1,0.6,0.0], # orange
    [1.0,1.0,0.0],  # yellow
    [0.,1,0.],
    [1,.7,.78],
    ]
sideRot=(0,0,0)

def InitGL(Width, Height):                # We call this right after our OpenGL window is created.
    glClearColor(0.0, 0.0, 0.0, 0.0)    # This Will Clear The Background Color To Black
    glClearDepth(1.0)                    # Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LESS)                # The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)                # Enables Depth Testing
    glShadeModel(GL_SMOOTH)                # Enables Smooth Color Shading
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()                    # Reset The Projection Matrix
                                        # Calculate The Aspect Ratio Of The Window
    gluPerspective(60.0, float(Width)/float(Height), 0.1, 100.0)


def ReSizeGLScene(Width, Height):
    if Height == 0:                        # Prevent A Divide By Zero If The Window Is Too Small 
        Height = 1

    glViewport(0, 0, Width, Height)        # Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

mouseDown=False   
xdiff=382
ydiff=-146
xrot=30
yrot=-45


def mouseButtonHandler(button,state,x,y):
    global mouseDown,xrot,yrot,xdiff,ydiff
    if (button == GLUT_LEFT_BUTTON and state==GLUT_DOWN):
        mouseDown=True
        xdiff=x-yrot
        ydiff=-y+xrot
#         printvars("xdiff","ydiff","xrot","yrot")
    else:
        mouseDown=False
    return()

def mouseMotionHandler(x,y):
    global mouseDown,xrot,yrot,xdiff,ydiff

    if mouseDown:
        yrot=x-xdiff
        xrot=y+ydiff
        glutPostRedisplay()
    return()

stopDraw=False
def closeWindow():
    global stopDraw
    stopDraw=True

def keyPressed(*args):
    # If escape is pressed, kill everything.
    global cube,xrot,yrot,xdiff,ydiff,sideRot
    key = args[0]
    if key in [ESCAPE,b'q']:
        sys.exit()
        #glutLeaveMainLoop()
        return()
    elif key == b'c':
        cube=Rcube()
    elif key == b'0':
        cube.replayLevel=0
    elif key == b'1':
        cube.replayLevel=1
    elif key == b'2':
        cube.replayLevel=2
    elif key == b'3':
        cube.replayLevel=3
    elif key == b'u':
        drawRotatingSide(0,1,1,.2)
        cube.rotateSide(0,1)
    elif key == b'f':
        drawRotatingSide(1,1,1,.2)
        cube.rotateSide(1,1)
    elif key == b'r':
        drawRotatingSide(2,1,1,.2)
        cube.rotateSide(2,1)
    elif key == b'b':
        drawRotatingSide(3,1,1,.2)
        cube.rotateSide(3,1)
    elif key == b'l':
        drawRotatingSide(4,1,1,.2)
        cube.rotateSide(4,1)
    elif key == b'd':
        drawRotatingSide(5,1,1,.2)
        cube.rotateSide(5,1)
    elif key == b'p':
        cube.replayLevel=2
    elif key==b'x':
        cube=Rcube.mkRandom()
        #print(repr(cube.facetLoc))
    #print("ASM",key,LEVEL)
    #CUBE,status,phase=applySavedMoves(CUBE,LEVEL)    
    elif key==b's':
        replayLevel=cube.replayLevel
        cube=Rcube(cube.facetLoc)
        icube=copy.deepcopy(cube.facetLoc)
        cube,*_=PetrusSolver.PetrusSolve(cube)
        cube.printTurns()
        if replayLevel!=3:
            if replayLevel==0:turns=cube.collapseTurns()
            else: turns=np.copy(cube.redTurns)
            phases = np.copy(cube.phase)
            cube=Rcube(icube)
            for i,turn in enumerate(turns):
                if replayLevel==0: sl=turn[2]
                else: sl=1
                if i in phases and replayLevel==1: 
                    drawCube()
                    time.sleep(2)
                drawRotatingSide(turn[0],turn[1],sl,.2)
                cube.rotateSide(turn[0],turn[1],sl)
                if replayLevel==-1:
                    drawCube()
                    time.sleep(1)
    elif key==b'?':
        print(helpText )
    elif key==b'z':
        while True:
            cube=Rcube.mkRandom()            
            drawCube()
            icube=copy.deepcopy(cube.facetLoc)
            cube,*_=PetrusSolver.PetrusSolve(cube)
            if cube.replayLevel==0:turns=np.copy(cube.turns)
            else: turns=np.copy(cube.redTurns)
            cube=Rcube(icube)
#             lt=len(turns)
            for i,turn in enumerate(turns):
#                 yrot=45+360*(i+1)/lt
#                 xrot=30+360*(i+1)/lt
                if cube.replayLevel==0: sl=turn[2]
                else: sl=1
                drawRotatingSide(turn[0],turn[1],sl,.3)
                cube.rotateSide(turn[0],turn[1],sl)
            sideRot=(0,0,0)
            drawCube()
            time.sleep(1)
    sideRot=(0,0,0)
    drawCube()
    
def drawFacet(color):
    foff = FACET_SIZE/2
    glBegin(GL_QUADS)            # Start Drawing The Cube
    glColor3f(*color)    # color for top.  sides and back are black
    glVertex3f( -foff, -foff,SPACE)  
    glVertex3f( foff, -foff,SPACE)  
    glVertex3f( foff, foff,SPACE)  
    glVertex3f( -foff, foff,SPACE)  

    glColor3f(0.,0.,0.)  # back and sides are black
    glVertex3f( -foff, -foff,-SPACE)  # left side
    glVertex3f( -foff, -foff,SPACE)  
    glVertex3f( -foff, foff,SPACE)  
    glVertex3f( -foff, foff,-SPACE)  

    glVertex3f( foff, -foff,-SPACE)  # right side
    glVertex3f( foff, -foff,SPACE)  
    glVertex3f( foff, foff,SPACE)  
    glVertex3f( foff, foff,-SPACE)  
    
    glVertex3f( -foff, foff,-SPACE)  # top side
    glVertex3f( -foff, foff,SPACE)  
    glVertex3f( foff, foff,SPACE)  
    glVertex3f( foff, foff,-SPACE)  
    
    glVertex3f( -foff,-foff,-SPACE)  # bottom side
    glVertex3f( -foff,-foff,SPACE)  
    glVertex3f( foff,-foff,SPACE)  
    glVertex3f( foff,-foff,-SPACE)  

    glVertex3f( -foff, -foff,-SPACE) # back  
    glVertex3f( foff, -foff,-SPACE)  
    glVertex3f( foff, foff,-SPACE)  
    glVertex3f( -foff, foff,-SPACE)  
    glEnd()

def drawRotatingSide(side,amt,slices,speed):
    global cube,sideRot
    steps=10
    rot=[0.,90.,180.,-90.][amt%4]
    for i in range(steps):
        sideRot=(side,rot*i/steps,slices)
        drawCube()
#         time.sleep(speed/steps)
    
def drawCube():
    global cube
    global sideRot
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);    # Clear The Screen And The Depth Buffer

    glLoadIdentity()                   # Reset The View
    glTranslatef(0.,0.,-10.)
    glRotatef(xrot,1.,0.,0.)
    glRotatef(yrot,0.,1.,0.)
    gt = [3,.5,-.5,-3][sideRot[2]]
    for i in range(6):
        for j in range(9):
            facet=cube.facetAtLoc[i,j] 
            '''
            if facet in [(2,2),(2,3)]:
                fcolor=3
            elif facet in [(1,4),(1,5)]:
                fcolor=4
            else: fcolor=1
            '''
            fcolor=Rcube.facetColors[facet]
            if fcolor>=0:
                rawxyz=Rcube.spos2adr((i,j)).astype(float)
                xyz=np.copy(rawxyz)
                for j in range(3):
                    if abs(xyz[j]) == 1:
                        xyz[j]=np.sign(xyz[j])*CUBE_SIZE/3
                    elif abs(xyz[j]) ==2:
                        xyz[j]=np.sign(xyz[j])*CUBE_SIZE/2
                        if j==0:
                            angle=np.sign(xyz[j])*90
                            rots=[0,1,0]
                        elif j==1:
                            angle=90+np.sign(xyz[j])*90
                            rots=[1,0,0]
                        else:
                            angle=-np.sign(xyz[j])*90
                            rots=[1,0,0]
                #print("drawing facet",i,angle,rots,xyz)
                sideAngle=0
                arots=[1,0,0]
                if sideRot[2]!=0 and sideRot[1]!=0:
                    axis=[2,1,0,1,0,2][sideRot[0]]
                    if sideRot[0] in [0,5]:
                        arots=[0,1,0]
                    elif sideRot[0] in [1,3]:
                        arots=[0,0,1]
                    else:
                        arots=[1,0,0]
                    sideSign=[1,-1,1,1,-1,-1][sideRot[0]]
                    rotSign=[-1,-1,-1,1,1,1][sideRot[0]]
                    if sideSign*rawxyz[axis]>gt:
                        sideAngle=rotSign*sideRot[1]
                        #print("sideRot",i,j,axis,rawxyz[axis],sideAngle)
                glRotate(sideAngle,arots[0],arots[1],arots[2])
                glTranslate(xyz[0],xyz[2],-xyz[1])
                glRotate(angle,rots[0],rots[1],rots[2])
                drawFacet(colorToRGB[fcolor])        
                glRotate(-angle,rots[0],rots[1],rots[2])
                glTranslate(-xyz[0],-xyz[2],xyz[1])
                glRotate(-sideAngle,arots[0],arots[1],arots[2])
    glutSwapBuffers()
    
 
def drawRubik(thisCube,text=helpText,x=2560,y=0):
    global window,cube,stopDraw,sideRot
    stopDraw=False
    glutInit(sys.argv)
    cube=thisCube
    sideRot=(0,0,0)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    #glutInitWindowSize(640, 480)
    glutInitWindowSize(400,300)
    glutInitWindowPosition(x, y)
    window = glutCreateWindow(b"Bob's Rubik")
    glutDisplayFunc(drawCube)
    glutMouseFunc(mouseButtonHandler)
    glutMotionFunc(mouseMotionHandler)
    glutWMCloseFunc(closeWindow) 
    glutReshapeFunc(ReSizeGLScene)
    glutKeyboardFunc(keyPressed)
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION) 
    #glutSetOption(GLUT_ACTION_GLUTMAINLOOP_RETURNS, GLUT_ACTION_CONTINUE_EXECUTION) 
    InitGL(640, 480)
    print(text)
    while not stopDraw:
        glutMainLoopEvent()
    #glutMainLoop()

if __name__ == '__main__':
    global cube
    cube=Rcube()
    drawRubik(cube)
