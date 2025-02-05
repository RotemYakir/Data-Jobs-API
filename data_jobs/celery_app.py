from celery import Celery

celery_app = Celery('data_jobs',
                    broker='pyamqp://guest@localhost//',  # RabbitMQ
                    backend='mongodb://localhost:27017/celery_results')  # MongoDB
