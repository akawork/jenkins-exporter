import requests
import argparse
import json
import time
import ast
import re
import os
import sys
import math

from prometheus_client.core import GaugeMetricFamily, UntypedMetricFamily
from datetime import datetime
    
from lib.connection.connectionRequest import *
from cont.queue_cont import *
from cont.other_cont import *


def makeMetrics(collector):

    list_metrics = []

    req = HttpRequests(collector)
    #-------------------------------------Make usable data------------------------------------------------------------------------------
    # list_queue_items, list_queue_items_info: Danh sach queue items, thong tin truy xuat theo queue id
    list_queue_items, list_queue_items_info = getListQueueItems(req, collector)

    #---------------------------------------Make metric---------------------------------------------------------------------------------

    # metric_queue_items_total
    metric_queue_items_total = GaugeMetricFamily('jenkins_queue_total',
                                        'Tong so items trong Queue',
                                        labels = None)
    
    metric_queue_items_total.add_metric(labels = [], value = getTotalQueue(list_queue_items))

    list_metrics.append(metric_queue_items_total)

    # metric_queue_items_stuck
    metric_queue_items_stuck = GaugeMetricFamily('Jenkins_queue_items_stuck',
                                        'So luong item stuck',
                                        labels = None)
    items_stuck_total = getStuckItemsTotal(list_queue_items, list_queue_items_info)
    metric_queue_items_stuck.add_metric(labels = [], value = items_stuck_total)

    list_metrics.append(metric_queue_items_stuck)

    # metric_queue_items_blocked
    metric_queue_items_blocked = GaugeMetricFamily('Jenkins_queue_items_blocked',
                                        'So luong item blocked',
                                        labels = None)
    items_blocked_total = getBlockedItemsTotal(list_queue_items, list_queue_items_info)
    metric_queue_items_blocked.add_metric(labels = [], value = items_blocked_total)

    list_metrics.append(metric_queue_items_blocked)

    # # metric_queue_items_reason
    # metric_queue_items_reason = UntypedMetricFamily('jenkins_queue_items_reason',
    #                                     'Ly do item bi day vao trong Queue',
    #                                     labels = ['qid','itemname'])
    # for q_id in list_queue_items:
    #     item = list_queue_items_info[q_id]
    #     name = item['name']
    #     qid = str(q_id)
    #     metric_queue_items_reason.add_metric(labels = [qid,name], value = item['why'])

    # list_metrics.append(metric_queue_items_reason)

    # metric_queue_item_duration
    metric_queue_item_duration = GaugeMetricFamily('jenkins_queue_item_duration',
                                        'Thoi gian item trong Queue tinh theo giay',
                                        labels = ['qid','itemname'])
    for q_id in list_queue_items:
        item = list_queue_items_info[q_id]
        name = item['name']
        qid = str(q_id)
        time_in_queue = getInQueueTime(q_id, list_queue_items_info)
        metric_queue_item_duration.add_metric(labels = [qid,name], value = time_in_queue)

    list_metrics.append(metric_queue_item_duration)

    return list_metrics
#----------------------------------------Functions------------------------------------------------------------------------------------


# Tao query 
def makeQuery(collector):
    queue_query_labels = QUEUE_LABELS

    tree = TREE_PREFIX + queue_query_labels
    prefix = collector._server + '/queue' +API_SUFFIX
    query = prefix + tree
    return query

def isStuck(item):
    return item['stuck']

def isBlocked(item):
    return item['blocked']

# Dem so item stuck
def getStuckItemsTotal(list_queue_items, list_queue_items_info):
    count = 0
    for qid in list_queue_items:
        item = list_queue_items_info[qid]
        if isStuck(item):
            count += 1
    return count

# Dem so item blocked
def getBlockedItemsTotal(list_queue_items, list_queue_items_info):
    count = 0
    for qid in list_queue_items:
        item = list_queue_items_info[qid]
        if isBlocked(item):
            count += 1
    return count

# Tinh chenh lech giua 2 khoang timestamp theo giay
def getTimeDurationSecond(timestamp1, timestamp2):
    return math.fabs(timestamp2 - timestamp1)

# Lay ra timestamp hien tai
def getTimestampNow():
    return datetime.now().timestamp()

# Lay ra so luong item trong Queue
def getTotalQueue(list_queue_items):
    return len(list_queue_items)

# Tinh thoi gian trong Queue cua 1 job
def getInQueueTime(queue_id, list_queue_items_info):
    item = list_queue_items_info[queue_id]
    return item['inQueueTime']

# Chuyen ly do vao queue sang code
# def convertReason(reason):
#     in_progress = re.search(IN_PROGRESS,reason)
#     is_offline = re.search(OFFLINE)

#     if in_progress is not None:
#         return 0 # a build is already in progress
#     if is_offline is not None:
#         return 1 # node is offline
    

# Lay ra danh sach queue items
def getListQueueItems(req, collector):
    my_url = makeQuery(collector)
    response = req.getHttpResponse(my_url)
    if response.status_code != 200:
        return []

    list_queue_items = []
    list_queue_items_info = {}

    raw_data = response.json()
    items = raw_data['items']
    #'items[_class,blocked,buildable,id,inQueueSince,stuck,task[name],why]'
    for item in items:
        list_queue_items.append(item['id'])
        list_queue_items_info[item['id']] = standardizeItemInfo(item)
        
    return list_queue_items, list_queue_items_info

# Chuan hoa thong tin item
def standardizeItemInfo(item):
    item_info = {}
    item_info['_class'] = item['_class']
    item_info['blocked'] = item['blocked']
    item_info['buildable'] = item['buildable']
    item_info['id'] = item['id']
    item_info['inQueueTime'] = getTimeDurationSecond(item['inQueueSince']/1000,getTimestampNow())
    item_info['stuck'] = item['stuck']
    item_task = item['task']
    if 'name' in item_task:
        item_info['name'] = item_task['name']
    else:
        item_info['name'] = 'N/A'
    item_info['why'] = item['why']

    return item_info
