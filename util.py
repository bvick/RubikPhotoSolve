'''
Created on Nov 12, 2017

@author: bob vick

a few utility functions
'''
import sys

# vnames are quoted variable names.  prints name,value of each 
def printvars(*vnames,label="",out=True):
    frame=sys._getframe(1)
    if label!="": print(label,end=" ")
    s= ""
    for v in vnames:
        s+= v+"="+str(eval(v,frame.f_globals,frame.f_locals))+" "
    if out: print(s)
    return(s)

# prints repr(v) broken at about 80 characters
def printrepr(v):
    words=iter(repr(v).split())
    current=""
    for word in words:
        if len(current)+1+len(word)>80:
            print(current)
            current=word
        else:
            current+=" "+word
    if (len(current)>0): print(current)

    
# swaps a for b and b for a, any other value unchanged
def swapab(x,a,b):
    if x in [a,b]: return(a+b-x)
    else:return(x)

def swapabcd(x,a,b,c,d):
    return(swapab(swapab(x,a,b),c,d))

# breaks list into pieces of length by (last one might be shorter)
def decat(x,by):
    a=[ ]
    for i in range(0,len(x),by):
        a.append( x[i:i+by])
    return(a)
 
 