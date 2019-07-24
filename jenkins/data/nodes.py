import re
import math

from datetime import datetime

API_SUFFIX = '/api/json'

NODE_SLAVE = 'hudson.slaves.SlaveComputer'
NODE_LABELS = 'totalExecutors,busyExecutors,\
computer[_class,displayName,offline,numExecutors,monitorData[*]]'
SWAP_SPACE_MONITOR = 'hudson.node_monitors.SwapSpaceMonitor'
SWAP_SPACE_LABELS = ['availablePhysicalMemory',
                    'availableSwapSpace',
                    'totalPhysicalMemory',
                    'totalSwapSpace']
TEMPORARY_SPACE_MONITOR = 'hudson.node_monitors.TemporarySpaceMonitor'
DISK_SPACE_MONITOR = 'hudson.node_monitors.DiskSpaceMonitor'
MONITOR_LABELS = ['availablePhysicalMemory',
                'availableSwapSpace',
                'totalPhysicalMemory',
                'totalSwapSpace',
                'temporarySpace',
                'diskSpace']

class Nodes(object):

    def __init__(self, jenkins):
        self.jenkins = jenkins
        list_nodes, node_info, executor_info = get_list_nodes(jenkins)
        self.list_nodes = list_nodes
        self.node_info = node_info
        self.executor_info = executor_info
        self.monitor_labels = []

    def get_list_nodes(self):
        return self.list_nodes
    
    def get_total_nodes(self):
        return len(self.list_nodes)

    def get_node(self, node_id):
        return self.node_info[node_id]

    def get_total_executors(self, node_type='all'):
        if node_type == 'all':
            return self.executor_info['total']
        count = 0
        
        for node_id in self.list_nodes:
            node = self.node_info[node_id]
            if node_type == 'slave':
                if node['master'] == False:
                    count += 1
            else:
                if node['master'] == True:
                    count += 1
        return count      

    def get_busy_executors(self):
        return self.executor_info['busy']

    def get_free_executors(self):
        return self.executor_info['free']

    def get_system_info(self, node_id, monitor_label):
        system_info = self.node_info[node_id]['system']
        return system_info[monitor_label]

    def is_online_node(self, node_id):
        return self.node_info[node_id]['online']

    # Count total node online
    def get_total_online_nodes(self):
        count = 0
        for node_id in self.list_nodes: 
            # node_id == node_info['display_name']
            node = self.node_info[node_id]
            if self.is_online_node(node_id):
                count += 1
        return count

    def get_total_offline_nodes(self):
        return self.get_total_nodes() - self.get_total_online_nodes()

    def get_monitor_labels(self):
        if len(self.monitor_labels) > 0:
            return self.monitor_labels
        labels = []
        for label in MONITOR_LABELS:
            labels.append(change_to_snake_case(label))
        self.monitor_labels = labels
        return self.monitor_labels

    def get_description(self, monitor_label):
        return re.sub('(\_)([a-z])', ' \\2', monitor_label)

    def get_type(self, node_id):
        node = self.node_info[node_id]
        if node['master']:
            return 'master'
        else:
            return 'slave'

# Create query to get all node
def make_query(jenkins):
    node_query_labels = NODE_LABELS

    tree = node_query_labels
    url = jenkins.server + '/computer' + API_SUFFIX
    params = {'tree': tree}
    return url, params

# Get all node
def get_list_nodes(jenkins):

    list_nodes = []
    node_info = {}
    executor_info = {}
    executor_info['total'] = 0
    executor_info['busy'] = 0
    executor_info['free'] = 0

    url, params = make_query(jenkins)
    response = jenkins.req.do_get(url=url, params=params)
    if response.status_code != 200:
        return list_nodes, node_info, executor_info

    raw_data = response.json()
    nodes = raw_data['computer']

    executor_info['total'] = raw_data['totalExecutors'] \
        if 'totalExecutors' in raw_data else 0
    executor_info['busy'] = raw_data['busyExecutors'] \
        if 'busyExecutors' in raw_data else 0
    executor_info['free'] = executor_info['total'] - executor_info['busy']
    
    for node in nodes:
        node_class = node['_class']
        node_name = node['displayName']
        node_master = True
        if is_slave(node_class):
            node_id = node_name
            node_master = False
        else:
            node_id = '(' + node_name + ')'
        list_nodes.append(node_id)
        node_info[node_id] = standardize_node_info(node=node, 
                                                master=node_master)

    return list_nodes, node_info, executor_info

def standardize_node_info(node, master):
    new_node = {}
    
    new_node['display_name'] = node['displayName']
    new_node['online'] = not(node['offline'])
    new_node['total_executors'] = node['numExecutors']
    new_node['master'] = master

    monitor_data_raw = node['monitorData']
    monitor_data = {}

    swap_space = monitor_data_raw[SWAP_SPACE_MONITOR]
    if swap_space is None:
        for swap_label in SWAP_SPACE_LABELS:
            key = change_to_snake_case(swap_label)
            monitor_data[key] = None
    else:
        for swap_label in SWAP_SPACE_LABELS:
            key = change_to_snake_case(swap_label)
            monitor_data[key] = swap_space[swap_label]

    temporary_space = monitor_data_raw[TEMPORARY_SPACE_MONITOR]
    if temporary_space is None:
        monitor_data['temporary_space'] = None
    else:
        monitor_data['temporary_space'] = temporary_space['size']

    disk_space = monitor_data_raw[DISK_SPACE_MONITOR]
    if disk_space is None:
        monitor_data['disk_space'] = None
    else:
        monitor_data['disk_space'] = disk_space['size']

    new_node['system'] = monitor_data

    return new_node

# Check node is slave or not
def is_slave(class_name):
    return class_name == NODE_SLAVE

# Check node is online or not
def is_online_node(node):
    return node['online']

# Convert from camelCase to snake_case 
def change_to_snake_case(camel):
    return re.sub('([A-Z])', '_\\1', camel).lower()

# Convert from camelCase to description 
def change_to_description(camel):
    return re.sub('([A-Z])', ' \\1', camel)


