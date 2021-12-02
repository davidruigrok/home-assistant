import uuid
from env import (
    PROJECT_NAME,
)
import logging

# Create unique trace id
trace_id = str(uuid.uuid4())

# Create logger for project
logging.basicConfig(
    level=logging.DEBUG,
    filename=f"/var/log/{PROJECT_NAME}.log",
    filemode="w",
    format="%(asctime)s [%(levelname)s] [%(trace_id)s] %(message)s",
    datefmt="%Y-%m-%d,%H:%M:%S",
)

log_record_factory = logging.getLogRecordFactory()


def record_factory(*args, **kwargs):
    record = log_record_factory(*args, **kwargs)
    record.trace_id = trace_id
    return record


logging.setLogRecordFactory(record_factory)
