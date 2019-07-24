import os
import sys
import time

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY

sys.path.append(os.path.abspath('.'))

from config.parse_args import parse_args
from jenkins.jenkins import JenkinsCollector

if __name__ == "__main__":
    args = parse_args()
    port_number = int(args.port)
    jenkins_collector = JenkinsCollector(args.server, 
                                        args.user, 
                                        args.passwd, 
                                        args.insecure)

    print('Start run Jenkin exporter at server: {}'.format(args.server))

    REGISTRY.register(jenkins_collector)
    start_http_server(port_number)

    while True: 
        time.sleep(1)