
from prometheus_client.core import GaugeMetricFamily

def make_metrics(nodes):

    list_metrics = []

    # Total nodes in Jenkins
    metric = GaugeMetricFamily('jenkins_nodes_total',
                                'Total nodes in Jenkins',
                                labels=None)
    metric.add_metric(labels=[], 
                    value=nodes.get_total_nodes())

    list_metrics.append(metric)

    # Total online nodes
    metric = GaugeMetricFamily('jenkins_nodes_online_total',
                                'Total online nodes in Jenkins',
                                labels=None) 
    metric.add_metric(labels=[], 
                    value=nodes.get_total_online_nodes())

    list_metrics.append(metric)

    # Total offline nodes
    metric = GaugeMetricFamily('jenkins_nodes_offline_total',
                                'Total offline nodes in Jenkins',
                                labels=None)
    metric.add_metric(labels=[], 
                    value=nodes.get_total_offline_nodes())

    list_metrics.append(metric)

    # Total executors in Jenkins
    metric = GaugeMetricFamily('jenkins_executors_total',
                                'Total executors in Jenkins',
                                labels=None)
    metric.add_metric(labels=[], 
                    value=nodes.get_total_executors())

    list_metrics.append(metric)

    # Total executor of slaves in Jenkins
    metric = GaugeMetricFamily('jenkins_slave_executors_total',
                                'Total executor of slaves in Jenkins',
                                labels=None)
    metric.add_metric(labels=[], 
                    value=nodes.get_total_executors(node_type='slave'))

    list_metrics.append(metric)

    # Total executor of master in Jenkins
    metric = GaugeMetricFamily('jenkins_master_executors_total',
                                'Total executor of master in Jenkins',
                                labels=None)
    metric.add_metric(labels=[], 
                    value=nodes.get_total_executors(node_type='master'))

    list_metrics.append(metric)

    # Total busy executor
    metric = GaugeMetricFamily('jenkins_executors_busy',
                                'Total busy executor in Jenkins',
                                labels=None)
    metric.add_metric(labels=[], 
                    value=nodes.get_busy_executors())

    list_metrics.append(metric)

    # Total free executor
    metric = GaugeMetricFamily('jenkins_executors_free',
                                'Total free executor in Jenkins',
                                labels=None)
    metric.add_metric(labels=[], 
                    value=nodes.get_free_executors())

    list_metrics.append(metric)

    # monitor metrics group
    list_monitor_labels = nodes.get_monitor_labels()
    list_nodes = nodes.get_list_nodes()
    for mlabel in list_monitor_labels:
        description = nodes.get_description(mlabel)
        metric = GaugeMetricFamily('jenkins_node_{}'.format(mlabel),
                            'Metric {} of a node'.format(description),
                            labels=['node_type','node'])
        for node_id in list_nodes:
            if nodes.is_online_node(node_id) == False:
                continue
            monitor_data = nodes.get_system_info(node_id, mlabel)
            if monitor_data is None:
                continue
            node_type = nodes.get_type(node_id)
            metric.add_metric(labels=[node_type, node_id], value=monitor_data)
            
        list_metrics.append(metric)

    return list_metrics