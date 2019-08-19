from prometheus_client.core import GaugeMetricFamily


def make_metrics(jobs):

    list_metrics = []
    list_jobs = jobs.get_list_jobs()

    # Total job
    metric = GaugeMetricFamily(
        'jenkins_jobs_total',
        'Total job in Jenkins',
        labels=None
    )

    metric.add_metric(
        labels=[],
        value=jobs.get_total_jobs()
    )

    list_metrics.append(metric)

    # Total build of a job
    metric = None
    metric = GaugeMetricFamily(
        'jenkins_job_builds_total',
        'Total builds of a job',
        labels=['job_name']
    )
    for job_id in list_jobs:  # job_id == job['full_name']
        metric.add_metric(
            labels=[job_id],
            value=jobs.get_total_builds(job_id)
        )

    list_metrics.append(metric)

    # Total consecutive failed of a job
    metric = None
    metric = GaugeMetricFamily(
        'jenkins_job_fail_consecutively',
        'The number of times the last consecutive failure build of a job',
        labels=['job_name']
    )
    for job_id in list_jobs:
        metric.add_metric(
            labels=[job_id],
            value=jobs.get_total_fail_consecutively(job_id)
        )

    list_metrics.append(metric)

    # Total building jobs
    metric = None
    metric = GaugeMetricFamily(
        'jenkins_jobs_building_total',
        'Total building jobs',
        labels=None
    )
    metric.add_metric(
        labels=[],
        value=jobs.get_total_building_jobs()
    )

    list_metrics.append(metric)

    # The building duration of a building job
    metric = None
    metric = GaugeMetricFamily(
        'jenkins_jobs_building_time_seconds',
        'The running duration of a building job',
        labels=['job_name', 'status']
    )
    for job_id in list_jobs:
        job = jobs.get_job(job_id)
        building_duration = jobs.get_building_duration(job_id)
        if building_duration > 0:
            metric.add_metric(
                labels=[job_id, 'building'],
                value=building_duration
            )
        else:
            if jobs.get_total_builds(job_id) == 0:
                metric.add_metric(
                    labels=[job_id, 'not_yet_built'],
                    value=0
                )
            else:
                metric.add_metric(
                    labels=[job_id, 'not_building'],
                    value=0
                )

    list_metrics.append(metric)

    return list_metrics
