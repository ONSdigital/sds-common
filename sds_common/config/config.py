from sds_common.config.config_helpers import ConfigHelpers


class Config:
    # Required environment variables.
    PROJECT_ID = ConfigHelpers.get_value_from_env("PROJECT_ID", "ons-sds-sandbox")

    # Default values for environment variables.
    PROCESS_TIMEOUT = int(ConfigHelpers.get_value_from_env("PROCESS_TIMEOUT", "540"))
    SECRET_ID = ConfigHelpers.get_value_from_env("SECRET_ID", "iap-secret")
    GITHUB_SCHEMA_URL = ConfigHelpers.get_value_from_env(
        "GITHUB_SCHEMA_URL",
        "https://raw.githubusercontent.com/ONSdigital/sds-schema-definitions/main/"
    )
    POST_SCHEMA_ENDPOINT = ConfigHelpers.get_value_from_env(
        "POST_SCHEMA_URL", "/v1/schema"
    )
    GET_SCHEMA_METADATA_ENDPOINT = ConfigHelpers.get_value_from_env(
        "GET_SCHEMA_METADATA_URL", "/v1/schema_metadata"
    )
    GET_ALL_SCHEMA_METADATA_ENDPOINT = ConfigHelpers.get_value_from_env(
        "GET_ALL_SCHEMA_METADATA_URL", "/v1/all_schema_metadata"
    )
    DATASET_CREATE_ENDPOINT = ConfigHelpers.get_value_from_env(
        "DATASET_CREATE_PATH", "/events/dataset/create"
    )
    DATASET_DELETE_ENDPOINT = ConfigHelpers.get_value_from_env(
        "DATASET_DELETE_PATH", "/events/dataset/delete"
    )
    PUBLISH_SCHEMA_ERROR_TOPIC_ID = ConfigHelpers.get_value_from_env(
        "PUBLISH_SCHEMA_ERROR_TOPIC_ID", "ons-sds-publish-schema-fail"
    )
    PUBLISH_SCHEMA_SUCCESS_TOPIC_ID = ConfigHelpers.get_value_from_env(
        "PUBLISH_SCHEMA_SUCCESS_TOPIC_ID", "ons-sds-publish-schema"
    )
    PUBLISH_SCHEMA_QUEUE_TOPIC_ID = ConfigHelpers.get_value_from_env(
        "PUBLISH_SCHEMA_QUEUE_TOPIC_ID", "publish-schema-queue"
    )
    PUBLISH_DATASET_TOPIC_ID = ConfigHelpers.get_value_from_env(
        "PUBLISH_DATASET_TOPIC_ID", "ons-sds-publish-dataset"
    )
    SDS_URL = ConfigHelpers.get_value_from_env("SDS_URL", "https://sds.ons.gov.uk")
    GET_DATASET_METADATA_ENDPOINT = ConfigHelpers.get_value_from_env(
        "GET_DATASET_METADATA_ENDPOINT", "/v1/dataset_metadata"
    )
    FIRESTORE_DB_NAME = ConfigHelpers.get_value_from_env(
        "FIRESTORE_DB_NAME", f"{PROJECT_ID}-sds"
    )
    SCHEMA_BUCKET_NAME = ConfigHelpers.get_value_from_env(
        "SCHEMA_BUCKET_NAME", f"{PROJECT_ID}-sds-europe-west2-schema"
    )
    SCHEMA_PUBLISH_BUCKET_NAME = ConfigHelpers.get_value_from_env(
        "SCHEMA_PUBLISH_BUCKET_NAME", f"{PROJECT_ID}-sds-europe-west2-schema-publish"
    )
    DATASET_BUCKET_NAME = ConfigHelpers.get_value_from_env(
        "DATASET_BUCKET_NAME", f"{PROJECT_ID}-sds-europe-west2-dataset"
    )


CONFIG = Config()
