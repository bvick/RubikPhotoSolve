Overview

Python 3 implementation of 3x3 Rubik's Cube solver, containing:
- solver based on Lars Petrus method with final edge solutions from Bernard Helmstetter
  Solutions to 25,000  30-random-turn configurations average 46.7 turns,
  about 1 second each on a fast PC.
- render a 3d image of a cube allowing rotations, side turns, randomization and solution
- photograph a cube and output solution steps
- Rcube class that can be used for other solution algorithms

Requirements

- to date it has only been run on a PC, but it has no PC-specific requirements,
  and I will soon be testing it on a Mac and a Raspberry Pi.
- uses Python OpenGL for rendering
- uses Python OpenCV for processing camera image
- everything else imported is pretty standard python addons: numpy, re, copy, pickle
- NB there are some known issues using OpenGL with some packaged versions of Python.  I didn't get it working with Ananconda, but it works fine with just Python 3.6 for example.

Use

If you want to solve from a picture:

Make sure you have a camera plugged into your PC
Run readRcube.py , which will prompt you to place the cube so 2 sides fit in the wireframe shown.
It will do this 3 times to get all six sides.  If it can't read a side, it will ask you again.
It is a little sensitive to lighting - shouldn't be dark but also shouldn't have glare.
After it reads the cube, you'll see a window with a picture of the cube.
Type "s" to have it solve the cube.   You'll see on the shell window the steps needed.
(I use the colors of the faces instead of UDFBLR.  There is a parameter to the printTurns() function in
Rcube module to use standard notation instead)
Note also that I'm working with an actual Rubik's cube.  If it doesn't work on your knock-off,
you may have to do some code-tweaking of the color maps. Look for colorFilters in readRcube.py, noting
that these are HSV, not the usual RGB!

If you want to just manipulate a cube picture:

Run drawRcube.py, which will give you a window with a clean cube in it.  You can reorient the cube
with a left-mouse-drag.
You can rotate a side CW with the udfblr keys. CCW rotations are 3 CW rotations, sorry.
'x' will randomize cube, and 's' will solve.
'z' will have it loop through random cube solutions. (Makes a nice screen-saver if you first maximize the window)

