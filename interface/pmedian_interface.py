#!/usr/bin/python

import cgi, cgitb
import json
import GISOps
import numpy as np
from scipy.spatial.distance import cdist
from ortools.linear_solver import pywraplp

def main():
    readJSONandSolve()

def readJSONandSolve():
    p = read_problem(receivedMarkerData)
    RunAllPMedianExampleCppStyleAPI(p)

def read_problem(file):
    global numFacilities
    global facilityIDs
    global forcedFacilities
    global numForced
    global numDemands
    global demandIDs
    global demandPop
    global js

    try:
      js = json.loads(file) # Convert the string into a JSON Object
    except IOError:
      print "unable to read file"

    # if the geoJSON includes a p value, use this rather than any input arguments
    try:
        p = js['properties']['pValue']
    except IOError:
        print "geoJSON has no pValue"

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
            forcedFacilities.append(rowID)
        rowID += 1

    numFacilities = len(facilityIDs)
    numDemands = len(demandIDs)
    numForced = len(forcedFacilities)

    demandPop = [js['features'][i]['properties']['pop'] for i in demandIDs]

    # check if valid for the given p
    try:
        if numForced > p:
            raise DataError('numForcedGreaterThanP')
    except DataError:
        print 'number of forced facilities is greater than p'
        raise
    return p

def RunAllPMedianExampleCppStyleAPI(p):
    if hasattr(pywraplp.Solver, 'CBC_MIXED_INTEGER_PROGRAMMING'):
        RunPMedianExampleCppStyleAPI(pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING, p)


def RunPMedianExampleCppStyleAPI(optimization_problem_type, p):
    """solve a standard formulation p-median problem"""
    solver = pywraplp.Solver('RunIntegerExampleCppStyleAPI',
                           optimization_problem_type)

    # 1 if demand i is served by facility j
    X = [[None for j in range(numFacilities)] for i in range(numDemands)]
    # 1 if facility at site j is located
    Y = [None]*numFacilities

    PreComputeDistances()

    BuildModel(solver, X, Y, p)
    SolveModel(solver, X, Y, p)
    
    generateGEOJSON(X, Y, p, solver.Objective().Value())
    return 1

def PreComputeDistances():

    #declare a couple variables
    global dSort
    global d

    # Convert Coordinates from Lat/Long to CONUS EqD Projection
    xyPointArray = GISOps.GetCONUSeqDprojCoords(js)

    A = [xyPointArray[i][:] for i in demandIDs]
    B = [xyPointArray[j][:] for j in facilityIDs]

    d = cdist(A, B,'euclidean')
    return 1

def BuildModel(solver, X, Y, p):

    infinity = solver.infinity()

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
        Y[j] = solver.BoolVar('Y_%d' % j)
        # set coefficients of the Y variables in constraint 3
        c3.SetCoefficient(Y[j], 1)

    for i in range(numDemands):

        # initialize c1 equality constraints = 1
        c1[i] = solver.Constraint(1, 1)

        for j in range(numFacilities):

            # initialize the X assignment variables and add them to the objective function
            X[i][j] = solver.BoolVar('X_%d,%d' % (i,j))
            objective.SetCoefficient(X[i][j], demandPop[i]*d[i,j])

            # set the variable coefficients of the sum(Xij) = 1 for each i
            c1[i].SetCoefficient(X[i][j], 1)

            # Yj - Xij >= 0 <--- canonical form of the assignment constraint
            c2[i*numFacilities+j] = solver.Constraint(0, infinity) # c2 rhs
            c2[i*numFacilities+j].SetCoefficient(X[i][j], -1)
            c2[i*numFacilities+j].SetCoefficient(Y[j], 1)
    return 1


def SolveModel(solver, X, Y, p):
    """Solve the problem"""
    result_status = solver.Solve()

    # The problem has an optimal solution.
    assert result_status == pywraplp.Solver.OPTIMAL, "The problem does not have an optimal solution!"

    # The solution looks legit (when using solvers others than
    # GLOP_LINEAR_PROGRAMMING, verifying the solution is highly recommended!).
    assert solver.VerifySolution(1e-7, True)
    return 1


def generateGEOJSON(X, Y, p, solution):

    for j in range(numFacilities):
        located = Y[j].SolutionValue()
        js['features'][facilityIDs[j]]['properties']['facilityLocated'] = located

    for i in range(numDemands):
        for j in range(numFacilities):
            if (X[i][j].SolutionValue() == True):
                js['features'][demandIDs[i]]['properties']['assignedTo'] = facilityIDs[j]
                break
    
    # update objective value
    js['properties']['objectiveWeightedDistance'] = solution
    
    return 1




    
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
