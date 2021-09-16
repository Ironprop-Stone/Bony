from generate_dataset import *

MAX_TIMES = 5
NAME_HEAD = 'more_ll_'

if __name__ == '__main__':
    bench_folder = './large_100k/'
    output_log = open('./large_100k.log', 'w')

    for i in range(MAX_TIMES):
        bench_name = NAME_HEAD + str(i).zfill(2)
        filename = bench_folder + bench_name + '.bench'
        print('Try to generate circuit {}'.format(bench_name + '.bench'))
    
        circuit_info = generate_circuit(bench_name, filename)
        output_log.write(circuit_info)

    output_log.close()
