import datetime

from sqlmodel import Session, select

from models import ImageStatus, jobs


def create_image(session: Session, filename: str) -> jobs:
    image = jobs(filename=filename, created_at=datetime.datetime.now())
    session.add(image)
    session.commit()
    session.refresh(image)
    return image


def get_image(session: Session, image_id: int) -> jobs | None:
    return session.get(jobs, image_id)


def update_image_status(session: Session, image_id: int, status: str) -> jobs | None:
    image = session.get(jobs, image_id)
    if not image:
        return None

    image.status = status
    session.add(image)
    session.commit()
    session.refresh(image)
    return image
