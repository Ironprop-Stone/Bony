# Beta Ongoing Netlist Yielder(BONY): 
# Design for Automated Netlist Generator : DAG generator

# system imports 
from sys import argv
import random
from collections import Counter
import glob
import platform
from parameter import *
from union_find import UnionFind

# from graphplot import exportGMLformat
# arg section

# gateStates = ["AND", "NAND", "OR", "NOR", "XOR"]
gateStates = ['AND', 'OR']

# object: Design constraints for the design
class designConst:
	def __init__(self):
		self.max_fan_out 		= 5
		self.max_fan_in  		= 8
		self.stages 			= 30		# Logic level
		self.max_nodes_in_stage = 50
		self.min_nodes_in_stage = 10
		self.proxDepth			= 5			# Max gap connection level
		self.IterationCount     = 5
		self.mainIterate		= 3
		self.max_tot_nodes		= 1000
		self.min_tot_nodes		= 100
		# --------------------
		self.max_rc_nodes     	= 0.99
		self.min_rc_nodes		= 0.2
		self.max_rc_area		= 0.99
		self.min_rc_area		= 0.6
		self.max_diff			= 999
		# --------------------
		self.circuit_name		= 'Default'
		self.no_nodes			= -1
		# --------------------
		self.serNum2Gate		= {}
		self.dis_connection		= []
	def __del__(self):
		pass	
	
# object:  gate module design framework
class Gate:
	def __init__(self):
		self.serNum = 0 
		self.gateType = ''
		self.isInputNode = 0
		self.isOutputNode = 0
		self.fanInList = []
		self.fanOutList = []
		self.is_branch = 0
		self.logic_stage = -1
	def __del__(self):
		pass	

# object: stage module design framework
class Stage:
	def __init__(self):
		self.numGates = 0
		self.totFanInRem = 0
		self.totFanOutRem = 0
		self.stageGates = []
	def __del__(self):
		pass
	
# grows the entire graph structure		
def growGraph(stageModule, design):
	gen_done = False
	retry_times = 0
	while not gen_done:
		if retry_times > 0 and retry_times % 1000 == 0:
			design.no_nodes = random.randint(design.min_tot_nodes, design.max_tot_nodes)
			design.stages = random.randint(level_range[0], level_range[1])
			print('[INFO] Retry times: {:}, # Nodes: {:}, # Levels: {:}'.format(retry_times, design.no_nodes, design.stages))
		tmp_shuffle = [0] * design.no_nodes
		last_idx = 0
		stage_num = []
		for level in range(design.stages - 1):
			tmp_shuffle[level] = 1
		random.shuffle(tmp_shuffle)
		for idx, ele in enumerate(tmp_shuffle):
			if ele == 1:
				level_len = idx - last_idx
				if level_len < design.min_nodes_in_stage or level_len > design.max_nodes_in_stage:
					break
				stage_num.append(level_len)
				last_idx = idx
		stage_num.append(design.no_nodes - last_idx)
		if design.no_nodes - last_idx != 0 and len(stage_num) == design.stages:
			gen_done = True
		else:
			retry_times += 1
	for level in range(design.stages):
		print('Level: {}, len: {}'.format(level, stage_num[level]))

	gateCount = 0
	for i in range(design.stages):
		stage = Stage()
		stage.numGates = stage_num[i]
		stageModule.append(stage)
		for j in range(stageModule[i].numGates):
			gate  = Gate()
			gateCount += 1
			gate.serNum = gateCount
			gate.logic_stage = i
			stageModule[i].stageGates.append(gate)
			design.serNum2Gate[gate.serNum] = gate
	print('[INFO] No of Gates: {:}, Level: {:}'.format(gateCount, design.stages))
	return gateCount		
					
					
# sets the input-output nodes/pins for the graph schematic
#	- Assumption: The number of deep in-out nodes will be a random event: range(number of stages in the circuit)
def setInputOutputNodes(stageModule, design):
	# sets the input nodes : entire first stage is input though
	nodesInFirstStage = len(stageModule[0].stageGates)
	# first stage is input by default
	for first in range(nodesInFirstStage):
		stageModule[0].stageGates[first].isInputNode = 1

	# sets the output nodes : entire output stage is output though
	nodesInLastStage = len(stageModule[design.stages - 1].stageGates)
	# last stage is output by default
	for last in range(nodesInLastStage):
		stageModule[design.stages - 1].stageGates[last].isInputNode = 0
		stageModule[design.stages - 1].stageGates[last].isOutputNode = 1


	# # determines the number of deep input nodes
	# detDeepInNodeCount = random.randint(0,design.stages-1)
	# for dNodeIn in range(detDeepInNodeCount):
	# 	# determine the stage selection at random
	# 	detStageIn = random.randint(0,design.stages-1)
	# 	# determine the  stage selection at random
	# 	detNodeIn = random.randint(0,len(stageModule[detStageIn].stageGates)-1)
	# 	# set the selected node to an Deep Input Node stage
	# 	stageModule[detStageIn].stageGates[detNodeIn].isInputNode = 1
	#
	#
	# # deterine the number of deep output modules
	# detDeepOutNodeCount = random.randint(0,design.stages-1)
	# for dNodeOut in range(detDeepOutNodeCount):
	# 	# determine the stage selection at random
	# 	detStageOut = random.randint(0,design.stages-1)
	# 	# determine the stage selection at random
	# 	detNodeOut = random.randint(0,len(stageModule[detStageOut].stageGates)-1)
	# 	# determine the selected node to a Deep Output Node stage
	# 	if stageModule[detStageOut].stageGates[detNodeOut].isInputNode != 1:
	# 		# preference given for input node select over output node selection
	# 		stageModule[detStageOut].stageGates[detNodeOut].isOutputNode = 1


# generate optimal start and stop functions for the stage random allocation
def generateRandStartandEndPoints(appRandStart,appRandEnd, design):
	if appRandEnd - appRandStart > design.proxDepth:
		randStart = appRandStart
		randEnd = appRandStart + design.proxDepth
	else:
		randStart = appRandStart
		randEnd = appRandEnd

	return randStart,randEnd
		


# fast: determine the interconnects: generate complete graph	
def determineInterConnectsFast(stageModule, design, uf):
	# map the fan-out with single dimension for each node random process
	for i in range(len(stageModule)-1):
		for j in range(len(stageModule[i].stageGates)): 
			node = stageModule[i].stageGates[j]
			# map the fan-out with single dimension for each node random process
			#	-doesn't gurantee that every node has a fan-in or fanout
			#	- output nodes will not have any fan-out(s) and input nodes no fan-ins(s)
			#	-random map: gurantee max fan-in not violated: rerun of rand return node allocation			
			if not node.isOutputNode:			
				#allocRandStage = random.randint(i+1,design.stages-1) 
				randStart,randEnd = generateRandStartandEndPoints(i+1,design.stages-1, design)
				allocRandStage = random.randint(randStart,randEnd) 				
				
				allocRandNode = random.randint(0,len(stageModule[allocRandStage].stageGates)-1)
				nodeConnect = stageModule[allocRandStage].stageGates[allocRandNode]
				if not nodeConnect.isInputNode: 
					if (nodeConnect.serNum not in node.fanOutList) and (node.serNum not in nodeConnect.fanInList):
						if (len(node.fanOutList) < design.max_fan_out) and (len(nodeConnect.fanInList) < design.max_fan_in):
							node.fanOutList.append(nodeConnect.serNum)
							nodeConnect.fanInList.append(node.serNum)		
							uf.union(node.serNum-1, nodeConnect.serNum-1)
			
			# map the fan-in with single dimension for each node random process
			if not node.isInputNode:
				#allocRandStage = random.randint(0,i-1)	
				randStart,randEnd = generateRandStartandEndPoints(0,i-1, design)
				allocRandStage = random.randint(randStart,randEnd) 				
				
				allocRandNode = random.randint(0,len(stageModule[allocRandStage].stageGates)-1)
				nodeConnect = stageModule[allocRandStage].stageGates[allocRandNode]
				if not nodeConnect.isOutputNode:
					if (nodeConnect.serNum not in node.fanInList) and (node.serNum not in nodeConnect.fanOutList):
						if (len(node.fanInList) < design.max_fan_in) and (len(nodeConnect.fanOutList) < design.max_fan_out):
							node.fanInList.append(nodeConnect.serNum)
							nodeConnect.fanOutList.append(node.serNum)	
							uf.union(node.serNum-1, nodeConnect.serNum-1)			


# stage analysis for free fanin and fanouts that can be accomodated for a complete connected network
def normalizeInterconnects(stageModule, design, uf):
	remFO = []
	remFI = []
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)): 
			node = stageModule[i].stageGates[j]	
			if not node.isOutputNode:
				if not len(node.fanOutList):
					for idx in range(50):
						allocRandStage = random.randint(i + 1, design.stages - 1)
						allocRandNode = random.randint(0, len(stageModule[allocRandStage].stageGates) - 1)
						nodeConnect = stageModule[allocRandStage].stageGates[allocRandNode]
						if not nodeConnect.isInputNode:
							if (nodeConnect.serNum not in node.fanOutList) and (
									node.serNum not in nodeConnect.fanInList):
								if (len(node.fanOutList) < design.max_fan_out + 1) and (
										len(nodeConnect.fanInList) < design.max_fan_in + 1):
									node.fanOutList.append(nodeConnect.serNum)
									nodeConnect.fanInList.append(node.serNum)
									uf.union(node.serNum-1, nodeConnect.serNum-1)
									break
					if not len(node.fanOutList):
						remFO.append(node.serNum)
			if not node.isInputNode:
				if not len(node.fanInList):
					for idx in range(50):
						allocRandStage = random.randint(0, i - 1)
						allocRandNode = random.randint(0, len(stageModule[allocRandStage].stageGates) - 1)
						nodeConnect = stageModule[allocRandStage].stageGates[allocRandNode]
						if not nodeConnect.isOutputNode:
							if (nodeConnect.serNum not in node.fanInList) and (
									node.serNum not in nodeConnect.fanOutList):
								if (len(node.fanInList) < design.max_fan_in + 1) and (
										len(nodeConnect.fanOutList) < design.max_fan_out + 1):
									node.fanInList.append(nodeConnect.serNum)
									nodeConnect.fanOutList.append(node.serNum)
									uf.union(node.serNum-1, nodeConnect.serNum-1)
									break
					if not len(node.fanInList):
						remFI.append(node.serNum)
	
	new_dis_connection = []
	for idx in design.dis_connection:
		if not uf.is_connected(0, node.serNum-1):
			node = design.serNum2Gate[idx]
			for times in range(50):
				allocRandStage = random.randint(node.logic_stage + 1, design.stages - 1)
				allocRandNode = random.randint(0, len(stageModule[allocRandStage].stageGates) - 1)
				nodeConnect = stageModule[allocRandStage].stageGates[allocRandNode]
				if not nodeConnect.isInputNode:
					if (nodeConnect.serNum not in node.fanOutList) and (
							node.serNum not in nodeConnect.fanInList):
						if (len(node.fanOutList) < design.max_fan_out + 1) and (
								len(nodeConnect.fanInList) < design.max_fan_in + 1):
							node.fanOutList.append(nodeConnect.serNum)
							nodeConnect.fanInList.append(node.serNum)
							uf.union(node.serNum-1, nodeConnect.serNum-1)
							break
			if not uf.is_connected(0, node.serNum-1):
				remFO.append(node.serNum)
				new_dis_connection.append(idx)
	design.dis_connection = new_dis_connection.copy()
	
	return remFO,remFI


# generates the random gate criteria by suffle mode					
def randomGateState():
	random.shuffle(gateStates)
	return gateStates[0]		# returns the first gate always	
	
# allocate the gate notation to the nodes in the circuit		
def allocateGateNotation(stageModule):
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			if node.isInputNode:
				pass
			else:
				if len(node.fanInList) == 1:	# inverter probable
					node.gateType = 'NOT'
				elif len(node.fanInList) == 2:
					node.gateType = randomGateState()
				else:
					non_xor_gateType = randomGateState()
					while non_xor_gateType == 'XOR':
						non_xor_gateType = randomGateState()
					node.gateType = non_xor_gateType

# generate the automated schematic framework
def generateBenchMarkCircuit(stageModule, targetfile):
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			if node.isInputNode:
				line = "INPUT(" + str(node.serNum) +")" +"\n"
				targetfile.write(line)				

	targetfile.write('\n\n')	
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			if node.isOutputNode:
				line = "OUTPUT(" + str(node.serNum) +")"+"\n"
				targetfile.write(line)
				
	targetfile.write('\n\n')					
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			if not node.isInputNode: 			
				line = str(node.serNum) +" = "+ node.gateType + "("
				for fanInRange in range(len(node.fanInList)):
					if fanInRange == len(node.fanInList)-1:
						line += str(node.fanInList[fanInRange])
					else:
						line += str(node.fanInList[fanInRange]) +", "
				line += ")\n"
				targetfile.write(line)			
							
def generateVerilogMarkCircuit(stageModule, targetfile):
	if platform.system() == 'Linux':
		name = targetfile.name.split("/")
		name = name[-1].split(".")
	else:
		name = targetfile.name.split("\\")
		name = name[1].split(".")
	circuit_name = name[0]
	pi_po_line = ''
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			if node.isInputNode or node.isOutputNode:
				pi_po_line += 'N' + str(node.serNum) + ', '
	pi_po_line = pi_po_line[:-2]
	first_line = 'module {} ({});\n'.format(circuit_name, pi_po_line)
	targetfile.write(first_line)
	targetfile.write('\n')		

	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			if node.isInputNode:
				line = "input " + 'N' + str(node.serNum) + "; \n"
				targetfile.write(line)				

	targetfile.write('\n')	
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			if node.isOutputNode:
				line = "output " + 'N' + str(node.serNum) + "; \n"
				targetfile.write(line)

	targetfile.write('\n')	
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			if not node.isInputNode and not node.isOutputNode:
				line = "wire " + 'N' + str(node.serNum) + "; \n"
				targetfile.write(line)
	
	targetfile.write('\n')					
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			if not node.isInputNode: 			
				line = 'assign ' + 'N' + str(node.serNum) +" = "
				gate_symbol = gateType2symbol(node.gateType)
				if gate_symbol == '~':
					line += gate_symbol+'({}); \n'.format('N' + str(node.fanInList[0]))
				else:
					for fanInRange in range(len(node.fanInList)):
						if fanInRange == len(node.fanInList) - 1:
							line += 'N' + str(node.fanInList[fanInRange]) + '; \n'
						else:
							line += 'N' + str(node.fanInList[fanInRange]) + ' ' + gate_symbol + ' '
				targetfile.write(line)			

	targetfile.write('endmodule\n')

def gateType2symbol(gate_type):
	if gate_type == 'AND':
		return '&'
	elif gate_type == 'OR':
		return '|'
	elif gate_type == 'XOR':
		return '^'
	elif gate_type == 'NOT':
		return '~'
	else:
		print('[ERROR] Type Unknown')
		raise


# non random : normalize method: 
def nonRandomNormalize(stageModule,remFO,remFI):
	print("It Wont work _critic :P ")

def check_reconvergent(stageModule, design, uf):
	tot_nodes = 0
	FOL = []
	source_node_list = []
	serNum2MatrixIdx = {}

	cnt = 0
	for level in range(len(stageModule)):
		cnt += len(stageModule[level].stageGates)
	if cnt > design.max_tot_nodes:
		return False, ''

	for level in range(len(stageModule)):
		FOL.append([])
		source_node_list.append([])
		tot_nodes += stageModule[level].numGates
		for idx, node in enumerate(stageModule[level].stageGates):
			FOL[level].append([])
			source_node_list[level].append(-1)
			serNum2MatrixIdx[node.serNum] = [level, idx]
			if len(node.fanOutList) > 0:
				node.is_branch = 1

	###########################################
	# Check Reconvergent Noodes
	###########################################
	for level in range(len(stageModule)):
		if level == 0:
			for idx, node in enumerate(stageModule[level].stageGates):
				if node.is_branch == 1:
					FOL[level][idx].append(node.serNum)
		else:
			for idx, node in enumerate(stageModule[level].stageGates):
				FOL_tmp = []
				for pre_serNum in node.fanInList:
					pre_level, pre_idx = serNum2MatrixIdx[pre_serNum]
					FOL_tmp += FOL[pre_level][pre_idx]
					FOL_cnt_dist = Counter(FOL_tmp)
					source_node_idx = 0
					source_node_level = -1
					is_rc = False
					for dist_idx in FOL_cnt_dist:
						if FOL_cnt_dist[dist_idx] > 1:
							is_rc = True
							if serNum2MatrixIdx[dist_idx][0] > source_node_level:
								source_node_level = serNum2MatrixIdx[dist_idx][0]
								source_node_idx = dist_idx
					if is_rc:
						source_node_list[level][idx] = source_node_idx
					else:
						source_node_list[level][idx] = -1
					FOL[level][idx] = list(set(FOL_tmp))
					if node.is_branch:
						FOL[level][idx].append(node.serNum)

	tot_rc_nodes = 0
	for level in range(len(stageModule)):
		for idx, node in enumerate(stageModule[level].stageGates):
			if source_node_list[level][idx] != -1:
				tot_rc_nodes += 1

	rc_nodes_ratio = tot_rc_nodes / tot_nodes
	if not (rc_nodes_ratio > design.min_rc_nodes and rc_nodes_ratio < design.max_rc_nodes):
		return False, ''

	###########################################
	# Check Level Difference
	###########################################
	max_level_diff = 0
	for level in range(len(stageModule)):
		for idx, node in enumerate(stageModule[level].stageGates):
			if source_node_list[level][idx] != -1:
				src_level, _ = serNum2MatrixIdx[source_node_list[level][idx]]
				if level - src_level > max_level_diff:
					max_level_diff = level - src_level
	if max_level_diff > design.max_diff:
		return False, ''

	###########################################
	# Check Reconvergent Area
	###########################################
	# rc_area_list = []
	# for level in range(len(stageModule)):
	# 	for idx, node in enumerate(stageModule[level].stageGates):
	# 		if source_node_list[level][idx] != -1:
	# 			src_serNum = source_node_list[level][idx]
	# 			dst_serNum = node.serNum
	# 			rc_area_list += dfs_rc_circuits(src_serNum, [src_serNum],
	# 										   dst_serNum, [],
	# 										   stageModule, serNum2MatrixIdx)
	# rc_area_list = list(set(rc_area_list))
	# rc_area_ratio = len(rc_area_list) / tot_nodes
	# if not (rc_area_ratio > design.min_rc_area and rc_area_ratio < design.max_rc_area):
	# 	return False, ''

	###########################################
	# Check Connection
	###########################################
	for idx in range(1, design.no_nodes, 1):
		if not uf.is_connected(0, idx):
			return False, ''
        
	info = ''
	info += '-----------------------------------\n'
	info += 'Circuit Name: {}\n'.format(design.circuit_name)
	info += 'Number of Nodes: {:}\n'.format(tot_nodes)
	info += 'Max level : {:}, \n'.format(max_level_diff)
	info += 'Reconvergent nodes: {:}/{:} = {:}\n'.format(tot_rc_nodes, tot_nodes, rc_nodes_ratio)
	# info += 'Reconvergent area: {:}/{:} = {:}\n'.format(len(rc_area_list), tot_nodes, rc_area_ratio)
	info += '-----------------------------------\n'
	info += '\n'
	return True, info

def dfs_rc_circuits(node_serNum, vis, dst_serNum, result, stageModule, serNum2MatrixIdx):
	if node_serNum == dst_serNum:
		result += vis
		return
	level, idx = serNum2MatrixIdx[node_serNum]
	for next_serNum in stageModule[level].stageGates[idx].fanOutList:
		next_level, _ = serNum2MatrixIdx[next_serNum]
		dst_level, _ = serNum2MatrixIdx[dst_serNum]
		if next_level <= dst_level:
			vis.append(next_serNum)
			dfs_rc_circuits(next_serNum, vis, dst_serNum, result, stageModule, serNum2MatrixIdx)
			vis = vis[:-1]
	return result

# iterative chance solver and final normalization method:
def iterateSolveandNormalize(stageModule, targetfile, design, uf):
	remFO = []
	remFI = []
	for i in range(1,design.IterationCount):
		remFO,remFI = normalizeInterconnects(stageModule, design, uf)
	if not len(remFO) and not len(remFI) and not len(design.dis_connection):
		check_res, circuit_info = check_reconvergent(stageModule, design, uf)
		if not check_res:
			return False, ''
		print("design sucess!")
		allocateGateNotation(stageModule)
		# generateBenchMarkCircuit(stageModule, targetfile)
		generateVerilogMarkCircuit(stageModule, targetfile)
		#exportGMLformat(stageModule)
		return True, circuit_info
	else:
		print("design fail!")
		print(remFO,remFI)
		nonRandomNormalize(stageModule,remFO,remFI)
		return False, ''
		
# deign framework : pretty much everything designed here : DAG generation mapping and allocation
def designFramework(stageModule, targetfile, design, uf):
	setInputOutputNodes(stageModule, design)
	#determineInterConnects(stageModule)
	determineInterConnectsFast(stageModule, design, uf)
	for i in range(0,design.mainIterate):	
		status, circuit_info = iterateSolveandNormalize(stageModule, targetfile, design, uf)
		if status == True:
			break
	return circuit_info

# simple graph traversal function : printing the ser num of the nodes in graph
def traverseGraph(stageModule, design):
	for i in range(len(stageModule)):
		for j in range(len(stageModule[i].stageGates)):
			node = stageModule[i].stageGates[j]
			print(node.serNum,"[stage]",i,"in",node.isInputNode,"out",node.isOutputNode,
				  "fanOutList:",node.fanOutList," fanInList:",node.fanInList)
def main():
	filename = './test.bench'
	targetfile = open(filename, 'w')
	design = designConst()
	stageModule = []
	totGates = 0
	totGates = growGraph(stageModule, design)				# grow the graph using nested lists
	designFramework(stageModule, targetfile, design)
	print(" The total number of gates: ",totGates)
	#traverseGraph(stageModule)				 	# traverse the entire graph	
	targetfile.close()

if __name__ == '__main__':
	main()


