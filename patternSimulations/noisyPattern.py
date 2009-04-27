#!/usr/bin/env jython
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
import os
import random
from math import pi
import java.io

# Third party modules.
import rmlimage.io.IO as IO
import rmlimage.kernel as kernel
import rmlimage.kernel.Convolution as Convolution
import rmlimage.kernel.Kernel as Kernel
import rmlimage.kernel.Transform as Transform
import rmlimage.kernel.MathMorph as MathMorph
import rmlimage.utility

# Local modules.
import EBSDTools.crystallography.lattice as lattice
import EBSDTools.crystallography.reflectors as reflectors
import EBSDTools.mathTools.eulers as eulers
import EBSDTools.mathTools.quaternions as quaternions
import EBSDTools.patternSimulations.patternSimulations as patternSimulations
import RandomUtilities.DrawingTools.drawing as drawing

scos = lambda p, x: p[0] * cos(2*pi*p[1]*(x-p[2])) + p[3]

def stddev(thickness, normalizedIntensity):
  amplitude = (2*thickness-(thickness/5.0))/2.0
  p = [-amplitude, 0.5, 0.0, amplitude+thickness/5.0]
  x = 1.0/(normalizedIntensity*255+1.0)
  return scos(p, x)

def colorMin():
  pass

def gaussianDistribution(thickness, normalizedIntensity, intensityBackground):
  stddev = thickness / 5.0 / normalizedIntensity
  colorMin = intensityBackground - 100
  return stddev, colorMin

def noisy1():
#  #FCC
  atoms = {(0,0,0): 14,
           (0.5,0.5,0): 14,
           (0.5,0,0.5): 14,
           (0,0.5,0.5): 14}
  L = lattice.Lattice(a=5.43, b=5.43, c=5.43, alpha=pi/2, beta=pi/2, gamma=pi/2, atoms=atoms)
  R = reflectors.Reflectors(L, maxIndice=5)
  print len(R.getReflectorsList())

  angles = eulers.eulers(random.randint(0,360)/180.0*pi, random.randint(0,360)/180.0*pi, random.randint(0,360)/180.0*pi) #z
  
  qSpecimenRotation = quaternions.quaternion(1,0,0,0)
  qCrystalRotation = quaternions.eulerAnglesToQuaternion(angles)
  qTilt = quaternions.axisAngleToQuaternion(-70/180.0*pi, (1,0,0))
  qDetectorOrientation = quaternions.axisAngleToQuaternion(90/180.0*pi, (1,0,0)) * quaternions.axisAngleToQuaternion(pi, (0,0,1))
#  qDetectorOrientation = quaternions.quaternion(1,0,0,0)
  qDetectorOrientation_ = qTilt * qDetectorOrientation.conjugate() * qTilt.conjugate()
  
  qRotations = [qSpecimenRotation, qCrystalRotation, qTilt, qDetectorOrientation_]

  image = patternSimulations.drawPattern(R
                      , bandcenter=False
                      , bandedges=False
                      , bandfull=True
                      , intensityMin=128
                      , intensityMax=255
                      , intensityFunction=patternSimulations.bandColorIntensityLog
                      , gaussianFunction=gaussianDistribution
                      , intensityBackground=128
                      , patternCenterX=0.0
                      , patternCenterY=0.0
                      , detectorDistance=0.4
                      , energy=20e3
                      , numberOfReflectors=50
                      , qRotations=qRotations
                      , patternWidth=1344
                      , patternHeight=1024
                      , patternCenterVisible=False
                      , colormode=drawing.COLORMODE_GRAYSCALE)
  
  image.setFile('noisy1before.bmp')
  IO.save(image)
  
  #Apply smooth filter
  kernelsize = 11
  kernel = Kernel([1]*kernelsize**2, kernelsize, kernelsize, kernelsize**2)
  Convolution.convolve(image, kernel)
  
  #Binning
  image = Transform.binning(image, 8, 8)
  
  #Noise
  for i in range(4):
    noise = rmlimage.utility.Noise()
    noise.gaussian(image, 25.0)
    
    image.setFile('noisy1_gn%i.bmp' % (i+1))
    IO.save(image)

if __name__ == '__main__':
  noisy1()