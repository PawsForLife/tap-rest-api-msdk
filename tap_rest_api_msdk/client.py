"""REST client handling, including RestApiStream base class."""

from pathlib import Path
from typing import Any, Iterator, Optional

import requests
from singer_sdk.streams import RESTStream

from tap_rest_api_msdk.auth import get_authenticator

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class RestApiStream(RESTStream):
    """rest-api stream class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_auth = None
        self._authenticator = getattr(self, "assigned_authenticator", None)

    def _request(
        self,
        prepared_request: requests.PreparedRequest,
        context: Optional[dict],
    ) -> requests.Response:
        """Send the request and validate the response.

        When _is_next_page_request is True and the response is 404, return the
        response without raising so that request_records can treat it as end-of-stream.
        """
        authenticated_request = self.authenticator(prepared_request)
        response = self.requests_session.send(
            authenticated_request,
            timeout=self.timeout,
            allow_redirects=self.allow_redirects,
        )
        self._write_request_duration_log(
            endpoint=self.path,
            response=response,
            context=context,
            extra_tags={"url": authenticated_request.path_url}
            if self._LOG_REQUEST_METRIC_URLS
            else None,
        )
        # 404 on a next-page request is treated as end-of-stream, not fatal.
        if response.status_code == 404 and getattr(
            self, "_is_next_page_request", False
        ):
            return response
        self.validate_response(response)
        return response

    def request_records(self, context: Optional[dict]) -> Iterator[dict]:
        """Request records with pagination; 404 on next-page is end-of-stream.

        When a paginated next-page request returns 404, pagination stops and
        only records from previous pages are yielded. 404 on the initial
        request remains fatal (validate_response raises).
        """
        paginator = self.get_new_paginator() or self._get_single_page_paginator()
        decorated_request = self.request_decorator(self._request)
        pages = 0

        with self.get_http_request_counter() as request_counter:
            request_counter.with_context(context)

            while not paginator.finished:
                next_page_token = paginator.current_value
                self._is_next_page_request = next_page_token is not None

                prepared_request = self.prepare_request(
                    context,
                    next_page_token=next_page_token,
                )
                resp = decorated_request(prepared_request, context)
                request_counter.increment()
                self.update_sync_costs(prepared_request, resp, context)

                # 404 on next-page: treat as end-of-stream, stop without yielding.
                if resp.status_code == 404:
                    break

                records = iter(self.parse_response(resp))
                try:
                    first_record = next(records)
                except StopIteration:
                    if paginator.continue_if_empty(resp):
                        paginator.advance(resp)
                        continue
                    self.log(
                        "Pagination stopped after %d pages because no records were "
                        "found in the last response",
                        pages,
                    )
                    break
                yield first_record
                yield from records
                pages += 1
                paginator.advance(resp)

    def _get_single_page_paginator(self):
        """Return the SDK single-page paginator (used when get_new_paginator is None)."""
        from singer_sdk.pagination import SinglePagePaginator

        return SinglePagePaginator()

    @property
    def url_base(self) -> Any:
        """Return the API URL root, configurable via tap settings.

        Returns:
            The base url for the api call.

        """
        return self.config["api_url"]

    @property
    def authenticator(self) -> Any:
        """Call an appropriate SDK Authentication method.

        Calls an appropriate SDK Authentication method based on the the set
        auth_method which is set via the config.
        If an authenticator (auth_method) is not specified, REST-based taps will simply
        pass `http_headers` as defined in the tap and stream classes.

        Note 1: Each auth method requires certain configuration to be present see
        README.md for each auth methods configuration requirements.

        Note 2: Using Singleton Pattern on the autenticator for caching with a check
        if an OAuth Token has expired and needs to be refreshed.

        Raises:
            ValueError: if the auth_method is unknown.

        Returns:
            A SDK Authenticator or APIAuthenticatorBase if no auth_method supplied.

        """
        # Obtaining Authenticator for authorisation to extract data.
        get_authenticator(self)

        return self._authenticator
