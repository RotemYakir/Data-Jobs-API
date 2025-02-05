from data_jobs.celery_app import celery_app
from data_jobs.jobs import MoveFramesJob
from data_jobs.jobs import DeleteFramesJob
import pymongo

# MongoDB client setup for local result storage
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
result_db = mongo_client['celery_results']


@celery_app.task(name='celery_tasks.run_move_frames_job')
def run_move_frames_job(job_id, params):
    job = MoveFramesJob(job_id=job_id, params=params)
    job.run()
    # Save the final status and logs to MongoDB
    result_db['job_results'].insert_one(job.get_status())
    return job.get_status()


@celery_app.task(name='celery_tasks.run_delete_frames_job')
def run_delete_frames_job(job_id, params):
    job = DeleteFramesJob(job_id=job_id, params=params)
    job.run()
    # Save the final status and logs to MongoDB
    result_db['job_results'].insert_one(job.get_status())
    return job.get_status()
