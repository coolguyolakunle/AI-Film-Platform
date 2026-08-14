from celery import Celery

# The Celery instance itself is created at import time (needed so task
# modules can register with @celery.task at import time), but it isn't
# configured with a broker/backend until init_celery(app) runs. That keeps
# this decoupled from any specific Flask app instance until startup.
celery = Celery(__name__)


def init_celery(flask_app):
    celery.conf.update(
        broker_url=flask_app.config["CELERY_BROKER_URL"],
        result_backend=flask_app.config["CELERY_RESULT_BACKEND"],
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        task_track_started=True,
        task_always_eager=flask_app.config.get("CELERY_TASK_ALWAYS_EAGER", False),
        task_eager_propagates=flask_app.config.get("CELERY_TASK_EAGER_PROPAGATES", False),
    )

    class ContextTask(celery.Task):
        """Ensures every task runs inside the Flask app context, so it can
        use db.session, current_app.config, etc. exactly like a request would."""

        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
