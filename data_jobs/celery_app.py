from celery import Celery
import pymongo
from jobs.job import job_factory

celery_app = Celery('data_jobs',
                    broker='pyamqp://guest@localhost//',
                    backend='mongodb://localhost:27017/celery_results')

mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
result_db = mongo_client['celery_results']


@celery_app.task(name='celery_tasks.run_job')
def run_job(job_type, job_description, params):
    try:
        job_class = job_factory(job_type)
        job = job_class(job_description, params)
        job_data = job.get_job_data()
        job_data["celery_task_id"] = run_job.request.id  # Store the Celery task ID

        result_db['job_results'].insert_one(job_data)
        job.run()

        result_db['job_results'].update_one(
            {"job_id": job.job_id},
            {"$set": job.get_job_data()}
        )
        return job.get_job_data()
    except NameError as e:
        return {"error": str(e)}
