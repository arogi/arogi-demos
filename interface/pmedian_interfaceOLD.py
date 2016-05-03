import cgi, cgitb
import json
import GISOps
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
    global facilityArray
    global numForced
    global numDemands
    global demandIDs
    global demandArray
    global js
    global jsonRowDictionary
  
    try:
        js = json.loads(file) # Convert the string into a JSON Object
    except IOError:
        print "unable to read file"

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
            
    return p

def RunAllPMedianExampleCppStyleAPI(p):
    if hasattr(pywraplp.Solver, 'GLPK_MIXED_INTEGER_PROGRAMMING'):
        RunPMedianExampleCppStyleAPI(pywraplp.Solver.GLPK_MIXED_INTEGER_PROGRAMMING, p)
    if hasattr(pywraplp.Solver, 'CBC_MIXED_INTEGER_PROGRAMMING'):
        RunPMedianExampleCppStyleAPI(pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING, p)
    if hasattr(pywraplp.Solver, 'SCIP_MIXED_INTEGER_PROGRAMMING'):
        RunPMedianExampleCppStyleAPI(pywraplp.Solver.SCIP_MIXED_INTEGER_PROGRAMMING, p)
    return 1
        
def RunPMedianExampleCppStyleAPI(optimization_problem_type, p):
  """Example of simple p-median program with the C++ style API."""
  solver = pywraplp.Solver('RunIntegerExampleCppStyleAPI',
                           optimization_problem_type)
  infinity = solver.infinity()
  
  #declare a couple variables
  name = ''
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
  
  SolveAndPrint(solver, X, Y, p)
  return 1

def SolveAndPrint(solver, X, Y, p):
  """Solve the problem and print the solution."""

  result_status = solver.Solve()

  # The problem has an optimal solution.
  assert result_status == pywraplp.Solver.OPTIMAL, "The problem does not have an optimal solution!"

  # The solution looks legit (when using solvers others than
  # GLOP_LINEAR_PROGRAMMING, verifying the solution is highly recommended!).
  assert solver.VerifySolution(1e-7, True)
      
  generateGEOJSON(X, Y, p)
  return 1


def generateGEOJSON(X, Y, p):
  
    unweightedObj = 0
    weightedObj = 0
    assignment = -1
    located = -1

    for j in range(numFacilities):
        located = Y[j].SolutionValue()
        js['features'][facilityIDs[j]]['properties']['facilityLocated'] = located
        js['features'][facilityIDs[j]]['properties']['assignedTo'] = facilityIDs[j]

    for i in range(numDemands):
          if (X[i][j].SolutionValue() == 1):        
              js['features'][demandIDs[i]]['properties']['assignedTo'] = facilityIDs[j]

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
