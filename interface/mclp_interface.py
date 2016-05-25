#!/usr/bin/python

import cgi, cgitb
import json
import GISOps
import numpy as np
from scipy.spatial.distance import cdist
from ortools.linear_solver import pywraplp


def main():
    ReadJSONandSolve()


def ReadJSONandSolve():
    [p,SD] = read_problem(receivedMarkerData)
    RunCBCMCLPexampleCppStyleAPI(p, SD)


def read_problem(file):
    global numSites
    global numFeatures
    global numDemands
    global numForced
    global facilityIDs
    global forcedFacilities
    global demandIDs
    global demandPop
    global js
    global demandTotal
    
    try:
        js = json.loads(file)
    except IOError:
        print 'Error reading file'
    
    numFeatures = len(js['features'])
    
    # if the geoJSON includes p and SD values, use these rather than any input arguments
    try:
        p = js['properties']['pValue']
    except ValueError:
        p = 3
        print "no p-value exists, using p = 3 instead"

    try:
        SD = js['properties']['distanceValue']*1000
    except ValueError:
        SD = 2000
        print "no SD-value exists, using SD = 2 km instead"


    facilityIDs = []
    demandIDs = []
    forcedFacilities = []

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
        if element['properties']['forcedLocation'] == 1:
            forcedFacilities.append(len(facilityIDs)-1)
        rowID += 1

    numSites = len(facilityIDs)
    numDemands = len(demandIDs)
    numForced = len(forcedFacilities)

    demandPop = [js['features'][i]['properties']['pop'] for i in demandIDs]

    demandTotal = sum(demandPop)
    js['properties']['demandTotal'] = demandTotal

    # check if valid for the given p
    try:
      if numForced > p:
        raise DataError('numForcedGreaterThanP')
    except DataError:
      print 'number of forced facilities is greater than p'
      raise
    
    return [p, SD]
    

def RunCBCMCLPexampleCppStyleAPI(p, SD):
  if hasattr(pywraplp.Solver, 'CBC_MIXED_INTEGER_PROGRAMMING'):
    ###Announce('CBC', 'C++ style API')
    RunMCLPexampleCppStyleAPI(pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING, p, SD)
    return 0


def RunMCLPexampleCppStyleAPI(optimization_problem_type, p, SD):
    """ Example of simple MCLP program with the C++ style API."""
    solver = pywraplp.Solver('RunIntegerExampleCppStyleAPI', optimization_problem_type)
    
    # Create a global version of:
    # Facility Site Variable X
    X = [None] * numSites

    # Coverage Variable Y  - NOTE!!: Matt used the Minimization form where:
    # Y = 1 if it is NOT COVERED by a facility located within SD of demand Yi
    Y = [None] * numDemands

    computeCoverageMatrix(SD)

    BuildModel(solver, X, Y, p)
    SolveModel(solver)

    demandCovered = demandTotal - solver.Objective().Value()

    generateGEOJSON(X, Y, demandCovered)
    return 0


def BuildModel(solver, X, Y, p):
    
    infinity = solver.infinity()
    
    # DECLARE CONSTRAINTS:
    # declare demand coverage constraints (binary integer: 1 if UNCOVERED, 0 if COVERED)
    c1 = [None]*numDemands
    
    # Explicitly declare and initialize the p-facility constraint
    c2 = solver.Constraint(p,p) # equality constraint equal to p
    
    # declare the forced facility location constraints
    c3 = [None]*numForced
    
    # declare the objective
    objective = solver.Objective()
    objective.SetMinimization()
    
    # Add potential facility sites to the p constraint
    for j in range(numSites):
        # initialize the X variables as Binary Integer (Boolean) variables
        name = "X,%d" % facilityIDs[j]
        X[j] = solver.BoolVar(name)
        c2.SetCoefficient(X[j],1)
    
    # if facility is fixed into the solution, add a constraint to make it so
    for k in range(numForced):
          c3[k] = solver.Constraint(1,1)
          c3[k].SetCoefficient(X[forcedFacilities[k]],1)
    
    # add demands to the objective and coverage constraints
    for i in range(numDemands):
        name = "Y,%d" % demandIDs[i]
        # initialize the Y variables as Binary Integer (Boolean) variables
        Y[i] = solver.BoolVar(name)
        # Set the Objective Coefficients for the population * Demand Variable (Yi)
        objective.SetCoefficient(Y[i],demandPop[i])
        # Covering constraints
        c1[i] = solver.Constraint(1, solver.infinity())
        c1[i].SetCoefficient(Y[i],1)

    # add facility coverages to the coverage constraints
    for k in range(Nsize):
        c1[Nrows[k]].SetCoefficient(X[Ncols[k]],1)
    
    return 0


def computeCoverageMatrix(SD):
        
    #declare a couple variables
    global Nrows
    global Ncols
    global Nsize
    
    SDsquared = SD*SD
    
    # Convert Coordinates from Lat/Long to CONUS EqD Projection
    xyPointArray = GISOps.GetCONUSeqDprojCoords(js)
    A = [xyPointArray[i][:] for i in demandIDs]
    B = [xyPointArray[j][:] for j in facilityIDs]
    
    # Determine neighborhood of sites within SD of each other
    Nrows,Ncols = np.nonzero(((cdist(A, B,'sqeuclidean') <= SDsquared).astype(bool)))
    Nsize = len(Nrows)

    return 0

def SolveModel(solver):
  """Solve the problem and print the solution."""
  result_status = solver.Solve()

  # The problem has an optimal solution.
  assert result_status == pywraplp.Solver.OPTIMAL, "The problem does not have an optimal solution!"

  # The solution looks legit (when using solvers others than
  # GLOP_LINEAR_PROGRAMMING, verifying the solution is highly recommended!).
  assert solver.VerifySolution(1e-7, True)
                

def generateGEOJSON(X, Y, demandCovered):
  
  count = 0
  for j in facilityIDs:
    located = X[count].SolutionValue()
    js['features'][j]['properties']['facilityLocated'] = located
    count += 1
  
  count = 0
  for i in demandIDs:
    # NOTE: it is 1 - Y[j] because Y[j] is 1 if it is NOT covered
    covered = 1 - Y[count].SolutionValue()
    js['features'][i]['properties']['covered'] = covered
    count += 1
  
  js['properties']['demandCovered'] = demandCovered
  js['properties']['efficacyPercentage'] = float(demandCovered) / demandTotal
  




###########################################################
##################### The main controller code starts here.
###########################################################

# Create instance of FieldStorage and get data
form = cgi.FieldStorage()
receivedMarkerData = form.getvalue('useTheseMarkers')
## convert the received json string into a Python object
#receivedGeoJson = json.loads(receivedMarkerData)

# the magic happens here...
main()

# prepare for output... the GeoJSON should be returned as a string
transformedMarkerData = json.dumps(js)
print "Content-type:text/html\r\n\r\n"
print transformedMarkerData
