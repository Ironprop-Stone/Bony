from generator import *
import random
import os
from parameter import *

def generate_circuit(circuit_name, filename):
    first_time = True
    circuit_info = ''
    while first_time or os.path.getsize(filename) == 0:
        first_time = False

        targetfile = open(filename, 'w')
        design = designConst()
        design.stages = random.randint(level_range[0], level_range[1])
        design.proxDepth = random.randint(connect_gap_range[0], connect_gap_range[1])
        design.max_diff = random.randint(max_diff_range[0], max_diff_range[1])
        design.max_nodes_in_stage = min_max_no_nodes_level[1]
        design.min_nodes_in_stage = min_max_no_nodes_level[0]
        design.max_tot_nodes = max_tot_nodes
        design.circuit_name = circuit_name

        stageModule = []
        totGates = 0
        totGates = growGraph(stageModule, design)  # grow the graph using nested lists
        circuit_info = designFramework(stageModule, targetfile, design)
        # print(" The total number of gates: ", totGates)
        # traverseGraph(stageModule)				 	# traverse the entire graph
        targetfile.close()
    return circuit_info

def generate_dataset(bench_folder, MAX_TIMES):
    outputfile = open('random_circuits.log', 'w')
    outputfile.close()
    for i in range(MAX_TIMES):
        bench_name = 'SAT_'+str(i).zfill(3)
        filename = bench_folder+bench_name+'.bench'
        first_time = True

        while first_time or os.path.getsize(filename) == 0:
            first_time = False
            print('Try to generate circuit {}'.format(bench_name+'.bench'))

            targetfile = open(filename, 'w')
            design = designConst()
            design.stages = random.randint(level_range[0], level_range[1])
            design.proxDepth = random.randint(connect_gap_range[0], connect_gap_range[1])
            design.max_diff = random.randint(max_diff_range[0], max_diff_range[1])
            design.max_nodes_in_stage = min_max_no_nodes_level[1]
            design.min_nodes_in_stage = min_max_no_nodes_level[0]
            design.circuit_name = bench_name

            stageModule = []
            totGates = 0
            totGates = growGraph(stageModule, design)  # grow the graph using nested lists
            designFramework(stageModule, targetfile, design)
            # print(" The total number of gates: ", totGates)
            # traverseGraph(stageModule)				 	# traverse the entire graph
            targetfile.close()


if __name__ == '__main__':
    bench_folder = './random_circuits/'
    generate_dataset(bench_folder)