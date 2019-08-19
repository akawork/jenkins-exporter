import os
import sys
import time
import configparser

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from jenkins.jenkins import JenkinsCollector

if __name__ == "__main__":
    # Import configuration file
    config = configparser.ConfigParser()
    config.read("config.ini")
    collector = JenkinsCollector(
        server=config['DEFAULT']['JENKINS_SERVER'],
        user=config['DEFAULT']['JENKINS_USERNAME'],
        passwd=config['DEFAULT']['JENKINS_PASSWORD']
    )
    REGISTRY.register(collector)
    start_http_server(9118)
    while True:
        time.sleep(1)
