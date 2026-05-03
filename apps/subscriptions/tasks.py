from time import sleep

from celery import shared_task


@shared_task
def test() -> str:
    sleep(5)
    return "Test from Celery completed!"
