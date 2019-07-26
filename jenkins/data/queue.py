import re
import math

from datetime import datetime

API_SUFFIX = '/api/json'

QUEUE_LABELS = \
    'items[_class,blocked,buildable,id,inQueueSince,stuck,task[name],why]'
IN_PROGRESS = 'is already in progress'
OFFLINE = 'is offline'
BLOCKED_ITEM = 'hudson.model.Queue$BlockedItem'
BUILDABLE_ITEM = 'hudson.model.Queue$BuildableItem'

class Queue(object):

    def __init__(self, jenkins):
        self.jenkins = jenkins
        self.list_items, self.item_info = get_list_queue_items(jenkins)

    def get_total_items(self):
        return len(self.list_items)

    def get_list_items(self):
        return self.list_items

    def get_item(self, item_id):
        return self.item_info[item_id]

    def get_in_queue_duration(self, item_id):
        item = self.item_info[item_id]
        return item['in_queue_duration']

# Create query to get all item in queue
def make_query(jenkins):
    queue_query_labels = QUEUE_LABELS

    tree = queue_query_labels
    url = jenkins.server + '/queue' +API_SUFFIX
    params = {'tree': tree}
    return url, params

# Get all item in queue
def get_list_queue_items(jenkins):

    list_items = []
    item_info = {}

    url, params = make_query(jenkins)
    response = jenkins.req.do_get(url=url, params=params)
    if response.status_code != 200:
        return list_items, item_info

    raw_data = response.json()
    items = raw_data['items']
    #'items[_class,blocked,buildable,id,inQueueSince,stuck,task[name],why]'
    for item in items:
        item_id = item['id']
        list_items.append(item_id)
        item_info[item_id] = standardize_item_info(item)
        
    return list_items, item_info

def standardize_item_info(item):
    new_item = {}

    new_item['blocked'] = item['blocked']
    new_item['buildable'] = item['buildable']
    new_item['queue_id'] = item['id']
    new_item['in_queue_duration'] = \
        get_time_duration_second(item['inQueueSince']/1000, \
                                get_now_timestamp())
    new_item['stuck'] = item['stuck']

    item_task = item['task']
    new_item['name'] = item_task['name'] if 'name' in item_task else 'N/A'

    return new_item

# Calculate the duration between two time points,
# returning the number of seconds
def get_time_duration_second(timestamp1, timestamp2):
    return math.fabs(timestamp2 - timestamp1)

# Get current timestamp 
def get_now_timestamp():
    return datetime.now().timestamp()
