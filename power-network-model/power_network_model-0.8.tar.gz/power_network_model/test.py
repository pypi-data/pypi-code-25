# Test script to run the power network model generator on the included Horton (2012) data
# This script will read the two .csv files contained in .../Data/ and generate the model
# It will then make a funky plot of the data

import pkg_resources
import power_network_model as PNM
import power_network_model.plotter as PNMplot

# read in transformer file, generate substation data:
trafo_filename = pkg_resources.resource_filename("power_network_model", 'Data/Horton_Input_Trafos.csv')
ss_trafos, ss_connections, ss_meta = PNM.make_substations(trafo_filename)

# Generate connections between substations:
connections_filename = pkg_resources.resource_filename("power_network_model", 'Data/Horton_Input_Connections.csv')
connections_twixt_stations = PNM.connections_adder(connections_filename, ss_meta)

# Write out the output files
filename = "Horton_Output"
nodes_output, connections_output = PNM.write_out(filename, ss_trafos, ss_connections, connections_twixt_stations)

################################################################################
# If you want to plot the output:
PNMplot.network_plotter(nodes_output, connections_output, ["red", "blue"], "Horton Model")
