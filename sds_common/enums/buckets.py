from enum import Enum
from sds_common.config.config import CONFIG


class Bucket(Enum):
    SCHEMA_BUCKET = CONFIG.SCHEMA_BUCKET_NAME
    SCHEMA_PUBLISH_BUCKET = CONFIG.SCHEMA_PUBLISH_BUCKET_NAME
