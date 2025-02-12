from celery import Celery
from data_jobs.jobs import job_factory
import pymongo

celery_app = Celery('data_jobs',
                    broker='pyamqp://guest@localhost//',
                    backend='mongodb://localhost:27017/celery_results')

mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
result_db = mongo_client['celery_results']


@celery_app.task(name='celery_tasks.run_job')
def run_job(job_name, job_id, params):
    try:
        job_class = job_factory(job_name)
        job = job_class(job_id, params)
        job.run()
        result_db['job_results'].insert_one(job.get_status())
        return job.get_status()
    except NameError as e:
        return {"error": str(e)}
