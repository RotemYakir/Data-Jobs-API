from flask import Flask, request, jsonify, render_template, redirect
from data_jobs.celery_app import run_move_frames_job, run_delete_frames_job
import pymongo
from datetime import datetime

app = Flask(__name__)

# MongoDB client setup
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
result_db = mongo_client['celery_results']


@app.template_filter('date_format')
def date_format(value):
    if not value:
        return ''  # Return an empty string if value is None

    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return value  # If the format is wrong, return the original value

    return str(value)  # Fallback for unexpected types


@app.route('/')
def main_page():
    """
    Display all tasks and buttons to trigger specific task forms.
    """
    tasks = result_db['job_results'].find().sort('start_time', -1)
    tasks = [{**task, '_id': str(task['_id'])} for task in tasks]  # Convert ObjectId to string
    return render_template('main_page.html', tasks=tasks)


@app.route('/move-frames-form')
def move_frames_form():
    """
    Render the Move Frames job form.
    """
    return render_template('move_frames_form.html')


@app.route('/delete-frames-form')
def delete_frames_form():
    """
    Render the Delete Frames job form.
    """
    return render_template('delete_frames_form.html')


@app.route('/submit-move-job', methods=['POST'])
def submit_move_job():
    """
    Handle form submission to trigger a Move Frames job.
    """
    job_id = request.form.get('job_id')
    params = {
        'folder_patterns': request.form.get('folder_patterns'),
        'frame_query': request.form.get('frame_query'),
        'source': request.form.get('source'),
        'destination': request.form.get('destination'),
        'modify': request.form.get('modify', 'true').lower() == 'true'
    }

    task_result = run_move_frames_job.delay(job_id, params)
    return redirect("/")


@app.route('/submit-delete-job', methods=['POST'])
def submit_delete_job():
    """
    Handle form submission to trigger a Delete Frames job.
    """
    job_id = request.form.get('job_id')
    params = {
        'folder_pattern': request.form.get('folder_pattern'),
        'frame_query': request.form.get('frame_query')
    }

    task_result = run_delete_frames_job.delay(job_id, params)
    return redirect("/")


@app.route('/job-status/<job_id>')
def job_status(job_id):
    """
    Display the status and logs of a job.
    """
    result = result_db['job_results'].find_one({'job_id': job_id})
    if not result:
        return "Job not found.", 404

    result['_id'] = str(result['_id'])
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
