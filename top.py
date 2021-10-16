from generate_dataset import *

MAX_TIMES = 2000
NAME_HEAD = 'Depth_10_20_Nodes_300_500_S0_'

if __name__ == '__main__':
    # bench_folder = './bench/'
    verilog_folder = './verilog/'
    output_log = open('./verilog.log', 'w')

    for i in range(MAX_TIMES):
        bench_name = NAME_HEAD + str(i).zfill(2)
        filename = verilog_folder + bench_name + '.v'
        print('Try to generate circuit {}'.format(bench_name + '.v'))
    
        circuit_info = generate_circuit(bench_name, filename)
        output_log.write(circuit_info)

    output_log.close()
