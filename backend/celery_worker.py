from app import create_app
from app.celery_app import celery

flask_app = create_app()

# Import tasks so they register with the Celery instance before the
# worker starts consuming from the queue.
from app import tasks  # noqa: E402,F401
