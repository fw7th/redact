# benchmarks/locustfile.py
from locust import HttpUser, between, task


class PredictUser(HttpUser):
    wait_time = between(1, 5)  # simulate user think time

    """
    @task
    def upload(self):
        with open("../media/mobile2.jpg", "rb") as f:
            files = {"files": ("mobile2.jpg", f, "image/jpg")}
            self.client.post("/predict", files=files)
    """

    """
    @task
    def check(self):
        batch_id = 1
        self.client.get(f"/predict/{batch_id}", name="/predict/[batch_id]")
    """

    @task
    def check(self):
        batch_id = 1
        self.client.get(f"/predict/check/{batch_id}", name="/predict/check/[batch_id]")
