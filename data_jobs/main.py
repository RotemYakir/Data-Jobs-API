from flask import Flask
from data_jobs_api import data_jobs_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

app.register_blueprint(data_jobs_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
