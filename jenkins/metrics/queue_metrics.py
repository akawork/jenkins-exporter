
from prometheus_client.core import GaugeMetricFamily

def make_metrics(queue):

    list_metrics = []

    # Total items in Queue
    metric = GaugeMetricFamily('jenkins_queue_total',
                                'Total items in Queue',
                                labels = None)
    metric.add_metric(labels = [], 
                    value = queue.get_total_items())

    list_metrics.append(metric)

    # Duration of an item in Queue
    metric = GaugeMetricFamily('jenkins_queue_item_duration',
                                'Duration of a item in Queue in seconds',
                                labels = ['queue_id','item_name'])
    list_items = queue.get_list_items()
    for item_id in list_items:
        item = queue.get_item(item_id)
        item_name = item['name']
        queue_id = str(item_id)
        metric.add_metric(labels = [queue_id, item_name], 
                        value = queue.get_in_queue_duration(item_id))
                        
    list_metrics.append(metric)

    return list_metrics