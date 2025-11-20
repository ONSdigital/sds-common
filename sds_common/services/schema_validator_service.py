from sds_common.config.logging_config import logging
from sds_common.models.schema_publish_errors import (
    SchemaDuplicationError,
    SchemaVersionMismatchError,
)
from sds_common.schema.schema import Schema
from sds_common.services.sds_schema_request_service import SdsSchemaRequestService
from sds_common.utilities.utils import split_filename

logger = logging.getLogger(__name__)


class SchemaValidatorService:
    def __init__(self):
        self.sds_schema_request_service = SdsSchemaRequestService()

    def validate_schema(self, schema: Schema) -> None:
        """
        Validate the schema by verifying the version and checking for duplicate versions.

        :param schema: The schema object to validate.
        :return: None
        """
        logger.info(f"Validating schema {schema.filepath}")
        self._verify_version(schema)
        self._check_duplicate_versions(schema)

    @staticmethod
    def _verify_version(schema: Schema) -> None:
        """
        Method to verify the schema version in the JSON matches the filename.

        :param schema: the schema object to be posted.
        :return: None
        """
        trimmed_filename = split_filename(schema.filepath)
        if schema.schema_version != trimmed_filename:
            raise SchemaVersionMismatchError(schema.filepath)

    def _check_duplicate_versions(self, schema: Schema) -> None:
        """
        Check that the schema_version for the new schema is not already present in SDS.

        :param schema: the schema to be posted.
        :return: None
        """
        schema_metadata = self.sds_schema_request_service.get_schema_metadata(schema.survey_id)

        # If the schema_metadata endpoint returns a 404, then the survey is new and there are no duplicate versions.
        if schema_metadata.status_code == 404:
            return

        for version in schema_metadata.json():
            if schema.schema_version == version["schema_version"]:
                raise SchemaDuplicationError(schema.filepath)
