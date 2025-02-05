from flask import Flask, request, jsonify, render_template, redirect, url_for
from data_jobs.celery_tasks import run_move_frames_job, run_delete_frames_job
import pymongo

app = Flask(__name__)

# MongoDB client setup
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
result_db = mongo_client['celery_results']


@app.route('/')
def job_form():
    """
    Display the job form to the user.
    """
    return render_template('job_form.html')


@app.route('/submit-job', methods=['POST'])
def submit_job():
    """
    Handle form submission to trigger a job.
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
    return redirect(url_for('job_status', job_id=job_id))


@app.route('/job-status/<job_id>')
def job_status(job_id):
    """
    Display the status and logs of the job.
    """
    result = result_db['job_results'].find_one({'job_id': job_id})
    if not result:
        return "Job not found.", 404

    result['_id'] = str(result['_id'])
    return jsonify(result)


@app.route('/submit-delete-job', methods=['POST'])
def submit_delete_job():
    job_id = request.form.get('job_id')
    params = {
        'folder_pattern': request.form.get('folder_pattern'),
        'frame_query': request.form.get('frame_query')
    }

    task_result = run_delete_frames_job.delay(job_id, params)
    return redirect(url_for('job_status', job_id=job_id))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
