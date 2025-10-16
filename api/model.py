import time
from uuid import UUID

from sqlalchemy.orm import Session

from crud import update_batch_status
from tables import FileStatus


def simulate_model_work(batch_id: UUID, task_id: str, duration: int = 5):
    """Simulates a long-running task"""
    print(f"Starting task {task_id}")
    try:
        update_batch_status(batch_id, FileStatus.processing)
        time.sleep(duration)
        update_batch_status(batch_id, FileStatus.complete)

    except Exception as e:
        print(f"Exception: {e}")
        update_batch_status(batch_id, FileStatus.failed)

    result = f"Task {task_id} completed after {duration} seconds"
    print(result)
    return result
