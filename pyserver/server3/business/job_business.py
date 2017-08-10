#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
# @author   : Tianyi Zhang
# @version  : 1.0
# @date     : 2017-05-24 11:00pm
# @function : Getting all of the job of statics analysis
# @running  : python
# Further to FIXME of None
"""
from copy import deepcopy

from datetime import datetime

from server3.entity.job import Job
from server3.repository.job_repo import JobRepo

job_repo = JobRepo(Job)


def get_by_job_id(job_id):
    # job_obj = Job(id=job_id)
    return job_repo.read_by_unique_field('id', job_id)
    # return job_repo.read_by_job_id(job_obj)


def get_by_job_model(model):
    # job_obj = Job(model=model)
    return job_repo.read_by_unique_field('model', model)
    # return job_repo.read_by_model(job_obj)


def get_by_project(project):
    return job_repo.read_by_unique_field('project', project)


def get_by_job_toolkit(toolkit):
    # job_obj = Job(toolkit=toolkit)
    return job_repo.read_by_unique_field('toolkit', toolkit)
    # return job_repo.read_by_toolkit(job_obj)


def get_by_job_staging_data_set(staging_data_set):
    # job_obj = Job(staging_data_set=staging_data_set)
    # return job_repo.read_by_staging_data_set(job_obj)
    return job_repo.read_by_unique_field('staging_data_set', staging_data_set)


def get_by_job_status(job_status):
    # job_obj = Job(status=job_status)
    # return job_repo.read_by_status(job_obj)
    return job_repo.read_by_unique_field('job_status', job_status)


def add_toolkit_job(toolkit_obj, staging_data_set_obj, project_obj, **kwargs):
    """toolkit is a obj"""
    # job = job_obj['staging_data_set'] or job_obj['model'] or job_obj['toolkit']
    # if not 0 < len(toolkit_obj.items()) <= 1:
    #     raise ValueError('invalid toolkit_obj')
    time = datetime.utcnow()

    job_obj = Job(status=0, toolkit=toolkit_obj,
                  staging_data_set=staging_data_set_obj,
                  project=project_obj,
                  create_time=time, **kwargs)
    return job_repo.create(job_obj)


def add_model_job(model_obj, staging_data_set_obj, project_obj, **kwargs):
    """

    :param model_obj:
    :param staging_data_set_obj:
    :param argv:
    :return:
    """
    now = datetime.utcnow()

    job_obj = Job(status=0, model=model_obj,
                  staging_data_set=staging_data_set_obj,
                  project=project_obj,
                  create_time=now, **kwargs)
    return job_repo.create(job_obj)


def add_model_train_job(model_obj, staging_data_set_obj):
    time = datetime.utcnow()
    job_obj = Job(status=0, toolkit=model_obj,
                  staging_data_set=staging_data_set_obj, create_time=time)
    return job_repo.create(job_obj)


def add_many(objects):
    return job_repo.create_many(objects)


def end_job(job_obj):
    time = datetime.utcnow()
    return job_repo.update_one_by_id_status_and_time(job_obj.id, 200, time)


def update_job(job_obj):
    time = datetime.utcnow()
    return job_repo.update_one_by_id_status_and_time(job_obj.id, 200, time)


def remove_by_id(file_id):
    return job_repo.delete_by_id(file_id)


def copy_job(job, belonged_project, staging_data_set):
    # from server3.entity.job import Job
    # if not isinstance(job, Job):
    #     return
    j = deepcopy(job)
    j.id = None
    j.project = belonged_project
    if staging_data_set:
        j.staging_data_set = staging_data_set
    job_repo.create(j)
    return j