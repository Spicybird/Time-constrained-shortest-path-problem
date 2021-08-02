from utils import read_network, retrieve_one_to_one_shortest_path_info, output_path_finding_results
from path import single_source_shortest_path_deque

# Read input data
input_dir = './input'
network = read_network(input_dir)

# Assume that we only solve one agent, you can easily extend it to the situation in which we
# find time-constrained shortest path for several agents
agent = network.agent_list[0]

origin_node_id = agent.origin_node_id
origin_node_seq_no = agent.origin_node_seq_no
destination_node_id = agent.destination_node_id  # one-to-one time constrained shortest path problem

iter_num = 1
max_iter_num = 10

step_size = 1
while iter_num <= max_iter_num:
    network.update_link_modified_cost_of_the_network(agent.lagrangian_multiplier)

    network = single_source_shortest_path_deque(network, origin_node_id)

    agent = retrieve_one_to_one_shortest_path_info(network, agent.origin_node_id, agent.destination_node_id, agent)
    agent.update_sub_gradient()
    agent.update_langrangian_multiplier(step_size)

    iter_num += 1
    step_size = 1.0 / iter_num

output_path_finding_results(agent)
