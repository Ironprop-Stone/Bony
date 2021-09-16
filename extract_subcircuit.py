from benchsolver import *
import aiger
from aiger_sat import SolverWrapper
import glob
import platform

def read_simulation(prob_filename):
    f = open(prob_filename, "r")
    data = f.readlines()
    x_data_prob = []
    for data_info in data:
        if data_info == '\n':
            continue
        x_data_prob.append(float(data_info[:-1]))
    return x_data_prob

def save_subcircuit(x_data, NL, pre_list, filename):
    ori2sub = {}
    sub_cnt = 0
    new_x_data = []
    new_edge = []
    for ori_idx in NL:
        new_x_data.append(x_data[ori_idx].copy())
        ori2sub[ori_idx] = sub_cnt
        sub_cnt += 1
    for ori_idx in NL:
        for pre_ori_idx in pre_list[ori_idx]:
            new_edge.append([ori2sub[pre_ori_idx], ori2sub[ori_idx]])

    f = open('./subcircuit/'+filename+'.txt', 'w')
    for node in new_x_data:
        for n in node:
            f.write(str(n) + ":")
        f.write(";")
    f.write("\n")
    for edge in new_edge:
        f.write("(" + str(edge[0]) + "," + str(edge[1]) + ");")
    f.write("\n")
    f.close()
    print('[SUCCESS] Save UNSAT subcircuit : {}'.format(filename))

def extract_node(x_data, pre_list, level_list, bench_name):
    NL = []
    expr = []
    x_symbol = []
    for x_data_info in x_data:
        NL.append([])
        expr.append(None)
        x_symbol.append(aiger.atom(x_data_info[0]))

    # Assign symbol for PI expr
    for pi_idx in level_list[0]:
        expr[pi_idx] = x_symbol[pi_idx]
        NL[pi_idx].append(pi_idx)

    # Find expr for all nodes level by level
    for level in range(1, len(level_list), 1):
        for idx in level_list[level]:
            # find expr
            gate_type = get_gate_type_by_number(x_data[idx][1])
            if gate_type == 'AND':
                for pre_idx in pre_list[idx]:
                    if expr[idx].__sizeof__() == 16:
                        expr[idx] = (expr[pre_idx])
                    else:
                        expr[idx] &= (expr[pre_idx])
            elif gate_type == 'NAND':
                for pre_idx in pre_list[idx]:
                    if expr[idx].__sizeof__() == 16:
                        expr[idx] = (expr[pre_idx])
                    else:
                        expr[idx] &= (expr[pre_idx])
                expr[idx] = (~expr[idx])
            elif gate_type == 'OR':
                for pre_idx in pre_list[idx]:
                    if expr[idx].__sizeof__() == 16:
                        expr[idx] = (expr[pre_idx])
                    else:
                        expr[idx] |= (expr[pre_idx])
            elif gate_type == 'NOR':
                for pre_idx in pre_list[idx]:
                    if expr[idx].__sizeof__() == 16:
                        expr[idx] = (expr[pre_idx])
                    else:
                        expr[idx] |= (expr[pre_idx])
                expr[idx] = (~expr[idx])
            elif gate_type == 'NOT':
                expr[idx] = (~expr[pre_list[idx][0]])
            elif gate_type == 'XOR':
                expr[idx] = (expr[pre_list[idx][0]] ^ expr[pre_list[idx][1]])

            # Find Net List
            NL[idx].append(idx)
            for pre_idx in pre_list[idx]:
                NL[idx] += NL[pre_idx]
            NL[idx] = list(set(NL[idx]))

            # Check SAT
            solver = SolverWrapper()
            solver.add_expr(expr[idx])
            if not solver.is_sat():
                print('[INFO] Node {} is UNSAT'.format(x_data[idx][0]))
                sub_circuit_name = bench_name + '_' + str(len(NL[idx])) + '_' + x_data[idx][0]
                save_subcircuit(x_data, NL[idx], pre_list, sub_circuit_name)
            # else:
            #     print('[INFO] Node {} is SAT'.format(x_data[idx][0]))

if __name__ == '__main__':
    for file in glob.glob('./circuits/*.bench'):
        if platform.system() == 'Linux':
            name = file.split("/")
            name = name[-1].split(".")
        else:
            name = file.split("\\")
            name = name[1].split(".")

        file_name = './circuits/'+name[0]+'.bench'
        print('[INFO] Circuit {:}'.format(file_name))
        x_data, level_list, pre_list, next_list = parse_bench(file_name)
        print('[INFO] Read bench file')
        extract_node(x_data, pre_list, level_list, name[0])
        print('Done')