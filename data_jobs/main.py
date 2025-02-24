import pymongo
from flask import Flask
from data_jobs.data_jobs_api import data_jobs_bp

mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
result_db = mongo_client['celery_results']
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

app.register_blueprint(data_jobs_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)