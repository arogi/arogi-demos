#!/usr/bin/python

import cgi, cgitb
import json
import GISOps
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
    
    # Temporary Array will hold the rowID of each feature in the JSON object
    temp = []
    rowID = 0
    
    # typeFD = Field Codes Represent:
    #  1 = demand only
    #  2 = potential facility only
    #  3 = both demand and potential facility
    for element in js['features']:
        
        # to create a dictionary of pointID and row number
        temp.append((element['properties']['pointID'],rowID))
        rowID += 1
        
        if element['properties']['typeFD']==3: # Both Facility/Demand
            facilityIDs.append(element['properties']['pointID'])
            demandIDs.append(element['properties']['pointID'])
            demandTotal += element['properties']['pop']
            element['properties']['fillColor'] = '#46A346'
        elif element['properties']['typeFD']==2: # Facility Site Only
            facilityIDs.append(element['properties']['pointID'])
            element['properties']['fillColor'] = '#FDBC43'
        elif element['properties']['typeFD']==1: # Demand Point Only
            demandIDs.append(element['properties']['pointID'])
            demandTotal += element['properties']['pop']
            element['properties']['fillColor'] = '#6198FD'

    # print(facilityIDs)
    # print(demandIDs)
    # print(demandTotal)

    js['properties']['demandTotal'] = demandTotal

    numSites = len(facilityIDs)
    numDemands = len(demandIDs)

    siteArray = [[None for k in range(4)] for j in range(numSites)]
    demandArray = [[None for k in range(4)] for j in range(numDemands)]

    i = 0
    j = 0
    k = 0
    for line in js['features']:
      if line['properties']['typeFD']>=2:
        siteArray[i][0] = line['properties']['pointID']
        siteArray[i][1] = xyPointArray[k][0]
        siteArray[i][2] = xyPointArray[k][1]
        siteArray[i][3] = line['properties']['forcedLocation']
        i += 1
      if line['properties']['typeFD'] % 2 == 1:
        demandArray[j][0] = line['properties']['pointID']
        demandArray[j][1] = xyPointArray[k][0]
        demandArray[j][2] = xyPointArray[k][1]
        demandArray[j][3] = line['properties']['pop']
        j += 1
      k += 1
    numForced = sum(zip(*siteArray)[3])
    # check if valid for the given p
    try:
      if numForced > p:
        raise DataError('numForcedGreaterThanP')
    except DataError:
      print 'number of forced facilities is greater than p'
      raise
    
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

    # instantiate distance matrix
    d = [[0. for i in range(numSites)] for j in range(numDemands)]
    # instantiate neighborhood (coverage) matrix
    N = [[0 for i in range(numSites)] for j in range(numDemands)]
    # Determine neighborhood of sites within SD of each other
    for j in range(numSites):
        for i in range(numDemands):
            d[i][j] = ((siteArray[j][1]-demandArray[i][1])**2 + (siteArray[j][2]-demandArray[i][2])**2)**0.5
            if d[i][j] <= SD:
                N[i][j] = 1


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
        # initialize the X variables as Binary Integer (Boolean) variables
        name = "X,%d" % facilityIDs[j]
        X[j] = solver.BoolVar(name)
        c2.SetCoefficient(X[j],1)
        if siteArray[j][3] == 1:
          c3[k] = solver.Constraint(1,1)
          c3[k].SetCoefficient(X[j],1)
          k += 1

    for i in range(numDemands):
        name = "Y,%d" % demandIDs[i]
        # initialize the Y variables as Binary Integer (Boolean) variables
        Y[i] = solver.BoolVar(name)
        # Set the Objective Coefficients for the population * Demand Variable (Yi)
        objective.SetCoefficient(Y[i],demandArray[i][3])

        c1[i] = solver.Constraint(1, solver.infinity())
        c1[i].SetCoefficient(Y[i],1)
        for j in range(numSites):
            if N[i][j] == 1:
                c1[i].SetCoefficient(X[j],1)

    #printModel = True
    if printModel:
        model = solver.ExportModelAsLpFormat(False)
        print(model)

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
    ### count = -1
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
      jsRow = jsonRowDictionary[j]
      js['features'][jsRow]['properties']['facilityLocated'] = located
      if located == 1:
        js['features'][jsRow]['properties']['fillColor'] = '#DD2727'
      count += 1

    count = 0
    for i in demandIDs:
      jsRow = jsonRowDictionary[i]
      # NOTE: it is 1 - Y[j] because Y[j] is 1 if it is NOT covered  
      covered = 1 - Y[count].SolutionValue()
      js['features'][jsRow]['properties']['covered'] = covered
      if covered == 1:
        demandCovered += js['features'][jsRow]['properties']['pop']
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
printModel = False
main()

# prepare for output... the GeoJSON should be returned as a string
transformedMarkerData = json.dumps(js)
print "Content-type:text/html\r\n\r\n"
print transformedMarkerData
