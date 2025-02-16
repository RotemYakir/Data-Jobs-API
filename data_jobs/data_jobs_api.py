from flask import Flask, request, jsonify, render_template, redirect
from data_jobs.celery_app import run_job
import pymongo
from datetime import datetime
from jobs import get_job_parameters

app = Flask(__name__)

# MongoDB client setup
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
result_db = mongo_client['celery_results']


@app.template_filter('date_format')
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


@app.route('/')
def main_page():
    tasks = result_db['job_results'].find().sort('start_time', -1)
    tasks = [{**task, '_id': str(task['_id'])} for task in tasks]
    return render_template('main_page.html', tasks=tasks)


@app.route('/job-form')
def job_form():
    """
    Render the job submission form with job metadata.
    """
    job_types = ["move", "delete"]  # Available jobs
    job_params = {job: get_job_parameters(job) for job in job_types}  # Get parameters for each job
    return render_template("job_form.html", job_types=job_types, job_params=job_params)


@app.route('/submit-job', methods=['POST'])
def submit_job():
    """
    Generic job submission handler.
    """
    job_name = request.form.get('job_name')
    job_description = request.form.get('job_description')

    # Collect all parameters dynamically
    params = {key: value for key, value in request.form.items() if key not in ['job_name', 'job_id']}

    try:
        task_result = run_job.delay(job_name, job_description, params)
        return redirect("/")
    except NameError:
        return f"Error: Job '{job_name}' not found.", 400


@app.route('/job-status/<job_id>')
def job_status(job_id):
    result = result_db['job_results'].find_one({'job_id': job_id})
    if not result:
        return "Job not found.", 404
    result['_id'] = str(result['_id'])
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
