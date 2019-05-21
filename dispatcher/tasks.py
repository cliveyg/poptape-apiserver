# tasks.py

from celery import shared_task, group
import time
from django.conf import settings

import logging
logger = logging.getLogger('apiserver')

# -----------------------------------------------------------------------------

@shared_task
def get_microservice_data():
    logger.info("In me task eating your greens")
    time.sleep(2)
    logger.info("That was yummy")
    foovar = "bar"
    return foovar
