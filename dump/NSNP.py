from latex2sympy2 import latex2sympy, latex2latex
import json, pprint, random, sympy, re

# VERSION 1
JSON_XMP_1 = {
	"NSNP": {
		"neurons": {
			"n1": {
				"var":{
					"x_{1,1}":1,
					"x_{2,1}":2
				},
				"prf":{
					"f1":"x_{1,1}+x_{2,1}",
					"f2":"2*x_{1,1}"
				}
			},
			"n2": {
				"var":{
					"x_{1,2}":0,
					"x_{2,2}":0
				},
				"prf":{}
			}
		},
		"syn":[["n1","n2"]],
		"in":[],
		"out":["x_{2,1}"]
	},
	"branch" : 2,
	"sim_type" : 0,
	"cur_depth" : 0,
	"sim_depth" : 100,
	"random" : True,
	"choice" : [["n1","f1",5]]
}

# VERSION 2
JSON_XMP_2a = {
	"NSNP": {
		"neurons": [
			{
				"id":1,
				"name":"n1",
				"var":[
					{"id":1,"uid":"x_{1,1}","name":"var1","value":5},
					{"id":2,"uid":"x_{2,1}","name":"var2","value":6},
				],
				"prf":[
					{"id":1,"uid":"f_{1,1}","name":"f1","expr":"x_{1,1}+x_{2,1}","thld":None},
					{"id":2,"uid":"f_{2,1}","name":"f2","expr":"2*x_{1,1}","thld":None},
				]
			},
			{
				"id":2,
				"name":"n2",
				"var":[
					{"id":1,"uid":"x_{1,2}","name":"var3","value":9},
				],
				"prf":[
					{"id":1,"uid":"f_{1,2}","name":"f3","expr":"x_{1,2}+\\frac{1}{2}","thld":1},
				]
			}
		],
		"syn":[[1,2]],
		"in":[],
		"out":[2]
	},
	"branch" : 2,
	"sim_type" : 1,
	"cur_depth" : 0,
	"sim_depth" : 10,
	"choice" : [["n1","f1",5]]
}

JSON_XMP_2b = {
	"NSNP": {
		"neurons": [
			{
				"id":1,
				"name":"n1",
				"var":[
					{"id":1,"uid":"x_{1,1}","name":"var1","value":1},
					{"id":2,"uid":"x_{2,1}","name":"var2","value":1},
				],
				"prf":[
					{"id":1,"uid":"f_{1,1}","name":"f1","expr":"(1/2)(x_{1,1}+x_{2,1})","thld":1},
				]
			},
			{
				"id":2,
				"name":"n2",
				"var":[
					{"id":1,"uid":"x_{1,2}","name":"var3","value":1},
				],
				"prf":[
					{"id":1,"uid":"f_{1,2}","name":"f2","expr":"x_{1,2}","thld":None},
					{"id":2,"uid":"f_{2,2}","name":"f3","expr":"-x_{1,2}","thld":None}
				]
			},
			{
				"id":3,
				"name":"n3",
				"var":[
					{"id":1,"uid":"x_{1,3}","name":"var4","value":0},
				],
				"prf":[
					{"id":1,"uid":"f_{1,3}","name":"f4","expr":"x_{1,3}","thld":None},
				]
			},
			{
				"id":4,
				"name":"n4",
				"var":[
					{"id":1,"uid":"x_{1,4}","name":"var5","value":0},
				],
				"prf":[
					{"id":1,"uid":"f_{1,4}","name":"f5","expr":"-x_{1,4}","thld":None},
				]
			},
			{
				"id":5,
				"name":"n5",
				"var":[
					{"id":1,"uid":"x_{1,5}","name":"var6","value":2},
				],
				"prf":[
					{"id":1,"uid":"f_{1,5}","name":"f6","expr":"(1/2)x_{1,5}","thld":None},
				]
			},
		],
		"syn":[[1,2],[2,1],[1,3],[2,4],[3,5],[4,5]],
		"in":[],
		"out":[2]
	},
	"branch" : 2,
	"sim_type" : 1,
	"cur_depth" : 0,
	"sim_depth" : 10,
	"choice" : [["n1","f1",5]]
}

JSON_XMP_2c = {
	"NSNP": {
		"neurons": [
			{
				"id":1,
				"name":"n1",
				"var":[
					{"id":1,"uid":"x_{1,1}","name":"var1","value":1},
					{"id":2,"uid":"x_{2,1}","name":"var2","value":1},
				],
				"prf":[
					{"id":1,"uid":"f_{1,1}","name":"f1","expr":"x_{1,1}+x_{2,1}","thld":None},
					{"id":2,"uid":"f_{2,1}","name":"f2","expr":"0.5(x_{1,1}+x_{2,1})","thld":None}
				]
			},
			{
				"id":2,
				"name":"n2",
				"var":[
					{"id":1,"uid":"x_{1,2}","name":"var3","value":2},
				],
				"prf":[
					{"id":1,"uid":"f_{1,2}","name":"f2","expr":"x_{1,2}","thld":None},
					{"id":2,"uid":"f_{2,2}","name":"f3","expr":"0.5(x_{1,2})","thld":4}
				]
			},
		],
		"syn":[[1,2],[2,1]],
		"in":[],
		"out":[2]
	},
	"branch" : 2,
	"sim_type" : 1,
	"cur_depth" : 0,
	"sim_depth" : 100,
	"choice" : [["n1","f1",5]]
}

# Class that represents a numerical spiking neural p system
class NumericalSNPSystem:
	def __init__(self, neurons, synapses, 
					in_neuron, out_neuron):
		self.neurons = neurons
		self.synapses = synapses
		self.in_neuron = in_neuron
		self.out_neuron = out_neuron
		self.var_config = {var["uid"]:var["value"] for neuron in neurons
							for var in neuron["var"]}
		self.init_config = self.var_config

	# Helper Functions for calculating configurations
	# 	- get_node_by_var: returns the node id from a variable uid
	# 	- get_adjacent_neurons: returns the adjacent neurons of a neuron
	# 	- choose_random_function: returns a random function from a list
	# 	- get_var_total: returns the total value of a list of variables
	

	def get_node_by_var(self, uid):
		return int(re.search(r"x_{[1-9]+,([1-9]+)}", uid).group(1))

	def get_adjacent_neurons(self, neuron):
		return [synapse[1] for synapse in self.synapses 
									if synapse[0] == neuron["id"]]

	def get_random_function(self, prf_list):
		return prf_list.pop(random.randrange(len(prf_list)))

	def get_vars_min(self,neuron,vars_uid):
		return min([self.var_config[var["uid"]] for var in neuron["var"] 
									if sympy.Symbol(var["uid"]) in vars_uid])

	# Simulation of the system
	# 	- simulate: simulates the system for a given depth starting from cur_depth
	# 	- next_config: simulates the system for a single timestep
	#   - distribute: distributes the value of a variable to the adjacent neurons
	# 	- valid_prf_call: returns whether a prf call is valid based on the threshold

	def simulate(self, sim_type, cur_depth, sim_depth, choices):
		config_list = [self.var_config.copy()]
		# 
		while cur_depth < sim_depth:
			next_config, prf_called = self.next_config(sim_type, choices)
			if not prf_called: break
			config_list.append(next_config)
			cur_depth += 1
			
		return config_list
		
	def next_config(self, sim_type, choices):
		var_changes = self.var_config.copy()
		prf_called = False
		#print("==="*20)
		for neuron in self.neurons:
			prf_list = neuron["prf"].copy()

			while len(prf_list):
				# Necessary for simulation
				synapses = self.get_adjacent_neurons(neuron)
				prf = self.get_random_function(prf_list)    #TODO: Change this function to enable simulation types
				expr = latex2sympy(prf["expr"])

				# For treshold checking
				vars_uid = expr.atoms(sympy.Symbol)
				vars_min = self.get_vars_min(neuron,vars_uid)
				prf_value = expr.evalf(subs=self.var_config)
				
				# Check if prf call is valid and distribute					
				if self.valid_prf_call(prf, prf_value, vars_uid, vars_min):
					#print(prf)
					self.distribute(var_changes, vars_uid, synapses, prf_value)
					prf_called = True
					break
		
		# 	print(neuron["id"], prf["id"], prf["thld"], vars_min, prf_value, self.valid_prf_call(prf, prf_value, vars_uid, vars_min), )
		# print(var_changes)

		self.var_config = var_changes
		return var_changes, prf_called

	def valid_prf_call(self, prf, prf_value, vars_uid, vars_min):
		all_zero = False if prf_value else True
		# Check if all variables are zero
		for var in vars_uid:
			if self.var_config[str(var)] != 0:
				all_zero = False
				break

		return (prf["thld"] == None or prf["thld"] <= vars_min) and not all_zero

	def distribute(self, var_changes, vars_uid, synapses, prf_value):
		for var in var_changes:
			# Variables of in the same neuron
			if sympy.Symbol(var) in vars_uid:
				var_changes[var] -= self.var_config[var]

			# Variables of adjacent neurons
			if self.get_node_by_var(var) in synapses:
				var_changes[var] += prf_value














def parse_simulation(simulation):
	neurons = simulation["NSNP"]["neurons"]
	synapses = simulation["NSNP"]["syn"]
	in_neuron = simulation["NSNP"]["in"]
	out_neuron = simulation["NSNP"]["out"]
	return NumericalSNPSystem(neurons, synapses, in_neuron, out_neuron)

def check_polynomial(neurons):
	for neuron in neurons:
		for prf in neuron["prf"]:
			expr = latex2sympy(neuron["prf"][prf])
			if expr.is_polynomial() == False:
				return False
	return True

def convert_config_to_int(config):
	for var in config:
		config[var] = int(config[var])
	return config

def print_config(config):
	for var in config:
		print(config[var], end="\t")
	print()

# NSNP_1 = NumericalSNPSystem(JSON_XMP_2a["NSNP"]["neurons"],JSON_XMP_2a["NSNP"]["syn"],JSON_XMP_2a["NSNP"]["in"],JSON_XMP_2a["NSNP"]["out"])
# config_path = NSNP_1.simulate(JSON_XMP_2a["sim_type"],JSON_XMP_2a["cur_depth"],JSON_XMP_2a["sim_depth"],JSON_XMP_2a["choice"])
# for i in config_path:
# 	print_config(convert_config_to_int(i))

NSNP_2 = NumericalSNPSystem(JSON_XMP_2b["NSNP"]["neurons"],JSON_XMP_2b["NSNP"]["syn"],JSON_XMP_2b["NSNP"]["in"],JSON_XMP_2b["NSNP"]["out"])
config_path = NSNP_2.simulate(JSON_XMP_2b["sim_type"],JSON_XMP_2b["cur_depth"],JSON_XMP_2b["sim_depth"],JSON_XMP_2b["choice"])
for i in config_path:
	print_config(convert_config_to_int(i))

# NSNP_3 = NumericalSNPSystem(JSON_XMP_2c["NSNP"]["neurons"],JSON_XMP_2c["NSNP"]["syn"],JSON_XMP_2c["NSNP"]["in"],JSON_XMP_2c["NSNP"]["out"])
# config_path = NSNP_3.simulate(JSON_XMP_2c["sim_type"],JSON_XMP_2c["cur_depth"],JSON_XMP_2c["sim_depth"],JSON_XMP_2c["choice"])
# for i in config_path:
# 	print_config(convert_config_to_int(i))