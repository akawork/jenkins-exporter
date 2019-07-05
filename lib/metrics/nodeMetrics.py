import requests
import argparse
import json
import time
import ast
import re
import os
import sys
import math

from sys import exit
from pprint import pprint
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily
from datetime import datetime   

from lib.connection.connectionRequest import *
from cont.node_cont import *
from cont.other_cont import *

def makeMetrics(collector):

    list_metrics = []
    req = HttpRequests(collector)
    #-------------------------------------Make usable data------------------------------------------------------------------------------
    # list_slaves, list_masters, list_slaves_info, list_masters_info: danh sach ten va info truy xuat theo ten cua cac node slave/master trong jenkins
    # total_executor, busy_executor: tong so executor va so executor ban
    list_slaves, list_masters, list_slaves_info, list_masters_info, total_executor, busy_executor = getListNode(req, collector)
    slaves_on = getNodesOn(list_slaves, list_slaves_info)
    master_on = getNodesOn(list_masters, list_masters_info)
    total_slaves = len(list_slaves)
    total_master = len(list_masters)

    #---------------------------------------Make metric---------------------------------------------------------------------------------
    # metric_total_node
    metric_total_node = GaugeMetricFamily('jenkins_nodes_total',
                                        'Tong so node trong Jenkins',
                                        labels = None)
    total_node = total_slaves + total_master
    metric_total_node.add_metric(labels = [], value = total_node)

    list_metrics.append(metric_total_node)

    # metric_total_node_slave
    metric_total_node_slave = GaugeMetricFamily('jenkins_nodes_slave_total',
                                        'Tong so node slave trong Jenkins',
                                        labels = None)
    metric_total_node_slave.add_metric(labels = [], value = total_slaves)

    list_metrics.append(metric_total_node)

    # metric_total_node_master
    metric_total_node_master = GaugeMetricFamily('jenkins_nodes_master_total',
                                        'Tong so node master trong Jenkins',
                                        labels = None)
    metric_total_node_master.add_metric(labels = [], value = total_master)

    list_metrics.append(metric_total_node)

    # metric_total_node_on
    metric_total_node_on = GaugeMetricFamily('jenkins_nodes_on_total',
                                        'Tong so node online trong Jenkins',
                                        labels = None)
    total_node_on = slaves_on + master_on
    metric_total_node_on.add_metric(labels = [], value = total_node_on)

    list_metrics.append(metric_total_node_on)

    # metric_total_node_off
    metric_total_node_off = GaugeMetricFamily('jenkins_nodes_off_total',
                                        'Tong so node offline trong Jenkins',
                                        labels = None)
    total_node_off = total_node - (slaves_on + master_on)
    metric_total_node_off.add_metric(labels = [], value = total_node_off)

    list_metrics.append(metric_total_node_off)

    # metric_executor_total
    metric_executor_total = GaugeMetricFamily('jenkins_executors_total',
                                        'Tong so executor trong Jenkins',
                                        labels = None)
    metric_executor_total.add_metric(labels = [], value = total_executor)

    list_metrics.append(metric_executor_total)

    # metric_test_slave_executor_total
    metric_test_slave_executor_total = GaugeMetricFamily('jenkins_executors_slave_total',
                                        'Tong so executor cua cac may slave trong Jenkins',
                                        labels = None)
    count_slave_executor = 0
    for name in list_slaves:
        if isOn(list_slaves_info[name]):
            count_slave_executor += list_slaves_info[name]['numExecutors']
    metric_test_slave_executor_total.add_metric(labels = [], value = count_slave_executor)

    list_metrics.append(metric_test_slave_executor_total)

    # metric_test_master_executor_total
    metric_test_master_executor_total = GaugeMetricFamily('jenkins_executors_master_total',
                                        'Tong so executor cua cac may master trong Jenkins',
                                        labels = None)
    count_master_executor = 0
    for name in list_masters:
        if isOn(list_masters_info[name]):
            count_master_executor += list_masters_info[name]['numExecutors']
    metric_test_master_executor_total.add_metric(labels = [], value = count_master_executor)

    list_metrics.append(metric_test_master_executor_total)

    # metric_executor_busy
    metric_executor_busy = GaugeMetricFamily('jenkins_executors_busy',
                                        'Tong so executor busy trong Jenkins',
                                        labels = None)
    metric_executor_busy.add_metric(labels = [], value = busy_executor)

    list_metrics.append(metric_executor_busy)

    # metric_executor_free
    metric_executor_free = GaugeMetricFamily('jenkins_executors_free',
                                        'Tong so executor busy trong Jenkins',
                                        labels = None)
    metric_executor_free.add_metric(labels = [], value = total_executor - busy_executor)

    list_metrics.append(metric_executor_free)

    # monitor metrics group
    list_monitor_labels = MONITOR_LABELS #'availablePhysicalMemory','availableSwapSpace','totalPhysicalMemory','totalSwapSpace','temporarySpace','diskSpace'
    for mlabel in list_monitor_labels:
        monitor_metric_name =  changeToSnakeCase(mlabel)
        monitor_metric_description  = changeToDescription(mlabel)
        metric_monitor = GaugeMetricFamily('jenkins_node_{}'.format(monitor_metric_name),
                                            'Thong tin {} cua mot node'.format(monitor_metric_description),
                                            labels = ['class','node'])
        for name in list_slaves:
            monitor_data = getMonitorData(list_slaves_info[name],mlabel)
            metric_monitor.add_metric(labels = ['slave',name], value = monitor_data)

        for name in list_masters:
            monitor_data = getMonitorData(list_masters_info[name],mlabel)
            metric_monitor.add_metric(labels = ['master',name], value = monitor_data)

        list_metrics.append(metric_monitor)

    return list_metrics


#------------------------------------------Functions------------------------------------------------------------------------------


#
def getMonitorData(node, mlabel):
    monitor_data = node['monitorData']
    if monitor_data[mlabel] is None:
        return 0
    else:
        return monitor_data[mlabel]


# Chuyen doi camelCase sang snake_case 
def changeToSnakeCase(camel):
    return re.sub('([A-Z])', '_\\1', camel).lower()

# Chuyen doi camelCase sang description 
def changeToDescription(camel):
    return re.sub('([A-Z])', ' \\1', camel)

# Dem so luong node on
def  getNodesOn(list_nodes, list_nodes_info):
    count = 0
    for node_name in list_nodes:
        if isOn(list_nodes_info[node_name]):
            count += 1
    return count

# Tao query lay tat ca thong tin cac node
def makeQuery(collector):
    node_query_labels = NODE_LABELS

    tree = TREE_PREFIX + node_query_labels
    prefix = collector._server + '/computer' +API_SUFFIX
    query = prefix + tree
    return query

# Check node la slave hay khong
def isSlave(class_name):
    return class_name == NODE_SLAVE

# Check node on hay khong
def isOn(node):
    return node['online']

# Lay ra danh sach node
def getListNode(req, collector):
    my_url = makeQuery(collector)
    response = req.getHttpResponse(my_url)
    if response.status_code != 200:
        return []

    list_slaves = []
    list_masters = []
    list_slaves_info = {}
    list_masters_info = {}

    raw_data = response.json()
    nodes = raw_data['computer']

    total_executor = raw_data['totalExecutors']
    busy_executor = raw_data['busyExecutors']
    
    for node in nodes:
        node_class = node['_class']
        node_name = node['displayName']
        if isSlave(node_class):
            list_slaves.append(node_name)
            list_slaves_info[node_name] = standardizeNodeInfo(node)
        else:
            list_masters.append(node_name)
            list_masters_info[node_name] = standardizeNodeInfo(node)
        
    return list_slaves, list_masters, list_slaves_info, list_masters_info, total_executor, busy_executor

# Chuan hoa thong tin node
def standardizeNodeInfo(node):
    new_node = {}
    
    new_node['name'] = node['displayName']
    new_node['online'] = not(node['offline'])
    new_node['numExecutors'] = node['numExecutors']

    monitor_data_raw = node['monitorData']
    monitor_data = {}

    swap_space = monitor_data_raw[SWAP_SPACE_MONITOR]
    if swap_space is None:
        for mlabel in MONITOR_LABELS:
            monitor_data[mlabel] = None
    else:
        for swap_label in SWAP_SPACE_LABELS:
            monitor_data[swap_label] = swap_space[swap_label]

    temporary_space = monitor_data_raw[TEMPORARY_SPACE_MONITOR]
    if temporary_space is None:
        monitor_data['temporarySpace'] = None
    else:
        monitor_data['temporarySpace'] = temporary_space['size']

    disk_space = monitor_data_raw[DISK_SPACE_MONITOR]
    if disk_space is None:
        monitor_data['diskSpace'] = None
    else:
        monitor_data['diskSpace'] = disk_space['size']

    new_node['monitorData'] = monitor_data

    return new_node

# def convertRawData(req):
#     my_url = VIEW_SOURCE + req._collector._server
#     response = req.getHttpResponse(my_url)
#     if response.status_code != 200:
#         return []
#     buildExecutorStatus = re.search()