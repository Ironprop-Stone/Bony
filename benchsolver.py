import aiger
from  aiger_cnf import aig2cnf
from util import *
from aiger_sat import SolverWrapper
import glob
import platform

def get_PO_expr(x_data, level_list, pre_list):
    # if len(level_list[-1]) != 1:
    #     print('[ERROR] Must one PO!')
    #     return None

    expr = []
    x_symbol = []
    for x_data_info in x_data:
        expr.append(None)
        x_symbol.append(aiger.atom(x_data_info[0]))

    # Assign symbol for PI expr
    for pi_idx in level_list[0]:
        expr[pi_idx] = x_symbol[pi_idx]

    # Find expr for all nodes level by level
    for level in range(1, len(level_list), 1):
        for idx in level_list[level]:
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

    return expr[level_list[-1][0]]

def solve_bench(file_name):
    x_data, level_list, pre_list, next_list = parse_bench(file_name)
    PO_expr = get_PO_expr(x_data, level_list, pre_list)

    solver = SolverWrapper()
    solver.add_expr(PO_expr)

    sat_res = solver.is_sat()
    if not sat_res:
        sat_ass = None
    else:
        sat_ass = solver.get_model()
    return sat_res, sat_ass

def solve_and_simulation(file_name, prob_range, no_pattern):
    x_data, level_list, pre_list, next_list = parse_bench(file_name)
    PO_prob = simulator(x_data, pre_list, level_list, no_pattern)
    if PO_prob < prob_range[0] or PO_prob > prob_range[1]:
        print('[FAILED] Probability of PO cannot match')
        return False, None
    print('PO Probability : {:}'.format(PO_prob))

    PO_expr = get_PO_expr(x_data, level_list, pre_list)
    solver = SolverWrapper()
    solver.add_expr(PO_expr)

    sat_res = solver.is_sat()
    if not sat_res:
        sat_ass = None
    else:
        sat_ass = solver.get_model()
    return sat_res, sat_ass

def check_sat_unsat_node(x_data, level_list, pre_list):
    expr = []
    fanin_list = []
    x_symbol = []
    sat_nodes = []
    unsat_nodes = []
    tot_node_cnt = len(x_data)
    proc_node_cnt = 0
    for x_data_info in x_data:
        expr.append(None)
        fanin_list.append([])
        x_symbol.append(aiger.atom(x_data_info[0]))

    # Assign symbol for PI expr
    for pi_idx in level_list[0]:
        expr[pi_idx] = x_symbol[pi_idx]
        fanin_list[pi_idx].append(pi_idx)

    # Find expr for all nodes level by level
    for level in range(1, len(level_list), 1):
        for idx in level_list[level]:
            # Generate the expr
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
            # Update fan-in list
            for pre_idx in pre_list[idx]:
                fanin_list[idx] += fanin_list[pre_idx]
            fanin_list[idx].append(idx)
            fanin_list[idx] = list(set(fanin_list[idx]))

            # Solve
            solver = SolverWrapper()
            solver.add_expr(expr[idx])
            if solver.is_sat():
                sat_nodes.append(idx)
            else:
                unsat_nodes.append(idx)
            # Print
            proc_node_cnt += 1
            if proc_node_cnt % 100 == 0:
                print('[INFO] Check {:} out of {:}'.format(proc_node_cnt, tot_node_cnt))

    return sat_nodes, unsat_nodes, fanin_list

def output_subcircuit(x_data, level_list, pre_list, sc_nodes, po_idx, filename):
    targetfile = open(filename, 'w')
    for level in range(0, len(level_list), 1):
        if level == 0:
            for idx in level_list[level]:
                if idx in sc_nodes:
                    line = 'INPUT(' + str(x_data[idx][0]) + ')\n'
                    targetfile.write(line)
            targetfile.write('\n')
            line = 'OUTPUT(' + str(x_data[po_idx][0]) + ')\n'
            targetfile.write(line)
            targetfile.write('\n')
        else:
            for idx in level_list[level]:
                if idx in sc_nodes:
                    fanin_nodes = []
                    for pre_idx in pre_list[idx]:
                        if pre_idx in sc_nodes:
                            fanin_nodes.append(pre_idx)
                    line = str(x_data[idx][0]) + ' = '
                    gate_type = get_gate_type_by_number(x_data[idx][1])
                    line += gate_type + '('
                    for k, pre_idx in enumerate(fanin_nodes):
                        if k == len(fanin_nodes) - 1:
                            line += x_data[pre_idx][0] + ')\n'
                        else:
                            line += x_data[pre_idx][0] + ', '
                    targetfile.write(line)
    targetfile.close()

if __name__ == '__main__':
    sat_cnt = 0
    unsat_cnt = 0
    for bench_file in glob.glob('./bench/*.bench'):
        if platform.system() == 'Linux':
            name = bench_file.split("/")
            name = name[-1].split(".")
        else:
            name = bench_file.split("\\")
            name = name[1].split(".")

        circuit_name = name[0]

        x_data, level_list, pre_list, next_list = parse_bench(bench_file)
        sat_nodes, unsat_nodes, fanin_list = check_sat_unsat_node(x_data, level_list, pre_list)

        # SAT subcircuit
        for sat_node in sat_nodes:
            if len(fanin_list[sat_node]) > 300 and len(fanin_list[sat_node]) < 1500:
                filename = './sat_unsat/SAT_' + str(sat_cnt).zfill(3) + '.bench'
                output_subcircuit(x_data, level_list, pre_list, fanin_list[sat_node], sat_node, filename)
                sat_cnt += 1

        # UNSAT subcircuit
        for unsat_node in unsat_nodes:
            if len(fanin_list[unsat_node]) > 300 and len(fanin_list[unsat_node]) < 1500:
                filename = './sat_unsat/UNSAT_' + str(unsat_cnt).zfill(3) + '.bench'
                output_subcircuit(x_data, level_list, pre_list, fanin_list[unsat_node], unsat_node, filename)
                unsat_cnt += 1

        print(' ---------------------------------------------- ')
        print('[INFO] Circuit Name: {}'.format(circuit_name))
        print('[INFO] SAT node: {:} / {:}, save: {:} / {:}'.format(len(sat_nodes), len(x_data), sat_cnt, len(x_data)))
        print('[INFO] UNSAT node: {:} / {:}, save: {:} / {:}'.format(len(unsat_nodes), len(x_data), unsat_cnt,
                                                                     len(x_data)))
    print(' Done ')


