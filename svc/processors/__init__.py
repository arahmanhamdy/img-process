"""
The processors package contains all image processing tasks that will be executed on the uploaded images
you can import tasks modules and add them to REGISTERED_TASKS list
"""
from svc.processors import average_pixel

REGISTERED_TASKS = [
    average_pixel,
]
