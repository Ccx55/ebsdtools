#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe Pinard (philippe.pinard@mail.mcgill.ca)"
__version__ = ""
__date__ = ""
__copyright__ = "Copyright (c) 2009 Philippe Pinard"
__license__ = ""

# Subversion informations for the file.
__svnRevision__ = ""
__svnDate__ = ""
__svnId__ = ""

# Standard library modules.
from math import log

# Third party modules.
#import numpy.fft
#import PIL

# Local modules.
import java.io
import EBSDTools.indexation.hough as hough
import EBSDTools.indexation.masks as masks
import EBSDTools.indexation.pattern as pattern
import rmlimage.io.IO as IO
import rmlimage.kernel.Convolution as Convolution
import rmlimage.kernel.Kernel as Kernel
import rmlimage.kernel.Transform as Transform
import rmlimage.kernel.MathMorph as MathMorph

maskMap = masks.createMaskDisc(width=168, height=128, centroid=(84,64), radius=59)
P = pattern.Pattern(filepath='c:/documents/workspace/EBSDTools/indexation/testData/pattern1.bmp', maskMap=maskMap)
H = hough.Hough(P)
H.calculateHough(angleIncrement=0.5)



#file = java.io.File('c:/documents/workspace/EBSDTools/dev/hough1(Red).bmp')
#houghMap = IO.load(file)

houghMap = H.houghMap.duplicate()

MathMorph.closing(houghMap, 1)

houghMap.setFile('c:/documents/workspace/EBSDTools/dev/hough1.bmp')
IO.save(houghMap)

k = [[0,-2,0], [1,3,1], [0,-2,0]]
k = [[-10, -15, -22, -22, -22, -22, -22, -15, -10],
     [ -1,  -6, -13, -22, -22, -22, -13,  -6,  -1],
     [  3,   6,   4,  -3, -22,  -3,   4,   6,   3],
     [  3,  11,  19,  28,  42,  28,  19,  11,   3],
     [  3,  11,  27,  42,  42,  42,  27,  11,   3],
     [  3,  11,  19,  28,  42,  28,  19,  11,   3],
     [  3,   6,   4,  -3, -22,  -3,   4,   6,   3],
     [ -1,  -6, -13, -22, -22, -22, -13,  -6,  -1],
     [-10, -15, -22, -22, -22, -22, -22, -15, -10]]

kernel = Kernel(k, 50)
Convolution.convolve(houghMap, kernel)

print houghMap

houghMap.setFile('c:/documents/workspace/EBSDTools/dev/hough1_b.bmp')
IO.save(houghMap)