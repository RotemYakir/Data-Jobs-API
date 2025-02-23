import time
from abc import ABC, abstractmethod
import logging
from datetime import datetime

import pymongo
from celery import current_task
from bson import ObjectId

mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
result_db = mongo_client['celery_results']
job_results_collection = result_db['job_results']


class Job(ABC):
    def __init__(self, job_description: str, params: dict):
        self.job_id = str(ObjectId())
        self.job_description = job_description
        self.params = params
        self.start_time = None
        self.end_time = None
        self.status = 'PENDING'  # Options: PENDING, RUNNING, COMPLETED, FAILED, STOPPED
        self.logs = []

    def log(self, message: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        self.logs.append(log_message)
        job_results_collection.update_one(
            {"job_id": self.job_id},
            # {"$push": {"logs": log_message}}
            {"$push": {"logs": log_message}}
        )

        logging.info(log_message)

    def run(self):
        self.start_time = datetime.now()
        self.status = 'RUNNING'
        job_results_collection.update_one(
            {"job_id": self.job_id},
            {"$set": self.get_job_data()}
        )
        self.log(f"Job {self.job_id} started with params: {self.params}")
        try:
            self.execute()
            for i in range(5):  # Simulate 5 steps, each taking 60s
                current_task.update_state(state="RUNNING", meta={"progress": f"{(i + 1) * 20}% done"})
                self.log(f"Simulating work... {i + 1}/5")
                time.sleep(5)  # Sleep for 60 seconds per step
            self.status = 'COMPLETED'
            self.log(f"Job {self.job_id} completed successfully.")
        except Exception as e:
            self.status = 'FAILED'
            self.log(f"Job {self.job_id} failed with error: {e}")
        finally:
            self.end_time = datetime.now()

    @abstractmethod
    def execute(self):
        pass

    def get_job_data(self):
        return {
            'job_id': self.job_id,
            'job_description': self.job_description,
            'status': self.status,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'logs': self.logs
        }


def get_job_parameters(job_type: str):
    """Returns a list of parameter names required for a given job."""
    job_class = job_factory(job_type)
    return job_class.PARAMS


def job_factory(job_type: str):
    """ Factory method to return the correct job class. """
    from data_jobs.jobs.delete_frames import DeleteFramesJob
    from data_jobs.jobs.move_frames import MoveFramesJob
    job_map = {
        "delete": DeleteFramesJob,
        "move": MoveFramesJob
    }
    job = job_map.get(job_type)
    if not job:
        raise NameError(f"Job '{job_type}' doesn't exist")
    return job
