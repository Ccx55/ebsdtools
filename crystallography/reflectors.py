#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe Pinard (philippe.pinard@mail.mcgill.ca)"
__version__ = ""
__date__ = ""
__copyright__ = "Copyright (c) 2008 Philippe Pinard"
__license__ = ""

# Subversion informations for the file.
__svnRevision__ = ""
__svnDate__ = ""
__svnId__ = ""

# Standard library modules.
from math import sin, cos, pi, acos, atan2, exp, sqrt
import csv
import os.path
import warnings

# Third party modules.

# Local modules.
import EBSDTools
import EBSDTools.mathTools.vectors as vectors
import EBSDTools.crystallography.reciprocal as reciprocal
import EBSDTools.crystallography.bragg as bragg
import RandomUtilities.sort.sortDict as sortDict
from EBSDTools.mathTools.mathExtras import zeroPrecision

class scatteringFactors:
  def __init__(self
               , filepath_0_2='data/elastic_atomic_scattering_factors_0_2.csv'
               , filepath_2_6='data/elastic_atomic_scattering_factors_2_6.csv'):
    
    basedir = EBSDTools.__path__[0]
    
    reader = csv.reader(open(os.path.join(basedir,filepath_0_2), 'r'))
    rows = list(reader)
    self.__read_0_2(rows[1:])
    
    reader = csv.reader(open(os.path.join(basedir,filepath_2_6), 'r'))
    rows = list(reader)
    self.__read_2_6(rows[1:])
    
  def __read_0_2(self, rows):
    self.parameters_0_2 = {}
    
    for row in rows:
      Z = int(row[0])
      self.parameters_0_2.setdefault(Z, {})
      self.parameters_0_2[Z]['a1'] = float(row[1])
      self.parameters_0_2[Z]['a2'] = float(row[2])
      self.parameters_0_2[Z]['a3'] = float(row[3])
      self.parameters_0_2[Z]['a4'] = float(row[4])
      self.parameters_0_2[Z]['a5'] = float(row[5])
      self.parameters_0_2[Z]['b1'] = float(row[6])
      self.parameters_0_2[Z]['b2'] = float(row[7])
      self.parameters_0_2[Z]['b3'] = float(row[8])
      self.parameters_0_2[Z]['b4'] = float(row[9])
      self.parameters_0_2[Z]['b5'] = float(row[10])
  
  def __read_2_6(self, rows):
    self.parameters_2_6 = {}
    
    for row in rows:
      Z = int(row[0])
      self.parameters_2_6.setdefault(Z, {})
      self.parameters_2_6[Z]['a1'] = float(row[1])
      self.parameters_2_6[Z]['a2'] = float(row[2])
      self.parameters_2_6[Z]['a3'] = float(row[3])
      self.parameters_2_6[Z]['a4'] = float(row[4])
      self.parameters_2_6[Z]['a5'] = float(row[5])
      self.parameters_2_6[Z]['b1'] = float(row[6])
      self.parameters_2_6[Z]['b2'] = float(row[7])
      self.parameters_2_6[Z]['b3'] = float(row[8])
      self.parameters_2_6[Z]['b4'] = float(row[9])
      self.parameters_2_6[Z]['b5'] = float(row[10])
  
  def getScatteringFactor(self, Z, s):
    """
      Return the scattering factor for atomic number Z and s
      s is defined as $\frac{4\pi\sin\theta}{\lambda}$
      
      The values are limited for $0 < s < 2 \AA$
      
      References:
        Prince2004
      
      Inputs:
        Z: atomic number (integer)
        s: norm of the scattering vector in $\AA$ (float)
      
      Outputs:
        a float of the scattering factor
    """
    
    #Test with x-ray scattering factor
#===============================================================================
#    a = [6.292, 3.035, 1.989, 1.541]
#    b = [2.439, 32.334, 0.678, 81.694]
#    c = 1.141
#    
#    fx = 0.0
#    
#    x = s / (4*pi)
#    
#    for i in range(4):
#      fx += a[i]*exp(-b[i]*x**2)
#    
#    fx += c
#    
#    fe = 0.023934 * (Z - fx) / x**2
#    
#    return fe
#===============================================================================
    
    
    if s >= 0 and s < 2:
      a = [self.parameters_0_2[Z]['a1'], self.parameters_0_2[Z]['a2'], self.parameters_0_2[Z]['a3'], self.parameters_0_2[Z]['a4'], self.parameters_0_2[Z]['a5']]
      b = [self.parameters_0_2[Z]['b1'], self.parameters_0_2[Z]['b2'], self.parameters_0_2[Z]['b3'], self.parameters_0_2[Z]['b4'], self.parameters_0_2[Z]['b5']]
    elif s >= 2 and s < 6:
#    elif s >= 2:
      a = [self.parameters_2_6[Z]['a1'], self.parameters_2_6[Z]['a2'], self.parameters_2_6[Z]['a3'], self.parameters_2_6[Z]['a4'], self.parameters_2_6[Z]['a5']]
      b = [self.parameters_2_6[Z]['b1'], self.parameters_2_6[Z]['b2'], self.parameters_2_6[Z]['b3'], self.parameters_2_6[Z]['b4'], self.parameters_2_6[Z]['b5']]
    else:
      warnings.warn("Outside table range of s (%e) < 6\AA" % s)
      a = [self.parameters_2_6[Z]['a1'], self.parameters_2_6[Z]['a2'], self.parameters_2_6[Z]['a3'], self.parameters_2_6[Z]['a4'], self.parameters_2_6[Z]['a5']]
      b = [self.parameters_2_6[Z]['b1'], self.parameters_2_6[Z]['b2'], self.parameters_2_6[Z]['b3'], self.parameters_2_6[Z]['b4'], self.parameters_2_6[Z]['b5']]
      
    f = 0.0
    
    for i in range(5):
      f += a[i]*exp(-b[i]*s**2)
    
    return f

class Reflectors:
  def __init__(self, L, maxIndice=2):
    self.L = L
    
    self.scatteringFactors = scatteringFactors()
    
    self._calculateReflectors(maxIndice)
    
  def _calculateReflectors(self, maxIndice):
    self.reflectors = {}
    intensities = []
    planeSpacings = []
    
    planes = self.__findReflectors(maxIndice)
    
    for plane in planes:
      planeKey = plane.toTuple()
      self.reflectors.setdefault(planeKey, {})
      
      self.reflectors[planeKey]['reflector'] = plane
      
      planeSpacing = self.__calculatePlaneSpacing(plane)
      if self.__isNewPlaneSpacing(planeSpacing, planeSpacings):
        planeSpacings.append(planeSpacing)
      self.reflectors[planeKey]['plane spacing'] = planeSpacing
      
      intensity = self.__calculateIntensity(plane, planeSpacing)
      intensities.append(intensity)
      self.reflectors[planeKey]['intensity'] = intensity
    
    if len(planes) > 0:
      intensityMax = max(intensities)
      if intensityMax > 0.0:
        for planeKey in self.reflectors.keys():
          self.reflectors[planeKey]['normalized intensity'] = self.reflectors[planeKey]['intensity'] / intensityMax
      
      planeSpacings.sort(reverse=True)
      for planeKey in self.reflectors.keys():
        family = self.__getPlaneSpacingIndex(self.reflectors[planeKey]['plane spacing'], planeSpacings)
        self.reflectors[planeKey]['family'] = family
  
  def __isNewPlaneSpacing(self, newPlaneSpacing, planeSpacings):
    inPlaneSpacing = False
    
    for existantPlaneSpacing in planeSpacings:
      if abs(existantPlaneSpacing - newPlaneSpacing) < zeroPrecision:
        inPlaneSpacing = True
        break
    
    return not inPlaneSpacing
  
  def __getPlaneSpacingIndex(self, planeSpacing, planeSpacings):
    for index, existantPlaneSpacing in enumerate(planeSpacings):
      if abs(existantPlaneSpacing - planeSpacing) < zeroPrecision:
        return index
  
  def __areEquivalentPlanes(self, plane1, plane2):
    angle = reciprocal.interplanarAngle(plane1, plane2, self.L)
    planeSpacing1 = reciprocal.planeSpacing(plane1, self.L)
    planeSpacing2 = reciprocal.planeSpacing(plane2, self.L)
    
    if angle < zeroPrecision or abs(angle - pi) < zeroPrecision:
      if abs(planeSpacing1 - planeSpacing2) < zeroPrecision:
        return True
      else:
        return False
    else:
      return False

  def __isDiffracting(self, plane):
    sum = 0
    
    atomPositions = self.L.getAtomsPositions()
    
    for atomPosition in atomPositions:
      sum += (-1)**(2*vectors.dot(plane, atomPosition))
    
    if sum > 0:
      return True
    else:
      return False

  def __findReflectors(self, maxIndice):
    reflectors = []
    
    for h in range(-maxIndice, maxIndice+1):
      for k in range(-maxIndice, maxIndice+1):
        for l in range(-maxIndice, maxIndice+1):
          plane = vectors.vector(h,k,l).positive()
          
          if not plane == vectors.vector(0,0,0): #Remove plane (0,0,0)
            if self.__isDiffracting(plane):
              for reflector in reflectors:
                if self.__areEquivalentPlanes(plane, reflector):
                  plane = vectors.vector(None)
                  break
                  
              if plane[0] != None:
                reflectors.append(plane)
    
    reflectors.sort()
    return reflectors
  
  def __calculatePlaneSpacing(self, plane):
    return reciprocal.planeSpacing(plane, self.L)
  
  def __calculateIntensity(self, plane, planeSpacing):
    sum = 0.0
    
    s = 2*pi/planeSpacing
    
    for atom in self.L.atoms:
      
      sum += (-1)**(2*vectors.dot(plane, atom)) * self.scatteringFactors.getScatteringFactor(self.L.atoms[atom], s)
    
    return sum**2
  
  def getReflectorsDict(self):
    return self.reflectors
  
  def getReflectorsList(self, sortKey='normalized intensity', reverse=True):
    """
      Return a list of reflectors sorted in decreasing order of intensity
      
      Inputs:
        sortKey: key that the reflector list will be sorted by
        reverse: True: descending order, False: ascending order
      
      Outputs:
        a list
    """
    intensityDict = {}
    for reflector in self.reflectors.keys():
      intensityDict.setdefault(reflector, self.reflectors[reflector][sortKey])
    
    sortedIntensityDict = sortDict.sortDictByValue(intensityDict, reverse=reverse)
    
    keys = []
    for item in sortedIntensityDict:
      keys.append(item[0])
    
    return keys
  
  def getReflectorsListByFamily(self, family):
    keys = []
    
    for reflector in self.reflectors.keys():
      if self.reflectors[reflector]['family'] == family:
        keys.append(self.reflectors[reflector]['reflector'])
    
    return keys
      
  
  def getReflectorInfo(self, plane):
    if plane in self.reflectors.keys():
      return self.reflectors[plane]
  
  def getReflectorFamily(self, plane):
    if plane in self.reflectors.keys():
      return self.reflectors[plane]['family']
  
  def getReflectorPlaneSpacing(self, plane):
    if plane in self.reflectors.keys():
      return self.reflectors[plane]['plane spacing']
  
  def getReflectorIntensity(self, plane):
    if plane in self.reflectors.keys():
      return self.reflectors[plane]['intensity']
  
  def getReflectorNormalizedIntensity(self, plane):
    if plane in self.reflectors.keys():
      return self.reflectors[plane]['normalized intensity']

if __name__ == '__main__':
  import EBSDTools.crystallography.lattice as lattice
  atoms = {(0,0,0): 26, 
           (0,0.5,0.5): 26,
           (0.5,0,0.5): 26,
           (0.5,0.5,0): 26}
  
  L = lattice.Lattice(a=3.59, b=3.59, c=3.59, alpha=pi/2, beta=pi/2, gamma=pi/2, atoms=atoms, reflectorsMaxIndice=4)
  
  reflectors = L.getReflectors().getReflectorsDict()
  reflectorsList = L.getReflectors().getReflectorsList(sortKey='family', reverse=False)
  
  print len(reflectorsList)
  
#  for reflector in reflectorsList:
#    print '%s, %i' % (reflector, reflectors[reflector]['family'])
#  
