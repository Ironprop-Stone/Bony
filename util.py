import random

def parse_bench(file_name):
    f = open(file_name, "r")
    data = f.readlines()

    data, size = pre_process(data)
    matrix, edge, x_data = feature_generation(data, size)

    pre_list = []
    next_list = []
    level_list = []
    max_level = 0
    for x_data_info in x_data:
        pre_list.append([])
        next_list.append([])
        if x_data_info[2] > max_level:
            max_level = x_data_info[2]
    for level in range(max_level+1):
        level_list.append([])
    for idx, x_data_info in enumerate(x_data):
        level_list[x_data_info[2]].append(idx)
    for c, col in enumerate(matrix):
        for r, row in enumerate(col):
            if row == 1:
                next_list[r].append(c)
                pre_list[c].append(r)

    f.close()
    return x_data, level_list, pre_list, next_list

def pre_process(data):
    '''
    Input:
        (Node_Index):INPUT(x);(Node_level)
    Gate:
        (Node_Index):269 = NAND(1, 8, 13, 17)
    '''
    node_label = 0
    m_size = 0

    for i, val in enumerate(data):
        # matrix size
        # if ("#" in val and "inputs" in val) or ("#" in val and "gates" in val) or ("#" in val and "inverters" in val):
        # v = val.split(" ")
        # m_size = m_size + int(v[1])

        # node level and index  for PI
        if "INPUT" in val:
            data[i] = str(node_label) + ":" + data[i][:len(val) - 1] + ";0"
            node_label = node_label + 1
            m_size = m_size + 1

            # index for gate nodes
        if ("= NAND" in val) or ("= NOR" in val) or ("= AND" in val) or ("= OR" in val) or (
                "= NOT" in val) or ("= XOR" in val):  # or :
            data[i] = str(node_label) + ":" + data[i]
            node_label = node_label + 1
            m_size = m_size + 1

        if "= BUFF" in val:
            data[i] = ":" + data[i]
    return data, m_size

def feature_generation(data, m_size):
    # initializing adjacency matrix: of shape (m_size, m_size)
    '''
    n1 = and(n2, n3, n4)
    level(n1) = max(level(n2), level(n3), level(n4)) + 1;
    '''
    name2line = {}
    for line_idx, line in enumerate(data):
        if 'INPUT' in line:
            node_name = line.split('(')[-1].split(')')[0]
            node_name = node_name.replace(' ', '')
            name2line[node_name] = line_idx
        elif 'AND' in line or 'NAND' in line or 'OR' in line or 'NOR' in line \
            or 'NOT' in line or 'XOR' in line:
            if '=' in line and ':' in line:
                node_name = line.split(':')[-1].split('=')[0]
                node_name = node_name.replace(' ', '')
                name2line[node_name] = line_idx

    Matrix = [[0 for x in range(m_size)] for y in range(m_size)]

    # initializing attributes and edges list
    x_data = [0] * m_size
    edge_index_data = []
    for i1, val in enumerate(data):
        # defining source and destination variables
        initial_sources = []
        updated_sources = []
        initial_destination = 0
        updated_destination = -1
        # defining levels array

        levels = []
        initial_level = -1
        v = []
        if "INPUT" in val:
            # saving on hot vector, scoap and node level for PI in attributes list
            node_index = val.split(":")
            node_name = node_index[1].split("(")
            node_name = node_name[1].split(")")
            x_data[int(node_index[0])] = [node_name[0], get_gate_type(val)]
        elif "= NAND(" in val:
            v = val.split(" = NAND(")
        elif "= NOR(" in val:
            v = val.split(" = NOR(")
        elif "= AND(" in val:
            v = val.split(" = AND(")
        elif "= OR(" in val:
            v = val.split(" = OR(")
        elif "= NOT(" in val:
            v = val.split(" = NOT(")
        elif "= XOR(" in val:
            v = val.split(" = XOR(")
        elif "= BUFF(" in val:
            # v = val.split(" = BUFF(")
            continue

        if len(v) > 1:
            # calculating edge destinations
            destination = v[0].split(":")
            updated_destination = destination[0]
            initial_destination = destination[1]
            # calculating edge sources
            initial_sources = v[1].split(", ")
            last_source = initial_sources[len(initial_sources) - 1].split(")")
            initial_sources[len(initial_sources) - 1] = last_source[0]
            # removing buffers
            # print("initial sources", initial_sources)
            for (idx_s, row) in enumerate(initial_sources):
                value = -1
                for ind, lines in enumerate(data):
                    if ":" + row + " = BUFF(" in lines:
                        l = lines.split("(")
                        l_ = l[1].split(")")
                        value = l_[0]
                        break
                if value != -1:
                    # loop to check nestest parent buffers
                    found = True
                    updated_value = -1
                    while found:
                        updated_value = -1
                        for ind, lines in enumerate(data):
                            if ":" + value + " = BUFF(" in lines:
                                l = lines.split("(")
                                l_ = l[1].split(")")
                                updated_value = l_[0]
                                break
                        if updated_value == -1:
                            found = False
                        else:
                            value = updated_value
                    initial_sources[idx_s] = l_[0]
            initial_sources = Remove(initial_sources)
            # calculating edge source indexes and levels
            for row in initial_sources:
                i = name2line[row]
                lines = data[i]
                l = lines.split(":")
                updated_sources.append(l[0])
                level = lines.split(";")
                if len(level) > 1:
                    levels.append(int(level[1]))
            if updated_destination != -1 and len(updated_sources) != 0:
                # adding edge
                for row in updated_sources:
                    Matrix[int(updated_destination)][int(row)] = 1
                    edge_index_data.append([int(row), int(updated_destination)])
                # adding gate and level feature
                x_data[int(updated_destination)] = [initial_destination, get_gate_type(val)]
            else:
                print(initial_destination)
                print(val)

    next_list = []
    pre_list = []
    bfs_q = []
    x_data_level = [-1] * len(x_data)
    for idx, x_data_info in enumerate(x_data):
        next_list.append([])
        pre_list.append([])
        if x_data_info[1] == 0:
            bfs_q.append(idx)
            x_data_level[idx] = 0
    for r, row in enumerate(Matrix):
        for c, col in enumerate(row):
            if col == 1:
                next_list[c].append(r)
                pre_list[r].append(c)
    while len(bfs_q) > 0:
        idx = bfs_q[-1]
        bfs_q.pop()
        for next_node in next_list[idx]:
            if x_data_level[next_node] == -1:
                update_flag = True
                pre_max_level = 0
                for pre_node in pre_list[next_node]:
                    if x_data_level[pre_node] == -1:
                        update_flag = False
                        break
                    if x_data_level[pre_node] > pre_max_level:
                        pre_max_level = x_data_level[pre_node]
                if update_flag:
                    x_data_level[next_node] = pre_max_level + 1
                    bfs_q.insert(0, next_node)
    if -1 in x_data_level:
        print('Wrong')
        raise
    else:
        for idx in range(len(x_data)):
            x_data[idx].append(x_data_level[idx])


    return Matrix, edge_index_data, x_data

def get_gate_type(node_type):
    if "INPUT" in node_type:
        vector_row = 0
    elif " AND" in node_type:
        vector_row = 1
    elif " NAND" in node_type:
        vector_row = 2
    elif " OR" in node_type:
        vector_row = 3
    elif " NOR" in node_type:
        vector_row = 4
    elif " NOT" in node_type:
        vector_row = 5
    # elif " BUFF" in node_type:
    #   vector_row = 6
    elif " XOR" in node_type:
        vector_row = 6

    return vector_row

def get_gate_type_by_number(type_number):
    res = 'UNKNOWN'
    if type_number == 0:
        res = 'INPUT'
    elif type_number == 1:
        res = 'AND'
    elif type_number == 2:
        res = 'NAND'
    elif type_number == 3:
        res = 'OR'
    elif type_number == 4:
        res = 'NOR'
    elif type_number == 5:
        res = 'NOT'
    elif type_number == 6:
        res = 'XOR'
    return res

def Remove(initial_sources):
    final_list = []
    for num in initial_sources:
        if num not in final_list:
            final_list.append(num)
    return final_list

def random_pattern_generator(no_PIs):
    vector = [0] * no_PIs
    for idx, ele in enumerate(vector):
        vector[idx] = random.randint(0, 1)
    return vector

def logic(gate_type, signals):
    if gate_type == 1:  # AND
        for s in signals:
            if s == 0:
                return 0
        return 1

    elif gate_type == 2:  # NAND
        for s in signals:
            if s == 0:
                return 1
        return 0

    elif gate_type == 3:  # OR
        for s in signals:
            if s == 1:
                return 1
        return 0

    elif gate_type == 4:  # NOR
        for s in signals:
            if s == 1:
                return 0
        return 1

    elif gate_type == 5:  # NOT
        for s in signals:
            if s == 1:
                return 0
            else:
                return 1

    # elif gate_type == 6:  # BUFF
    #  for s in signals:
    #      return s

    elif gate_type == 6:  # XOR
        z_count = 0
        o_count = 0
        for s in signals:
            if s == 0:
                z_count = z_count + 1
            elif s == 1:
                o_count = o_count + 1
        if z_count == len(signals) or o_count == len(signals):
            return 0
        return 1

def simulator(x_data, pre_list, level_list, no_pattern):
    pattern_count = 0
    generated_pattern = []
    y = [0] * len(x_data)
    y1 = [0] * len(x_data)
    while pattern_count < pow(2, len(level_list[0])) and pattern_count < no_pattern:
        input_vector = random_pattern_generator(len(level_list[0]))
        # print("generated vector .. ", input_vector)

        if not input_vector in generated_pattern:
            j = 0
            for i in level_list[0]:
                y[i] = input_vector[j]
                j = j + 1

            for level in range(1, len(level_list), 1):
                for node_idx in level_list[level]:
                    source_signals = []
                    for pre_idx in pre_list[node_idx]:
                        source_signals.append(y[pre_idx])
                    if len(source_signals) > 0:
                        gate_type = x_data[node_idx][1]
                        y[node_idx] = logic(gate_type, source_signals)
                        if y[node_idx] == 1:
                            y1[node_idx] = y1[node_idx] + 1

            pattern_count = pattern_count + 1
            generated_pattern.append(input_vector)
            if pattern_count % 1000 == 0:
                print("pattern count = ", pattern_count)

    return y1[level_list[-1][0]] / no_pattern
