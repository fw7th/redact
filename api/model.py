import time


def simulate_model_work(task_id: str, duration: int = 5):
    """Simulates a long-running task"""
    print(f"Starting task {task_id}")
    time.sleep(duration)
    result = f"Task {task_id} completed after {duration} seconds"
    print(result)
    return result
