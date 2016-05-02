# Copyright 2015-2016 Arogi Inc
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Antonio Medrano and Matt Niblett


"""A p-Median example that imports a JSON file problem definition and solves using
   a standard IP formulation."""

import sys
import json
import GISOps
import time
import numpy as np
from scipy.spatial.distance import cdist
from ortools.linear_solver import pywraplp

p = -1

printModel = False


def RunPMedianExampleCppStyleAPI(optimization_problem_type, p):
  """Example of simple p-median program with the C++ style API."""
  solver = pywraplp.Solver('RunIntegerExampleCppStyleAPI',
                           optimization_problem_type)
  infinity = solver.infinity()
  start_time = time.time()
  
  #declare a couple variables
  name = ''
  global d
  
  # 1 if demand i is served by facility j
  X = [[-1 for j in range(numFacilities)] for i in range(numDemands)]
  # 1 if facility at site j is located
  Y = [-1]*numFacilities
  
  A = [demandArray[i][0:2] for i in range(numDemands)]    
  B = [facilityArray[j][0:2] for j in range(numFacilities)]
  
  d = cdist(A, B,'euclidean')
  
  # DECLARE CONSTRAINTS
  # declare facility location constraints
  c1 = [None]*numDemands
  # declare allocation constraints
  c2 = [None]*(numDemands*numFacilities)
  # explicitly declare and initialize the p-facility constraint
  c3 = solver.Constraint(p,p)  # equality constraint equal to p
  
  # declare the objective
  objective = solver.Objective()
  objective.SetMinimization()
  
  # Generate the objective function and constraints
  for j in range(numFacilities):
    # initialize the Y site location variables
    name = "Y,%d" % (j+1)
    Y[j] = solver.BoolVar(name)
    # set coefficients of the Y variables in constraint 3
    c3.SetCoefficient(Y[j], 1)
  
  for i in range(numDemands):
    
    # initialize c1 equality constraints = 1
    c1[i] = solver.Constraint(1, 1)
    
    for j in range(numFacilities):
      
      # initialize the X assignment variables and add them to the objective function
      name = 'X,%d,%d' % (i+1,j+1)
      X[i][j] = solver.BoolVar(name)
      objective.SetCoefficient(X[i][j], demandArray[i][2]*d[i,j])
      
      # set the variable coefficients of the sum(Xij) = 1 for each i
      c1[i].SetCoefficient(X[i][j], 1)
      
      # Yj - Xij >= 0 <--- canonical form of the assignment constraint
      c2[i*numFacilities+j] = solver.Constraint(0, infinity) # c2 rhs
      c2[i*numFacilities+j].SetCoefficient(X[i][j], -1)
      c2[i*numFacilities+j].SetCoefficient(Y[j], 1)

  end_time = time.time()
  print("total time to set up problem: ", end_time - start_time)
  
  if printModel:
    model = solver.ExportModelAsLpFormat(False)
    print(model)
  
  SolveAndPrint(solver, X, Y, p)


def SolveAndPrint(solver, X, Y, p):
  """Solve the problem and print the solution."""
  print 'Number of variables = %d' % solver.NumVariables()
  print 'Number of constraints = %d' % solver.NumConstraints()

  result_status = solver.Solve()

  # The problem has an optimal solution.
  assert result_status == pywraplp.Solver.OPTIMAL, "The problem does not have an optimal solution!"

  # The solution looks legit (when using solvers others than
  # GLOP_LINEAR_PROGRAMMING, verifying the solution is highly recommended!).
  assert solver.VerifySolution(1e-7, True)

  print 'Problem solved in %f milliseconds' % solver.wall_time()

  # The objective value of the solution.
  print 'Optimal objective value = %f' % solver.Objective().Value()

  # print the selected sites
  print
  count = 0
  for j in facilityIDs:
    if (Y[count].SolutionValue() == True):
      print "Facility selected %d" % (js['features'][j]['properties']['pointID'])
    count += 1
      
  generateGEOJSON(X, Y, p)


def generateGEOJSON(X, Y, p):
  
  unweightedObj = 0
  weightedObj = 0
  assignment = -1
  #located = -1
  
  for j in range(numFacilities):
    located = Y[j].SolutionValue()
    js['features'][facilityIDs[j]]['properties']['facilityLocated'] = located
    #js['features'][facilityIDs[j]]['properties']['assignedTo'] = facilityIDs[j]
    
    # THIS GIVES THE WRONG OUPUT
    # for i in range(numDemands):
    #   if (X[i][j].SolutionValue() == True):
    #     print i,demandIDs[i],facilityIDs[j]
    #     js['features'][demandIDs[i]]['properties']['assignedTo'] = facilityIDs[j]  
  
  for i in range(numDemands):
      for j in range(numFacilities):
        if (X[i][j].SolutionValue() == True):
          #print i,demandIDs[i],facilityIDs[j], demandArray[i][2]*d[i,j]
          js['features'][demandIDs[i]]['properties']['assignedTo'] = facilityIDs[j]
  
  #print demandIDs  
  writeToGJSFile(js, p)
        
  
def writeToGJSFile(js, p):
    
  with open('./data/PMedianResult_s%d_p%d.json' % (numFeatures, p), 'w') as outfile:
    json.dump(js,outfile)


def Announce(solver, api_type):
  print ('---- Integer programming example with ' + solver + ' (' +
         api_type + ') -----')


def RunAllPMedianExampleCppStyleAPI(p):
  if hasattr(pywraplp.Solver, 'GLPK_MIXED_INTEGER_PROGRAMMING'):
    Announce('GLPK', 'C++ style API')
    RunPMedianExampleCppStyleAPI(pywraplp.Solver.GLPK_MIXED_INTEGER_PROGRAMMING, p)
  if hasattr(pywraplp.Solver, 'CBC_MIXED_INTEGER_PROGRAMMING'):
    Announce('CBC', 'C++ style API')
    RunPMedianExampleCppStyleAPI(pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING, p)
  if hasattr(pywraplp.Solver, 'SCIP_MIXED_INTEGER_PROGRAMMING'):
    Announce('SCIP', 'C++ style API')
    RunPMedianExampleCppStyleAPI(pywraplp.Solver.SCIP_MIXED_INTEGER_PROGRAMMING, p)

#
# Read a problem instance from a file
#
def read_problem(file, p, readType):
  global numFeatures
  global numFacilities
  global facilityIDs
  global facilityArray
  global numForced
  global numDemands
  global demandIDs
  global demandArray
  global js
  global jsonRowDictionary
  
  if readType == 1:
    print 'Reading JSON String Object'
    js = json.loads(file)
  elif readType == 2:
    print 'readFile({0})'.format(file)
    with open(file,"r") as f:
      js = json.load(f)
  else:
    print "READ TYPE ERROR!!"

  numFeatures = len(js['features'])

  # if the geoJSON includes a p value, use this rather than any input arguments
  try:
    p = js['properties']['pValue']
  except IOError:
    print "geoJSON has no pValue"
  
  xyPointArray = [[None for k in range(2)] for j in range(numFeatures)]
  xyPointArray = GISOps.GetCONUSeqDprojCoords(js) # Get the Distance Coordinates in CONUS EqD Projection

  facilityIDs = []
  demandIDs = []
  
  # rowID holds the index of each feature in the JSON object
  rowID = 0
  
  # typeFD = Field Codes Represent:
  #  1 = demand only
  #  2 = potential facility only
  #  3 = both demand and potential facility
  for element in js['features']:      
            
      if element['properties']['typeFD']==3: # Both Facility/Demand
          facilityIDs.append(rowID)
          demandIDs.append(rowID)
      elif element['properties']['typeFD']==2: # Facility Site Only
          facilityIDs.append(rowID)
      elif element['properties']['typeFD']==1: # Demand Point Only
          demandIDs.append(rowID)
      rowID += 1
    
  numFacilities = len(facilityIDs)
  numDemands = len(demandIDs)

  print("Number of Facilities: {0}".format(numFacilities))
  print('Number of Demands: {0}'.format(numDemands))
  
  facilityArray = [[None for k in range(3)] for j in range(numFacilities)]
  demandArray = [[None for k in range(3)] for j in range(numDemands)]
  
  i = 0
  j = 0
  k = 0
  for line in js['features']:
    if line['properties']['typeFD']>=2:
      facilityArray[i][0] = xyPointArray[k][0]
      facilityArray[i][1] = xyPointArray[k][1]
      facilityArray[i][2] = line['properties']['forcedLocation']
      i += 1
    if line['properties']['typeFD'] % 2 == 1:
      demandArray[j][0] = xyPointArray[k][0]
      demandArray[j][1] = xyPointArray[k][1]
      demandArray[j][2] = line['properties']['pop']
      j += 1
    k += 1
  
  numForced = sum(zip(*facilityArray)[2])
  # check if valid for the given p
  try:
    if numForced > p:
      raise DataError('numForcedGreaterThanP')
  except DataError:
    print 'number of forced facilities is greater than p'
    raise
  
  print 'Finished Reading the Data!'
  return p

    
def readJSONstrObjANDsolve(jsonStrObj,p):
  readType = 1
  
  p = read_problem(jsonStrObj, p, readType)
  main(p)
  return js

def main(p):
  print "Setting up and solving problem!"
  RunAllPMedianExampleCppStyleAPI(p)
  if js != None:
    return js
  else:
    print 'YOU ARE DUMB! You should be using exception handling!'
    return None

if __name__ == '__main__':
  readType = 2
  
  if len(sys.argv) > 2:
    p = float(sys.argv[1])
    file = sys.argv[2]
    print "Problem instance from", file
    p = read_problem(file)
    main(p)
  elif len(sys.argv) > 1:
    p = float(sys.argv[1])
    main(p)
  else:
    main(None)
