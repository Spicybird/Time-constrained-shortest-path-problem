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

    def update_link_modified_cost(self, lagrangian_multiplier):
        self.modified_cost = self.link_cost + lagrangian_multiplier * self.link_travel_time


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
        # self.total_modified_cost = 0  # =self.total_cost + Lagrangian_multiplier * (total_time - self.time_threshold)
        self.path_node_seq = ''
        self.path_link_seq = ''

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
        # # stores the current total travel time when traversing from the source node to all other node
        # self.node_traverse_time = []
        self.node_predecessor = []
        self.link_predecessor = []

    def update_link_modified_cost_of_the_network(self, lagrangian_multiplier):
        for link in self.link_list:
            link.update_link_modified_cost(lagrangian_multiplier)
