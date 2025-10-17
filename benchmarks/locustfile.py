# benchmarks/locustfile.py
from locust import HttpUser, between, task


class PredictUser(HttpUser):
    wait_time = between(1, 2)  # simulate user think time

    @task
    def upload(self):
        with open("benchmarks/test_assets/file7.jpeg", "rb") as f:
            files = {"files": ("file7.jpeg", f, "image/jpeg")}
            self.client.post("/predict", files=files)
