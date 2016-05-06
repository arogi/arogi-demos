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
    RunALLMCLPexampleCppStyleAPI(p, SD)

def read_problem(file):
    global numSites
    global numFeatures
    global numDemands
    global numForced
    global facilityIDs
    global demandIDs
    global siteArray
    global demandArray
    global js
    global demandTotal
    
    p = -1
    SD = -1
    
    # read data from string object
    ###print 'Reading JSON String Object!'
    try:
      js = json.loads(file) # Convert the string into a JSON Object
    except IOError:
      print "unable to read file"
    
    numFeatures = len(js['features'])
    
    # if the geoJSON includes p and SD values, use these rather than any input arguments
    try:
      p = js['properties']['pValue']
    except IOError:
      print "geoJSON has no pValue"
    try:
      SD = js['properties']['distanceValue']*1000
    except IOError:
      print "geoJSON has no distanceValue"
    
    xyPointArray = [[None for k in range(2)] for j in range(numFeatures)]
    xyPointArray = GISOps.GetCONUSeqDprojCoords(js) # Get the Distance Coordinates in CONUS EqD Projection
    
    facilityIDs = []
    demandIDs = []
    demandTotal = 0
    
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
            demandTotal += element['properties']['pop']
            element['properties']['fillColor'] = '#46A346'
        elif element['properties']['typeFD']==2: # Facility Site Only
            facilityIDs.append(rowID)
            element['properties']['fillColor'] = '#FDBC43'
        elif element['properties']['typeFD']==1: # Demand Point Only
            demandIDs.append(rowID)
            demandTotal += element['properties']['pop']
            element['properties']['fillColor'] = '#6198FD'
        rowID += 1
    
    numSites = len(facilityIDs)
    numDemands = len(demandIDs)
    
    siteArray = [[None for k in range(3)] for j in range(numSites)]
    demandArray = [[None for k in range(3)] for j in range(numDemands)]
    
    # assemble pertinent data for the model into multidimensional arrays
    i = 0
    j = 0
    k = 0
    for line in js['features']:
      if line['properties']['typeFD']>=2:  # Potential facility site
        siteArray[i][0] = xyPointArray[k][0]
        siteArray[i][1] = xyPointArray[k][1]
        siteArray[i][2] = line['properties']['forcedLocation']
        i += 1
      if line['properties']['typeFD'] % 2 == 1:  # Demand point
        demandArray[j][0] = xyPointArray[k][0]
        demandArray[j][1] = xyPointArray[k][1]
        demandArray[j][2] = line['properties']['pop']
        j += 1
      k += 1
    
    numForced = sum(zip(*siteArray)[2])
    demandTotal = sum(zip(*demandArray)[2])
    js['properties']['demandTotal'] = demandTotal
    
    ###print 'Finished Reading the Data!'
    return [p, SD]

def RunALLMCLPexampleCppStyleAPI(p, SD):
    if hasattr(pywraplp.Solver, 'GLPK_MIXED_INTEGER_PROGRAMMING'):
        ###Announce('GLPK', 'C++ style API')
        RunMCLPexampleCppStyleAPI(pywraplp.Solver.GLPK_MIXED_INTEGER_PROGRAMMING, p, SD)
    if hasattr(pywraplp.Solver, 'CBC_MIXED_INTEGER_PROGRAMMING'):
        ###Announce('CBC', 'C++ style API')
        RunMCLPexampleCppStyleAPI(pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING, p, SD)
    if hasattr(pywraplp.Solver, 'SCIP_MIXED_INTEGER_PROGRAMMING'):
        ###Announce('SCIP', 'C++ style API')
        RunMCLPexampleCppStyleAPI(pywraplp.Solver.SCIP_MIXED_INTEGER_PROGRAMMING, p, SD)
    return 1

def RunMCLPexampleCppStyleAPI(optimization_problem_type, p, SD):
    """ Example of simple MCLP program with the C++ style API."""
    solver = pywraplp.Solver('RunIntegerExampleCppStyleAPI', optimization_problem_type)
    infinity = solver.infinity()

    #declare a couple variables
    name = ''

    # Create a global version of:
    # Facility Site Variable X
    X = [-1] * numSites # Note, these will need to be updated if we start to consider demands/facility sites seperately

    # Coverage Variable Y  - NOTE!!: Matt used the Minimization form where:
    # Y = 1 if it is NOT COVERED by a facility located within SD of demand Yi
    Y = [-1] * numDemands # Note, these will need to be updated if we start to consider demands/facility sites seperately
    
    SDsquared = SD*SD
    
    A = [demandArray[i][0:2] for i in range(numDemands)]    
    B = [siteArray[j][0:2] for j in range(numSites)]
    
    # Determine neighborhood of sites within SD of each other
    Nrows,Ncols = np.nonzero(((cdist(A, B,'sqeuclidean') <= SDsquared).astype(bool)))
    Nsize = len(Nrows)
    
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
    
    # generate the objective function and constraints
    k = 0
    for j in range(numSites):
        # initialize the X and Y variables as Binary Integer (Boolean) variables
        name = "X,%d" % facilityIDs[j]
        X[j] = solver.BoolVar(name)
        c2.SetCoefficient(X[j],1)
        if siteArray[j][2] == 1:
          c3[k] = solver.Constraint(1,1)
          c3[k].SetCoefficient(X[j],1)
          k += 1
    
    for i in range(numDemands):
        name = "Y,%d" % demandIDs[i]
        Y[i] = solver.BoolVar(name)
        # Set the Objective Coefficients for the population * Demand Variable (Yi)
        objective.SetCoefficient(Y[i],demandArray[i][2])
        # Covering constraints
        c1[i] = solver.Constraint(1, solver.infinity())
        c1[i].SetCoefficient(Y[i],1)
    
    for k in range(Nsize):
        c1[Nrows[k]].SetCoefficient(X[Ncols[k]],1)
    
    SolveAndPrint(solver, X, Y, p, SD)
    return 1

def SolveAndPrint(solver, X, Y, p, SD):
    """Solve the problem and print the solution."""
    ###print 'Number of variables = %d' % solver.NumVariables()
    ###print 'Number of constraints = %d' % solver.NumConstraints()

    result_status = solver.Solve()

    # The problem has an optimal solution.
    assert result_status == pywraplp.Solver.OPTIMAL, "The problem does not have an optimal solution!"

    # The solution looks legit (when using solvers others than
    # GLOP_LINEAR_PROGRAMMING, verifying the solution is highly recommended!).
    assert solver.VerifySolution(1e-7, True)

    ###print 'Problem solved in %f milliseconds' % solver.wall_time()

    # The objective value of the solution.
    ###print 'Optimal objective value = %f' % solver.Objective().Value()

    # print the selected sites
    count = -1
    ### for j in facilityIDs:
    ###   count += 1
    ###   if (X[count].SolutionValue() == 1.0):
    ###     print "Site selected %d" % (j)

    generateGEOJSON(X, Y, p, SD)
    return 1


def generateGEOJSON(X, Y, p, SD):
    #global js
    #print numFeatures
    demandCovered = 0
    covered = -1
    located = -1
    count = 0
    for j in facilityIDs:
      located = X[count].SolutionValue()
      js['features'][j]['properties']['facilityLocated'] = located
      if located == 1:
        js['features'][j]['properties']['fillColor'] = '#DD2727'
      count += 1

    count = 0
    for i in demandIDs:
      covered = 1 - Y[count].SolutionValue()
      js['features'][i]['properties']['covered'] = covered
      if covered == 1:
        demandCovered += js['features'][i]['properties']['pop']
      count += 1

    js['properties']['demandCovered'] = demandCovered
    js['properties']['efficacyPercentage'] = float(demandCovered) / demandTotal

    ### As of this moment js is the output file... ready to be delivered back to
    ### as the solution
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
