import csv
import os
from classes import Node, Link, Agent, Network


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


def read_nodes(input_dir, network):
    # Read node info
    print('Read node.csv')

    with open(input_dir + '/node.csv', 'r', encoding='utf-8') as fp:
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


def read_links(input_dir, network):
    # Read link info
    print('\nRead link.csv')

    with open(input_dir + '/link.csv', 'r', encoding='utf-8') as fp:
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


def read_agents(input_dir, network):
    # Read agent info
    print("\nRead agent.csv")

    with open(input_dir + '/agent.csv', 'r', encoding='utf-8') as fp:
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


def read_network(input_dir='./input'):
    network = Network()
    read_nodes(input_dir, network)
    read_links(input_dir, network)
    read_agents(input_dir, network)

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

    agent.path_node_seq = ';'.join(str(x) for x in reversed(path_node_seq))

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

    agent.path_link_seq = ';'.join(str(x) for x in reversed(path_link_seq))
    agent.total_cost = total_cost
    agent.total_time = total_time
    agent.total_modified_cost = total_modified_cost

    if agent.total_time <= agent.time_threshold:
        agent.feasibility_flag = 1
    else:
        agent.feasibility_flag = 0

    return agent


def output_path_finding_results(agent):
    # Output_process

    if not os.path.isdir('./output'):
        os.mkdir('./output')
    output_dir = './output'

    with open(output_dir + '/agent_path.csv', 'w', newline='') as fp:
        writer = csv.writer(fp)

        line = ['agent_id', 'path_node_seq', 'path_link_seq', 'path_total_cost', 'path_total_time', 'time_threshold', 'lagrangian_multiplier']
        writer.writerow(line)

        line = [agent.agent_id, agent.path_node_seq, agent.path_link_seq, agent.total_cost, agent.total_time, agent.time_threshold, agent.lagrangian_multiplier]
        writer.writerow(line)

    print('\nThe results can be found in ' + os.path.join(os.getcwd(), '/output/agent_path.csv'))
