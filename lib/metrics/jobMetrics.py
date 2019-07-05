import requests
import argparse
import json
import time
import ast
import re
import os
import sys
import math

from prometheus_client.core import GaugeMetricFamily
from datetime import datetime
    
from lib.connection.connectionRequest import *
from cont.job_cont import *
from cont.other_cont import *


def makeMetrics(collector):

    list_metrics = []

    req = HttpRequests(collector)
    #-------------------------------------Make usable data------------------------------------------------------------------------------
    # list_jobs: Danh sach cac job va thong tin cua chung
    # total_jobs: Tong so luong pipeline
    # list_builds: Danh sach thong tin build cua tung job
    # list_last_builds: Danh sach thong tin lan build cuoi cua tung job
    total_jobs, list_jobs, list_builds, list_last_builds = getListJobs(req, collector)

    #---------------------------------------Make metric---------------------------------------------------------------------------------
    # metric_total_jobs
    metric_total_jobs = GaugeMetricFamily('jenkins_jobs_total',
                                        'Tong so job trong Jenkins',
                                        labels = None)
    metric_total_jobs.add_metric(labels = [], value = total_jobs)
    
    list_metrics.append(metric_total_jobs)

    # metric_total_builds
    metric_total_builds = GaugeMetricFamily('jenkins_jobs_build_total',
                                        'Tong so lan build trong pipeline',
                                        labels = ['jobname'])
    for job in list_jobs:
        job_name = job['name']
        metric_total_builds.add_metric(labels = [job_name], value = list_builds[job_name]['total'])

    list_metrics.append(metric_total_builds)

    # metric_job_fail_continuous
    metric_job_fail_continuous = GaugeMetricFamily('jenkins_job_fail_continuous',
                                        'So lan build fail lien tiep gan nhat trong pipeline',
                                        labels = ['jobname'])
    for job in list_jobs:
        job_name = job['name']
        total_fail = getTotalFail(job, list_builds)
        metric_job_fail_continuous.add_metric(labels = [job_name], value = total_fail)

    list_metrics.append(metric_job_fail_continuous)

    # metric_total_jobs_building
    metric_total_jobs_building = GaugeMetricFamily('jenkins_jobs_building_total',
                                        'Tong so luong job dang build',
                                        labels = None)
    total_building_jobs = getTotalBuildingJobs(list_jobs, list_last_builds)
    metric_total_jobs_building.add_metric(labels = [], value = total_building_jobs)

    list_metrics.append(metric_total_jobs_building)

    # metric_time_building_job
    metric_time_building_job = GaugeMetricFamily('jenkins_jobs_building_time_seconds',
                                        'Thoi gian da chay cua job dang build tinh theo giay',
                                        labels = ['jobname'])
    for job in list_jobs:
        if job['color'] != 'notbuilt':
            if isBuilding(job, list_last_builds):
                job_name = job['name']
                building_time = getBuildingTime(job, list_last_builds)
                metric_time_building_job.add_metric(labels = [job_name], value = building_time)

    list_metrics.append(metric_time_building_job)



    return list_metrics
#----------------------------------------Functions------------------------------------------------------------------------------------


# Tao query lay tat ca cac job
def makeQuery(collector):
    basic_query_labels = JOB_LABELS+',builds['+BUILDS_LABELS+'],lastBuild['+LAST_BUILD_LABELS+']'
    job_query_labels = basic_query_labels
    for i in range(MAX_TREE_DEGREE):
        job_query_labels = basic_query_labels + ',jobs['+job_query_labels+']'
    job_query_labels = 'jobs['+job_query_labels+']'

    tree = TREE_PREFIX + job_query_labels
    prefix = collector._server + API_SUFFIX
    query = prefix + tree
    return query

# Tinh chenh lech giua 2 khoang timestamp theo giay
def getTimeDurationSecond(timestamp1, timestamp2):
    return math.fabs(timestamp2 - timestamp1)

# Lay ra timestamp hien tai
def getTimestampNow():
    return datetime.now().timestamp()

# Check job is pipeline
def isPipeline(class_name):
    if class_name == FOLDER or \
       class_name == ORGANIZATION_FOLDER or \
       class_name == MULTIBRANCH:
        return False
    return True

# Lay thong tin tat ca cac job
def getListJobs(req, collector):
    my_url = makeQuery(collector)
    response = req.getHttpResponse(my_url)
    if response.status_code != 200:
        return []

    raw_data = response.json()

    list_jobs, list_builds, list_last_builds = getJobs(raw_data)
    return len(list_jobs), list_jobs, list_builds, list_last_builds

# Lay ra thong tin tat ca cac pipeline
def getJobs(raw_data):

    list_jobs = []
    list_builds = {}
    list_last_builds = {}
    
    for job in raw_data['jobs']:
        job_name = job['fullName']
        job_class = job['_class']
        if isPipeline(job_class):
            job_color = job['color']
            job_info = {'name': job_name, 'color': job_color}
            list_jobs.append(job_info)
            if job_color == 'notbuilt':
                list_builds[job_name] = {'total': 0, 'builds': []}
                list_last_builds[job_name] = {}
            else:   
                job_last_build = job['lastBuild']
                job_builds = job['builds']
                total = job_last_build['number']
                list_builds[job_name] = {'total': total, 'builds': job_builds}
                list_last_builds[job_name] = job_last_build
        else:
            if 'jobs' in job:
                sub_list_jobs, sub_list_builds, sub_list_last_builds = getJobs(job)
                list_jobs += sub_list_jobs
                list_builds.update(sub_list_builds)
                list_last_builds.update(sub_list_last_builds)
    
    return list_jobs, list_builds, list_last_builds

# Tinh tong so lan build fail lien tiep gan nhat cua mot job
def getTotalFail(job, list_builds):
    if (job['color'] != 'red'):
        return 0
    build_info = list_builds[job['name']]

    total = int(build_info['total'])
    builds = build_info['builds']
    i = total
    count = 0
    for build in builds:
        if build['result'] == 'FAILURE':
            count += 1
        else:
            break
    return count
    
# Lay ra thoi gian build cuoi cua 1 job theo timestamp
def getStartedTimestamp(job, list_last_builds):
    last_build = list_last_builds[job['name']]
    started_timestamp = int(last_build['timestamp']) / 1000
    return started_timestamp

# Tinh khoang thoi gian tu lan build cuoi toi hien tai
def getLastBuildTime(job, list_last_builds):
    started_timestamp = getStartedTimestamp(job, list_last_builds)
    now_timestamp = int(getTimestampNow())
    return getTimeDurationSecond(started_timestamp, now_timestamp)

# Tinh thoi gian da chay cua 1 job dang build
def getBuildingTime(job, list_last_builds):
    return getLastBuildTime(job, list_last_builds)

# Xac dinh 1 job co dang build hay khong
def isBuilding(job, list_last_builds):
    job_name = job['name']
    last_build = list_last_builds[job_name]
    
    return last_build['building']

# Lay ra tong so job dang build
def getTotalBuildingJobs(list_jobs, list_last_builds):
    total = 0
    for job in list_jobs:
        if job['color'] != 'notbuilt':
            if isBuilding(job, list_last_builds):
                total += 1
    return total
