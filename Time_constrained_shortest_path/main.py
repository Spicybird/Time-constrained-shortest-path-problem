from utils import read_network
from utils import retrieve_one_to_one_shortest_path_info
from utils import output_path_finding_results
from utils import output_gap_info
from path import single_source_shortest_path_deque
import matplotlib.pyplot as plt
import os

# Read input data
input_dir = './input'
network = read_network(input_dir)

# Assume that we only solve one agent, you can easily extend it to the situation in which we
# find time-constrained shortest path for several agents
agent = network.agent_list[0]

origin_node_id = agent.origin_node_id
origin_node_seq_no = agent.origin_node_seq_no
destination_node_id = agent.destination_node_id  # one-to-one time constrained shortest path problem

# global upper bound value
global_upper_bound = 99999

# global lower bound value
global_lower_bound = -99999

gap = global_upper_bound - global_lower_bound

iter_num = 0
step_size = 1

iter_list = []
g_ub_list = []
g_lb_list = []
lag_multiplier_list = []
path_list = []

while gap > 0.001:
    network.update_link_modified_cost_of_the_network(agent.lagrangian_multiplier)

    network = single_source_shortest_path_deque(network, origin_node_id)

    agent = retrieve_one_to_one_shortest_path_info(network, agent.origin_node_id, agent.destination_node_id, agent)

    local_lower_bound = agent.total_modified_cost - agent.lagrangian_multiplier * agent.time_threshold
    global_lower_bound = max(global_lower_bound, local_lower_bound)

    if agent.feasibility_flag == 1:
        global_upper_bound = min(global_upper_bound, agent.total_cost)

    gap = global_upper_bound - global_lower_bound

    agent.update_sub_gradient()
    agent.update_langrangian_multiplier(step_size)

    iter_list.append(iter_num)
    g_ub_list.append(global_upper_bound)
    g_lb_list.append(global_lower_bound)
    lag_multiplier_list.append(agent.lagrangian_multiplier)
    path_list.append(agent.path_node_seq)

    iter_num += 1
    step_size = 1.0 / iter_num

output_path_finding_results(agent)

output_gap_info(iter_list, g_ub_list, g_lb_list, lag_multiplier_list)

print("\nThe result:")
print(f"iter_list:\n {iter_list}")
print(f"g_ub_list:\n {g_ub_list}")
print(f"g_lb_list:\n {g_lb_list}")
print(f"lag_multiplier_list:\n {lag_multiplier_list}")
print(f"path_list (node id sequence):\n {path_list}")

if not os.path.isdir('./output'):
    os.mkdir('./output')
output_dir = './output'

plt.plot(iter_list[1:], g_lb_list[1:], scalex=iter_list)
plt.plot(iter_list[1:], g_ub_list[1:], scalex=iter_list)
plt.title("Evolution curve")
plt.xlabel("Iter number")
plt.ylabel("Bound value")
plt.xticks(list(range(1, iter_num)))
plt.grid()
plt.legend(['LB', 'UB'])
plt.savefig(output_dir + '/bound_evolution_curve.png')
plt.savefig(output_dir + '/bound_evolution_curve.svg')
plt.show()
