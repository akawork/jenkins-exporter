import os
import sys

sys.path.append(os.path.abspath('.'))

from jenkins.data.jobs import Jobs
from jenkins.data.queue import Queue
from jenkins.data.nodes import Nodes

from jenkins.metrics import job_metrics, node_metrics, queue_metrics

from jenkins.connection.api_connection import APIConnection

class Jenkins(object):

    def __init__(self, server, auth, insecure=True):
        self.server = server
        self.auth = auth
        self.req = APIConnection(server, auth)
        self.jobs = Jobs(self)
        self.queue = Queue(self)
        self.nodes = Nodes(self)


class JenkinsCollector(object):

    def __init__(self, server, user, passwd, insecure=False):
        self.server = server
        self.insecure = insecure
        self.auth = (user, passwd)


    def collect(self):
        jenkins = Jenkins(server=self.server,
                            auth=self.auth,
                            insecure=True)

        jenkins_metrics = JenkinsMetrics(jenkins)
        metrics = jenkins_metrics.make_metrics()

        for metric in metrics:
            yield metric



class JenkinsMetrics(object):

    def __init__(self, jenkins):
        self.jenkins = jenkins
        self.metrics = []

    def make_metrics(self):
        metrics = []

        metrics += job_metrics.make_metrics(self.jenkins.jobs)
        metrics += node_metrics.make_metrics(self.jenkins.nodes)
        metrics += queue_metrics.make_metrics(self.jenkins.queue)

        self.metrics = metrics

        return self.metrics
