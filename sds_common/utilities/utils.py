import json
from pathlib import Path

import requests


from sds_common.config.logging_config import logging
from sds_common.config.config import CONFIG
from sds_common.models.schema_publish_errors import FilepathError, SchemaJSONDecodeError, SchemaFetchError
from sds_common.services.http_service import HTTP_SERVICE

logger = logging.getLogger(__name__)


def split_filename(path: str) -> str | None:
    """
    Splits a filename without extension from the path.

    Parameters:
        path (str): the path to the file.

    Returns:
        str: the filename.
    """
    try:
        return Path(path).stem
    except TypeError:
        raise FilepathError(path) from None


def decode_json_response(response: requests.Response) -> dict | None:
    """
    Decode the JSON response from a requests.Response object.

    Parameters:
        response (requests.Response): the response object to decode.

    Returns:
        dict: the decoded JSON response.
    """
    try:
        decoded_response = response.json()
        return decoded_response
    except json.JSONDecodeError:
        raise SchemaJSONDecodeError("N/A") from None


def fetch_raw_schema_from_github(path: str) -> dict:
    """
    Fetches the schema from the ONSdigital GitHub repository.

    Parameters:
        path (str): the path to the schema JSON.

    Returns:
        dict: the schema JSON.
    """
    url = CONFIG.GITHUB_SCHEMA_URL + path
    logger.info(f"Fetching schema from {url}")
    http_service = HTTP_SERVICE
    response = http_service.make_get_request(url)

    if response.status_code != 200:
        raise SchemaFetchError(path, response.status_code, url)
    schema = decode_json_response(response)
    return schema
