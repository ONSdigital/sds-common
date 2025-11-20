from sds_common.services.http_service import AUTHENTICATED_HTTP_SERVICE


class CirRequestService:
    def __init__(self):
        self.http_service = AUTHENTICATED_HTTP_SERVICE
