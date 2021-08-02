import collections
import csv

""" global constant """
# for shortest path finding
MAX_LABEL_COST = 999999


def _convert_str_to_int(str):
    """
    TypeError will take care the case that str is None
    ValueError will take care the case that str is empty
    """
    if not str:
        return None

    try:
        return int(str)
    except ValueError:
        return int(float(str))
    except TypeError:
        return None


def _convert_str_to_float(str):
    """
    TypeError will take care the case that str is None
    ValueError will take care the case that str is empty
    """
    if not str:
        return None

    try:
        return float(str)
    except (TypeError, ValueError):
        return None


class Node:
    def __init__(self, node_id, node_seq_no):
        self.node_id = node_id
        self.node_seq_no = node_seq_no
        self.outgoing_link_list = []
        self.incoming_link_list = []
        self.coord_x = ''
        self.coord_y = ''
        self.zone_id = ''
        self.geometry = ''


class Link:
    def __init__(self, link_id, link_seq_no, from_node_id, to_node_id, from_node_seq_no, to_node_seq_no, link_cost, link_travel_time):
        self.link_id = link_id
        self.link_seq_no = link_seq_no
        self.from_node_id = from_node_id
        self.to_node_id = to_node_id
        self.from_node_seq_no = from_node_seq_no
        self.to_node_seq_no = to_node_seq_no
        self.link_cost = link_cost
        self.link_travel_time = link_travel_time
        self.modified_cost = 0  # = link_cost + lagrangian_multiplier * link_travel_time
        self.geometry = ''


class Agent:
    def __init__(self, agent_id, origin_node_id, destination_node_id, origin_node_seq_no, destination_node_seq_no, time_threshold):
        self.agent_id = agent_id
        self.origin_node_id = origin_node_id
        self.destination_node_id = destination_node_id
        self.origin_node_seq_no = origin_node_seq_no
        self.destination_node_seq_no = destination_node_seq_no
        self.time_threshold = time_threshold

        self.lagrangian_multiplier = 0
        self.sub_gradient = 0

        self.total_cost = 0
        self.total_time = 0
        self.total_modified_cost = 0  # =total_cost + Lagrangian_multiplier * total_time
        self.path_node_seq = []
        self.path_link_seq = []

        # 0: infeasible 1: feasible
        self.feasibility_flag = 0

    def update_sub_gradient(self):
        self.sub_gradient = self.total_time - self.time_threshold

    def update_langrangian_multiplier(self, step_size):
        self.lagrangian_multiplier += step_size * self.sub_gradient
        if self.lagrangian_multiplier < 0:
            self.lagrangian_multiplier = 0


class Network:
    def __init__(self):
        self.node_list = []
        self.link_list = []
        self.agent_list = []
        self.node_size = 0
        self.link_size = 0
        self.agent_size = 0
        self.node_id_to_no_dict = {}
        self.node_no_to_id_dict = {}
        self.link_id_to_no_dict = {}
        self.link_no_to_id_dict = {}
        self.zone_to_nodes_dict = {}
        self.node_label_cost = []
        # stores the current total travel time when traversing from the source node to all other node
        self.node_traverse_time = []
        self.node_predecessor = []
        self.link_predecessor = []


network = Network()
# Read input data
input_dir = './input'

# Read node info
with open(input_dir + '/node.csv', 'r', encoding='utf-8') as fp:
    print('Read node.csv')

    reader = csv.DictReader(fp)
    node_seq_no = 0
    for line in reader:
        node_id = _convert_str_to_int(line['node_id'])
        if node_id is None:
            continue

        node = Node(node_id, node_seq_no)

        network.node_list.append(node)
        network.node_id_to_no_dict[node_id] = node_seq_no
        network.node_no_to_id_dict[node_seq_no] = node_id

        node_seq_no += 1

    print(f"Number of nodes is: {node_seq_no}")
    network.node_size = node_seq_no

# Read link info
with open(input_dir + '/link.csv', 'r', encoding='utf-8') as fp:
    print('\nRead link.csv')

    reader = csv.DictReader(fp)
    link_seq_no = 0
    for line in reader:
        link_id = _convert_str_to_int(line['link_id'])
        if link_id is None:
            continue

        from_node_id = _convert_str_to_int(line['from_node_id'])
        if from_node_id is None:
            continue

        to_node_id = _convert_str_to_int(line['to_node_id'])
        if to_node_id is None:
            continue

        from_node_seq_no = network.node_id_to_no_dict[from_node_id]
        to_node_seq_no = network.node_id_to_no_dict[to_node_id]

        link_cost = _convert_str_to_float(line['link_cost'])
        link_travel_time = _convert_str_to_float(line['link_travel_time'])

        link = Link(link_id, link_seq_no, from_node_id, to_node_id, from_node_seq_no, to_node_seq_no, link_cost, link_travel_time)

        network.link_list.append(link)
        network.node_list[from_node_seq_no].outgoing_link_list.append(link)
        network.node_list[to_node_seq_no].incoming_link_list.append(link)

        network.link_id_to_no_dict[link_id] = link_seq_no
        network.link_no_to_id_dict[link_seq_no] = link_id

        link_seq_no += 1

    print(f"Number of links is: {link_seq_no}")
    network.link_size = link_seq_no

# Read agent info
with open(input_dir + '/agent.csv', 'r', encoding='utf-8') as fp:
    print("\nRead agent.csv")

    reader = csv.DictReader(fp)
    agent_num = 0
    for line in reader:
        agent_id = _convert_str_to_int(line['agent_id'])

        origin_node_id = _convert_str_to_int(line['origin_node_id'])
        if origin_node_id is None:
            continue

        destination_node_id = _convert_str_to_int(line['destination_node_id'])
        if destination_node_id is None:
            continue

        origin_node_seq_no = network.node_id_to_no_dict[origin_node_id]
        destination_node_seq_no = network.node_id_to_no_dict[destination_node_id]

        time_threshold = _convert_str_to_float(line['time_threshold'])

        agent = Agent(agent_id, origin_node_id, destination_node_id, origin_node_seq_no, destination_node_seq_no, time_threshold)
        network.agent_list.append(agent)
        agent_num += 1

    network.agent_size = agent_num
    print(f"The number of agents is: {agent_num}")

# #############################################################
# # Deque implementation of modified label-correcting algorithm
# # Deque MLC Algo
#
# origin_node_id = agent.origin_node_id
# origin_node_seq_no = agent.origin_node_seq_no
# destination_node_id = 6  # one-to-one time constrained shortest path problem
#
# # Step 1: initialization
# network.node_label_cost = [MAX_LABEL_COST] * network.node_size
# network.node_label_cost[origin_node_seq_no] = 0
#
# network.node_predecessor = [-1] * network.node_size
# network.link_predecessor = [-1] * network.link_size
#
# SEList = collections.deque()
# SEList.append(origin_node_seq_no)
#
# node_status = [0] * network.node_size
# node_status[origin_node_seq_no] = 1
#
# while SEList:
#     from_node_seq_no = SEList.popleft()
#     from_node_label_cost = network.node_label_cost[from_node_seq_no]
#
#     node_status[from_node_seq_no] = 2
#     for link in network.node_list[from_node_seq_no].outgoing_link_list:
#         to_node_seq_no = link.to_node_seq_no
#         new_to_node_cost = from_node_label_cost + link.link_cost
#         if new_to_node_cost < network.node_label_cost[to_node_seq_no]:
#             network.node_label_cost[to_node_seq_no] = new_to_node_cost
#             network.node_predecessor[to_node_seq_no] = from_node_seq_no
#             network.link_predecessor[to_node_seq_no] = link.link_seq_no
#             if node_status[to_node_seq_no] != 1:
#                 if node_status[to_node_seq_no] == 0:
#                     SEList.append(to_node_seq_no)
#                 elif node_status[to_node_seq_no] == 2:
#                     SEList.appendleft(to_node_seq_no)
#                 node_status[to_node_seq_no] = 1
#
# print(f"Node label cost: {network.node_label_cost}")
# print(f"Node predecessor: {network.node_predecessor}")
# #############################################################

# construct the Lagrangian problem
# for link in network.link_list:
#     link.modified_cost = link.link_cost + agent.lagrangian_multiplier * link.link_travel_time

iter = 1
max_iter_num = 3

origin_node_id = agent.origin_node_id
origin_node_seq_no = agent.origin_node_seq_no
destination_node_id = agent.destination_node_id  # one-to-one time constrained shortest path problem


def single_source_shortest_path_deque(network, origin_node_id):
    # Deque implementation of modified label-correcting algorithm
    origin_node_seq_no = network.node_id_to_no_dict[origin_node_id]

    # Step 1: initialization
    network.node_label_cost = [MAX_LABEL_COST] * network.node_size
    network.node_label_cost[origin_node_seq_no] = 0

    network.node_predecessor = [-1] * network.node_size
    network.link_predecessor = [-1] * network.link_size

    SEList = collections.deque()
    SEList.append(origin_node_seq_no)

    node_status = [0] * network.node_size
    node_status[origin_node_seq_no] = 1

    while SEList:
        from_node_seq_no = SEList.popleft()
        from_node_label_cost = network.node_label_cost[from_node_seq_no]

        node_status[from_node_seq_no] = 2
        for link in network.node_list[from_node_seq_no].outgoing_link_list:
            to_node_seq_no = link.to_node_seq_no
            new_to_node_cost = from_node_label_cost + link.modified_cost
            if new_to_node_cost < network.node_label_cost[to_node_seq_no]:
                network.node_label_cost[to_node_seq_no] = new_to_node_cost
                network.node_predecessor[to_node_seq_no] = from_node_seq_no
                network.link_predecessor[to_node_seq_no] = link.link_seq_no
                if node_status[to_node_seq_no] != 1:
                    if node_status[to_node_seq_no] == 0:
                        SEList.append(to_node_seq_no)
                    elif node_status[to_node_seq_no] == 2:
                        SEList.appendleft(to_node_seq_no)
                    node_status[to_node_seq_no] = 1
    return network


def retrieve_one_to_one_shortest_path_info(network, origin_node_id, destination_node_id, agent):
    # info: node seq, link seq, total cost, total time, feasibility flag, total modified cost
    path_node_seq = []
    path_link_seq = []

    total_cost = 0
    total_time = 0
    total_modified_cost = 0

    current_node_seq_no = network.node_id_to_no_dict[destination_node_id]
    current_node_id = destination_node_id
    while current_node_seq_no >= 0:
        path_node_seq.append(current_node_id)
        current_node_seq_no = network.node_predecessor[current_node_seq_no]
        try:
            current_node_id = network.node_no_to_id_dict[current_node_seq_no]
        except KeyError:
            pass

    agent.path_node_seq = [node_id for node_id in reversed(path_node_seq)]

    # retrieve path link sequence and calculate path total cost, total time and total modified cost
    current_node_seq_no = network.node_id_to_no_dict[destination_node_id]
    current_link_seq_no = network.link_predecessor[current_node_seq_no]
    current_link_id = network.link_no_to_id_dict[current_link_seq_no]
    while current_link_seq_no >= 0:
        path_link_seq.append(current_link_id)

        total_cost += network.link_list[current_link_seq_no].link_cost
        total_time += network.link_list[current_link_seq_no].link_travel_time
        total_modified_cost += network.link_list[current_link_seq_no].modified_cost

        current_node_seq_no = network.node_predecessor[current_node_seq_no]
        current_link_seq_no = network.link_predecessor[current_node_seq_no]
        try:
            current_link_id = network.link_no_to_id_dict[current_link_seq_no]
        except KeyError:
            pass

    agent.path_link_seq = [link_id for link_id in reversed(path_link_seq)]
    agent.total_cost = total_cost
    agent.total_time = total_time
    agent.total_modified_cost = total_modified_cost

    if agent.total_time <= agent.time_threshold:
        agent.feasibility_flag = 1
    else:
        agent.feasibility_flag = 0

    return agent


step_size = 1
while iter <= max_iter_num:
    for link in network.link_list:
        link.modified_cost = link.link_cost + agent.lagrangian_multiplier * link.link_travel_time
    network = single_source_shortest_path_deque(network, origin_node_id)

    agent = retrieve_one_to_one_shortest_path_info(network, agent.origin_node_id, agent.destination_node_id, agent)
    agent.update_sub_gradient()
    agent.update_langrangian_multiplier(step_size)

    iter += 1
    step_size = 1.0 / iter
