# Demo of using OpenTripPlanner and opentripplanner-jython
# Public domain

#!/usr/bin/jython
from org.opentripplanner.scripting.api import *
otp = OtpsEntryPoint.fromArgs([ "--graphs", "C:/Workspace/otp/graphs/", "--router", "san-fran", "--basePath", "C:\Workspace\otp"])

from opentripplanner import RoutingRequest, Graph
from opentripplanner.batch import BatchProcessor, PointSet

# Set the parameters for our search
r = RoutingRequest()
r.dateTime = 1412974800 # Friday, Oct. 10th, 2014, 4:00 pm CDT (doesn't matter for a walking search)
r.setModes('WALK')

# read the graph
g = Graph('graphs/','san-fran')

# read the destinations
# do this before running the batch processor, so that if there is an error reading the destinations, we don't have to wait for
# the batch processor to finish
destinations = PointSet('C:/Workspace/otp/pointsets/Point_Sets.csv')

# Link the destinations to the graph
# In theory this is done automatically, but the automatic linking happens after the searches have happened
# This shouldn't be a problem, but due to OTP bug #1577, it needs to happen before searches are run

#destinations.link(g)

# Create a BatchProcessor
b = BatchProcessor(
    graph=g,
    # What are the origins for the analysis?
    origins='E:\Transit-Casa-Alex\Input\Bus_Stops/bus stops.csv',
    # What are the parameters for the search?
    routingRequest=r,
    # This is for efficiency; we stop the algorithm running after it has found all blocks within a certain number of minutes of a grocery
    # every place in the City is surely within 60 minutes of a grocery store, I hope
    cutoffMinutes=60,
    # I have four cores but eight hyperthreading cores, and that seemed
    # to count with the old Java batch analyst
    threads=8
)

# Run the batch processor: build an SPT from each origin
b.run()

# get the results
results = b.eval(destinations)

# save the results as a csv
out = open('times.csv', 'w')

# loop over the destinations and write out geoid and time to nearest high school
out.write('geoid,time\n')

for did in xrange(len(destinations)):
    # we reconstruct the GEOID10 as for some reason it isn't picked up in properties
    geoid = '%02d%03d%06d%04d' %\
            (destinations[did].properties['STATEFP10'],
             destinations[did].properties['COUNTYFP10'],
             destinations[did].properties['TRACTCE10'],
             destinations[did].properties['BLOCKCE10'])

    # Results is of type opentripplanner.batch.Matrix
    time = min(results.getCol(did))

    # write a row
    out.write('%s,%s\n' % (geoid, time / 60.0))
