from os import name, replace
import sys
import re
import glob
import platform
from union_find import UnionFind

pre_list = []
gate_type = []
name2idx = {}

def new_gate(gate_name):
    name2idx[gate_name] = len(name2idx)
    pre_list.append([])
    gate_type.append('')
    
def convert_verilog_bench(verilog_file, bench_file):
    v_file = open(verilog_file, 'r')
    v_lineList = v_file.readlines()
    proc_v_lineList = []
    b_file = open(bench_file, 'w')
    node_cnt = 0
    line_idx = 0

    while line_idx < len(v_lineList):
        line = v_lineList[line_idx]
        if 'wire' in line or 'output' in line or 'input' in line:
            text = line.lstrip().rstrip().replace('\n', '').replace(';', '')
            text = text.split(' ')[-1]
            new_gate(text)
            proc_v_lineList.append(line)
            node_cnt += 1
        if 'NOT' in line or 'AND' in line or 'BUF' in line or 'OR' in line:
            new_line = ''
            while not ';' in line:
                line = line.lstrip().rstrip().replace('\n', '')
                new_line += line
                line_idx += 1
                line = v_lineList[line_idx]
            line = line.lstrip().rstrip().replace('\n', '')
            new_line += line
            node_cnt += 1
        line_idx += 1
            
    uf = UnionFind(node_cnt)
    
        

    b_file.close()
    v_file.close()
    print("[SUCCESS] Convert {:} Done".format(verilog_file))


def main():
    # verilog_folder_1 = '../../EPFL_benchmarks/arithmetic/*.v'
    # verilog_folder_2 = '../../EPFL_benchmarks/random_control/*.v'
    # bench_folder = '../../EPFL_benchmarks/bench/'
    
    verilog_folder = './syn_verilog/*.v'
    for file in glob.glob(verilog_folder):
        if (platform.system() == 'Linux'):
            name = file.split("/")
            name = name[-1].split(".")
        else:
            name = file.split("\\")
            name = name[1].split(".")
        
        # if name[0] != 'sr_n_0003_pk2_030_pg_040_t_9_sat_1':
        #     continue

        bench_file = './syn_bench/' + name[0] + '.bench'
        convert_verilog_bench(file, bench_file)


if __name__ == "__main__":
    # main()
    main()
