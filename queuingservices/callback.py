import json
import os

from storage.job_storage_interface import JobStorageInterface


def retrieve_job_data(bucket, username, project_id,
                      experiment_id, job_id, local_path, storage_obj, variant):
    """

    This function will download a job file to a specified location with
    a specified file name locally.

    :param variant: submission or completion
    :param storage_obj:
    :param bucket:
    :param username:
    :param project_id:
    :param experiment_id:
    :param job_id:
    :param local_path:

    :return:
    """
    storage_master_obj = JobStorageInterface(storage_obj=
                                             storage_obj)

    if local_path is None:
        local_path = f"{job_id}.tar"

    storage_master_obj.get_job_data(bucket=bucket,
                                    username=username,
                                    project_id=project_id,
                                    experiment_id=experiment_id,
                                    job_id=job_id,
                                    local_path=local_path, variant=variant)


def process_completion_service_job(message_dict, storage_obj):
    # build the local path to download job data
    local_path = f"{os.getcwd()}/{message_dict['experiment_id']}/{message_dict['job_id']}.tar"
    retrieve_job_data(bucket=message_dict['bucket_name'],
                      username=message_dict['username'],
                      project_id=message_dict['project_id'],
                      experiment_id=message_dict['experiment_id'],
                      job_id=message_dict['job_id'],
                      local_path=local_path,
                      storage_obj=storage_obj,
                      variant="completion")


def process_submission_service_job(message_dict, storage_obj):
    # Save the JOB
    local_path = f"/.mineai/jobs/{message_dict['username']}/{message_dict['project_id']}" \
                 f"/{message_dict['experiment_id']}/{message_dict['job_id']}.tar"
    retrieve_job_data(bucket=message_dict['bucket_name'],
                      username=message_dict['username'],
                      project_id=message_dict['project_id'],
                      experiment_id=message_dict['experiment_id'],
                      job_id=message_dict['job_id'],
                      local_path=local_path,
                      storage_obj=storage_obj,
                      variant="submission")



def callback_handler(message, storage_obj):
    message_dict = json.loads(message)

    if message_dict['completion']:
        process_completion_service_job(message_dict, storage_obj)

    elif message_dict['submission']:
        process_submission_service_job(message_dict, storage_obj)
