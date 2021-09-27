from os import name, replace
import sys
import re
import glob
import platform
from union_find import UnionFind

name2idx = {}
allGateVec = []

class Gate:
    def __init__(self, gate_name):
        self.gate_name = gate_name
        self.gate_type = ''
        self.pre_list = []
        self.enable = False

def new_gate(gate_name):
    gate_inst = Gate(gate_name)
    allGateVec.append(gate_inst)

def find_keys_list(name_list, find_keys):
    res = []
    for idx, ele in enumerate(name_list):
        if ele == find_keys[0]:
            res.append(name_list[idx+1])
            find_keys.pop(0)
            if len(find_keys) == 0:
                break
    return res

def is_const(gate_name):
    if name2idx['1\'h0'] == name2idx[gate_name] or name2idx['1\'h1'] == name2idx[gate_name]:
        return True
    else:
        return False
    
def convert_verilog_bench(verilog_file, bench_file):
    v_file = open(verilog_file, 'r')
    v_lineList = v_file.readlines()
    proc_v_lineList = []
    b_file = open(bench_file, 'w')
    node_cnt = 0
    line_idx = 0

    name2idx.clear()
    allGateVec.clear()

    # Process content
    new_gate('1\'h0')
    name2idx['1\'h0'] = len(name2idx)
    node_cnt += 1
    new_gate('1\'h1')
    name2idx['1\'h1'] = len(name2idx)
    node_cnt += 1
    while line_idx < len(v_lineList):
        line = v_lineList[line_idx]
        if 'wire' in line or 'output' in line or 'input' in line:
            line = line.lstrip().rstrip().replace('\n', '').replace(';', '')
            text = line.split(' ')[-1]
            new_gate(text)
            name2idx[text] = len(name2idx)
            proc_v_lineList.append(line)
            node_cnt += 1
        elif 'NOT' in line or 'AND' in line or 'BUF' in line or 'OR' in line:
            new_line = ''
            while not ';' in line:
                line = line.lstrip().rstrip().replace('\n', '')
                new_line += line
                line_idx += 1
                line = v_lineList[line_idx]
            line = line.lstrip().rstrip().replace('\n', '')
            new_line += line
            proc_v_lineList.append(new_line)
        elif 'assign' in line:
            line = line.lstrip().rstrip().replace('\n', '').replace(';', '')
            proc_v_lineList.append(line)
        line_idx += 1

    # Connection        
    uf = UnionFind(node_cnt)
    for line in proc_v_lineList:
        if 'assign' in line:
            line = line.split(' ')
            src_name = line[1]
            dst_name = line[3]
            uf.union(name2idx[src_name], name2idx[dst_name])
        elif 'BUF' in line:
            gate_type = line.split(' ')[0]
            line = line.replace(',', '').replace(';', '')
            name_list_tmp = line.split('(')
            name_list = []
            for tmp_line in name_list_tmp:
                name_list += tmp_line.split(')')
            res = find_keys_list(name_list, ['.A', '.Y'])
            src_name = res[0]
            dst_name = res[1]
            uf.union(name2idx[src_name], name2idx[dst_name])
    tmp_name2idx = name2idx.copy()
    for gate_name in tmp_name2idx:
        name2idx[gate_name] = uf.find(tmp_name2idx[gate_name])
        allGateVec[name2idx[gate_name]].enable = True

    # New Gates
    for line in proc_v_lineList:
        if 'input' in line:
            text = line.split(' ')[-1]
            allGateVec[name2idx[text]].gate_type = 'INPUT'
        elif 'output' in line:
            text = line.split(' ')[-1]
            allGateVec[name2idx[text]].gate_type = 'OUTPUT'
        elif 'NOT' in line or 'AND' in line or 'BUF' in line or 'OR' in line:
            line = line.replace(',', '').replace(';', '')
            gate_type = line.split(' ')[0]
            name_list_tmp = line.split('(')
            name_list = []
            for tmp_line in name_list_tmp:
                name_list += tmp_line.split(')')
            if gate_type == 'NOT':
                res = find_keys_list(name_list, ['.A', '.Y'])
                src_name = res[0]
                dst_name = res[1]
                allGateVec[name2idx[dst_name]].gate_type = gate_type
                allGateVec[name2idx[dst_name]].pre_list = [name2idx[src_name]]
            elif gate_type == 'AND' or gate_type == 'OR':
                res = find_keys_list(name_list, ['.A', '.B', '.Y'])
                src_name_1 = res[0]
                src_name_2 = res[1]
                dst_name = res[2]
                allGateVec[name2idx[dst_name]].gate_type = gate_type
                allGateVec[name2idx[dst_name]].pre_list = [name2idx[src_name_1], name2idx[src_name_2]]
    
    for gate in allGateVec:
        if gate.gate_type == 'INPUT' and not is_const(gate.gate_name):
            b_file.write('INPUT({:})\n'.format(gate.gate_name))
    b_file.write('\n')
    for gate in allGateVec:
        if gate.gate_type == 'OUTPUT' and not is_const(gate.gate_name):
            b_file.write('OUTPUT({:})\n'.format(gate.gate_name))
    b_file.write('\n')

    for gate in allGateVec:
        if gate.gate_type == 'AND' or gate.gate_type == 'OR' or gate.gate_type == 'NOT':
            line = gate.gate_name + ' = ' + gate.gate_type + '('
            for pre_idx in gate.pre_list:
                if pre_idx == gate.pre_list[-1]:
                    line += allGateVec[pre_idx].gate_name + ')\n'
                else:
                    line += allGateVec[pre_idx].gate_name + ', '
            b_file.write(line)
    b_file.write('\n')

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
        
        # if name[0] != 'test_07':
        #     continue

        print('[INFO] Converting Circuit: {}'.format(name[0]))
        bench_file = './syn_bench/' + name[0] + '.bench'
        convert_verilog_bench(file, bench_file)


if __name__ == "__main__":
    # main()
    main()
