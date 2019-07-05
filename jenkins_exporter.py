import requests
import argparse
import time
import ast
import os
import sys

from requests.auth import HTTPBasicAuth
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY

sys.path.append(os.path.abspath('.'))

import lib.metrics.jobMetrics as jobMetrics
import lib.metrics.nodeMetrics as nodeMetrics
import lib.metrics.queueMetrics as queueMetrics

from etc.parse_args import parse_args

class JenkinsCollector(object):

    def __init__(self, server, user, passwd, insecure):
        self._server = server
        self._user = user
        self._passwd = passwd
        self._insecure = insecure


#########################################################################################################################################
#-------------------------------------------Function collet start------------------------------------------------------------------------

    def collect(self):
        job_metrics = jobMetrics.makeMetrics(self)
        node_metrics = nodeMetrics.makeMetrics(self)
        queue_metrics = queueMetrics.makeMetrics(self)

        for metric in job_metrics:
            yield metric
        
        for metric in node_metrics:
            yield metric

        for metric in queue_metrics:
            yield metric

        

#-------------------------------------------Function collet end--------------------------------------------------------------------------
#########################################################################################################################################

if __name__ == "__main__":
    args = parse_args()
    portNumber = int(args.port)
    print('Start run Jenkin exporter at server: {}'.format(args.server))
    REGISTRY.register(JenkinsCollector(args.server, args.user, args.passwd, args.insecure))
    start_http_server(portNumber)
    while True: 
        time.sleep(1)