from bench import *
import random
from generate_dataset import *
import os

def supply():
    bench_folder = './random_circuits/'
    flag = True
    while flag:
        flag = False
        for i in range(MAX_TIMES):
            bench_name = str(i).zfill(3)
            filename = bench_folder + bench_name + '.bench'
            print('Try to generate circuit {}'.format(bench_name + '.bench'))

            if not os.path.getsize(filename):
                flag = True
                targetfile = open(filename, 'w')
                design = designConst()
                design.stages = random.randint(level_range[0], level_range[1])
                design.proxDepth = random.randint(connect_gap_range[0], connect_gap_range[1])
                design.max_diff = random.randint(max_diff_range[0], max_diff_range[1])
                design.circuit_name = bench_name

                stageModule = []
                totGates = 0
                totGates = growGraph(stageModule, design)  # grow the graph using nested lists
                designFramework(stageModule, targetfile, design)
                # print(" The total number of gates: ", totGates)
                # traverseGraph(stageModule)				 	# traverse the entire graph
                targetfile.close()

if __name__ == '__main__':
    supply()