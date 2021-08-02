# from main import MAX_LABEL_COST
import collections

""" global constant """
# for shortest path finding
MAX_LABEL_COST = 999999


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
