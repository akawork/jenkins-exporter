import re
import math

API_SUFFIX = '/api/json'
MAX_TREE_DEGREE = 10

PIPELINE = "org.jenkinsci.plugins.workflow.job.WorkflowJob"
MULTIBRANCH = \
    "org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject"
FOLDER = "com.cloudbees.hudson.plugins.folder.Folder"
ORGANIZATION_FOLDER = 'jenkins.branch.OrganizationFolder'
MAX_GET_BUILDS = 12
BUILDS_LABELS = 'number,result'
LAST_BUILD_LABELS = 'number,result,building,timestamp'
JOB_LABELS = '_class,fullName,color'

class Jobs(object):

    def __init__(self, jenkins):
        self.jenkins = jenkins
        self.list_jobs, self.job_info = get_list_jobs(jenkins)
                
    def get_list_jobs(self):
        return self.list_jobs
    
    def get_job(self, job_full_name):
        return self.job_info[job_full_name]

    def get_building_duration(self, job_full_name):
        job = self.job_info[job_full_name]

        if self.get_total_builds(job_full_name) == 0: # not yet build
            return 0

        if self.is_building_job(job_full_name): # a building job
            return get_building_duration(job)
        
        return 0

    def get_total_building_jobs(self):
        return get_total_building_jobs(self.list_jobs, self.job_info)

    def get_total_jobs(self):
        return len(self.list_jobs)

    def get_total_builds(self, job_full_name):
        job = self.job_info[job_full_name]
        return job['builds']['total']

    def get_total_fail_consecutively(self, job_full_name):
        job = self.job_info[job_full_name]
        return get_total_fail_consecutively(job)

    def is_building_job(self, job_full_name):
        job = self.job_info[job_full_name]
        return is_building(job)

# Create query to get all job
def make_query(jenkins):
    basic_query_labels = JOB_LABELS \
                        + ',builds[' \
                        + BUILDS_LABELS \
                        + '],lastBuild[' \
                        + LAST_BUILD_LABELS \
                        + ']' 
    job_query_labels = basic_query_labels
    for i in range(MAX_TREE_DEGREE):
        job_query_labels = basic_query_labels \
                        + ',jobs['+job_query_labels+']'
    job_query_labels = 'jobs['+job_query_labels+']'

    tree = job_query_labels
    url = jenkins.server + API_SUFFIX
    params = {'tree': tree}
    return url, params

# Get all job
def get_list_jobs(jenkins):
    list_jobs = []
    job_info = {}

    url, params = make_query(jenkins)
    response = jenkins.req.do_get(url=url, params=params)
    if response.status_code != 200:
        return list_jobs, job_info

    raw_data = response.json()

    list_jobs, job_info, unknown = get_jobs(raw_data)
    return list_jobs, job_info

def get_jobs(raw_data, unkn=0):

    list_jobs = []
    job_info = {}
    unknown = unkn
    
    jobs = raw_data['jobs']

    for job in jobs:
        if 'fullName' in job:
            job_id = job['fullName']
        else: 
            job_id = 'unknown-' + unknown
            unknown += 1

        job_class = job['_class']
        if is_pipeline(job_class):
            list_jobs.append(job_id)
            job_info[job_id] = standardize_job_info(job)
        else:
            if 'jobs' in job:
                sub_jobs, sub_job_info, sub_unknown = get_jobs(raw_data=job, 
                                                            unkn=unknown)
                list_jobs += sub_jobs
                job_info.update(sub_job_info)
                unknown = sub_unknown
    
    return list_jobs, job_info, unknown

def standardize_job_info(job):
    new_job = {}
    last_build = job['lastBuild'] if 'lastBuild' in job else None
    builds = {}

    if last_build is None:
        builds = {'total': 0, 'info': []}
        last_build = {}
    else:   
        builds['info'] = job['builds']
        builds['total'] = last_build['number']
    
    new_job['full_name'] = job['fullName']
    new_job['color'] = job['color']
    new_job['last_build'] = last_build
    new_job['builds'] = builds

    return new_job

# Calculate the duration between two time points,
# returning the number of seconds
def get_time_duration_second(timestamp1, timestamp2):
    return math.fabs(timestamp2 - timestamp1)

# Get current timestamp 
def get_now_timestamp():
    return datetime.now().timestamp()

# Check job is pipeline or not
def is_pipeline(class_name):
    if class_name == FOLDER or \
        class_name == ORGANIZATION_FOLDER or \
        class_name == MULTIBRANCH:
        return False
    return True

# Count the number of times the last consecutive failure build of a job
def get_total_fail_consecutively(job):
    
    total = int(job['builds']['total'])
    if (total == 0): # not yet built
        return 0
    
    builds = job['builds']['info']

    count = 0
    for build in builds:
        result = build['result'] if 'result' in build else None
        if result is None: # job is running a build
            continue
        if result == 'FAILURE':
            count += 1
        else:
            break
    return count
    
# Get the start time of the last build of a job
def get_started_timestamp(job):
    last_build = job['last_build']
    started_timestamp = int(last_build['timestamp']) / 1000
    return started_timestamp

# Calculate the time interval from the last build to the present
def get_last_build_time(job):
    started_timestamp = get_started_timestamp(job)
    now_timestamp = int(get_now_timestamp())
    return get_time_duration_second(started_timestamp, now_timestamp)

# Calculate the running duration of a building job
def get_building_duration(job):
    return get_last_build_time(job)

# Determine whether a job is building or not
def is_building(job):
    job_name = job['full_name']
    last_build = job['last_build']
    if 'building' in last_build:
        return last_build['building']
    else:
        return False

# Get the total number of jobs that are building
def get_total_building_jobs(list_jobs, job_info):
    total = 0
    for job_id in list_jobs:
        job = job_info[job_id]
        if is_building(job):
            total += 1
    return total