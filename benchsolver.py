import aiger
from  aiger_cnf import aig2cnf
from util import *
from aiger_sat import SolverWrapper

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

if __name__ == '__main__':
    file_name = './circuits/int2float.bench'
    x_data, level_list, pre_list, next_list = parse_bench(file_name)
    PO_expr = get_PO_expr(x_data, level_list, pre_list)

    solver = SolverWrapper()
    solver.add_expr(PO_expr)
    sat_ass = solver.get_model()

    print(solver.is_sat())
    print(sat_ass)
