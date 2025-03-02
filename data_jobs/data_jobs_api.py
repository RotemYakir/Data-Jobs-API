from flask import Flask, request, jsonify, render_template, redirect, flash, Blueprint
from celery_app import run_job, celery_app
import pymongo
from datetime import datetime

from data_jobs.jobs.job import get_job_parameters

data_jobs_bp = Blueprint('data_jobs', __name__)

# MongoDB client setup
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
result_db = mongo_client['celery_results']
data_jobs_bp.secret_key = 'temp_secret_key_here'  # Needed for flash messages


@data_jobs_bp.app_template_filter('date_format')
def date_format(value):
    if not value:
        return ''
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return value
    return str(value)


@data_jobs_bp.route('/')
def main_page():
    tasks = result_db['job_results'].find().sort('start_time', -1)
    tasks = [{**task, '_id': str(task['_id'])} for task in tasks]
    return render_template('main_page.html', tasks=tasks)


@data_jobs_bp.route('/job-form')
def job_form():
    """
    Render the job submission form with job metadata.
    """
    job_types = ["move", "delete"]  # Available jobs
    job_params = {job: get_job_parameters(job) for job in job_types}  # Get parameters for each job
    return render_template("job_form.html", job_types=job_types, job_params=job_params)


@data_jobs_bp.route('/submit-job', methods=['POST'])
def submit_job():
    """
    Generic job submission handler.
    """
    job_type = request.form.get('job_type')
    job_description = request.form.get('job_description')
    submission_type = request.form.get("submission_type", "sumbit&finish")

    # Collect all parameters dynamically
    params = {key: value for key, value in request.form.items() if key not in ['job_type', 'job_id']}

    try:
        task_result = run_job.delay(job_type, job_description, params)
        if submission_type == 'submit&fill':
            return redirect("/job-form")
        else:
            return redirect("/")
    except NameError:
        return f"Error: Job '{job_type}' not found.", 400


@data_jobs_bp.route('/job-status/<job_id>')
def job_status(job_id):
    result = result_db['job_results'].find_one({'job_id': job_id})
    if not result:
        return "Job not found.", 404
    result['_id'] = str(result['_id'])
    return render_template('job_status.html', result=result)


@data_jobs_bp.route('/stop-job/<job_id>', methods=['POST'])
def stop_job(job_id):
    """
       Stops a running Celery job by revoking it.
       """
    job = result_db['job_results'].find_one({"job_id": job_id})
    if not job:
        return jsonify({"error": "Job not found"}), 404

    celery_task_id = job.get("celery_task_id")
    if not celery_task_id:
        return jsonify({"error": "Task ID not available"}), 400

    celery_app.control.revoke(celery_task_id, terminate=True)
    result_db['job_results'].update_one(
        {"job_id": job_id},
        {"$set": {"status": "STOPPED", "end_time": datetime.now()}}
    )
    flash(f"Job {job_id} stopped successfully!", "success")
    return redirect("/")


