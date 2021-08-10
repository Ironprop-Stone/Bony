from bench import *
import random

MAX_TIMES = 10

if __name__ == '__main__':
    bench_folder = './random_circuits/'
    for i in range(MAX_TIMES):
        bench_name = str(i).zfill(3)
        filename = bench_folder+bench_name+'.bench'

        targetfile = open(filename, 'w')
        design = designConst()
        design.stages = random.randint(15,40)
        design.proxDepth = random.randint(5, 10)
        design.max_diff = random.randint(10, 20)

        stageModule = []
        totGates = 0
        totGates = growGraph(stageModule, design)  # grow the graph using nested lists
        designFramework(stageModule, targetfile, design)
        # print(" The total number of gates: ", totGates)
        # traverseGraph(stageModule)				 	# traverse the entire graph
        targetfile.close()

        print('Generate Circuit {}'.format(bench_name+'.bench'))

