from celery import Celery
from docgen import settings

class CeleryConnector:
    task_routes = {
        ## process result workers
        "process_doc_gen_result": {"queue": "doc_gen_rs"},
        ## process task workers
        "process_doc_gen": {"queue": "doc_gen"},
    }
    app = Celery(
        "postman",
        broker=settings.BROKER_URL,
    )

    def process_doc_gen_result(self, args):
        return self.send_task("process_doc_gen_result", args)

    def process_doc_gen(self, args):
        return self.send_task("process_doc_gen", args)


    def send_task(self, name=None, args=None):
        if (
            name not in self.task_routes
            or "queue" not in self.task_routes[name]
        ):
            # raise GeneralException("System")
            raise ValueError(f"{name} does not defined")
        return self.app.send_task(
            name, args, queue=self.task_routes[name]["queue"]
        )


c_connector = CeleryConnector()