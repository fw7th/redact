import datetime

from sqlmodel import Session, select

from tables import Batch, File, ImageStatus


def create_image(session: Session, filename: str) -> File:
    image = File(filename=filename, created_at=datetime.datetime.now())
    session.add(image)
    session.commit()
    session.refresh(image)
    return image


def get_image(session: Session, image_id: int) -> File | None:
    return session.get(File, image_id)


def update_image_status(session: Session, image_id: int, status: str) -> File | None:
    image = session.get(File, image_id)
    if not image:
        return None

    image.status = status
    session.add(image)
    session.commit()
    session.refresh(image)
    return image
