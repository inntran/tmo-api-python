"""Base client for The Mortgage Office API."""

import json
import sys
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import requests

from ._version import __version__
from .environments import DEFAULT_ENVIRONMENT, Environment
from .exceptions import APIError, AuthenticationError, NetworkError
from .resources import (
    CertificatesResource,
    DistributionsResource,
    HistoryResource,
    PartnersResource,
    PoolsResource,
)


class TMOClient:
    """Base client for The Mortgage Office API."""

    def __init__(
        self,
        token: str,
        database: str,
        environment: Union[Environment, str] = DEFAULT_ENVIRONMENT,
        timeout: int = 30,
        debug: bool = False,
        user_agent: Optional[str] = None,
    ) -> None:
        """Initialize the client.

        Args:
            token: Your API token assigned by Applied Business Software
            database: The name of your company database
            environment: API environment (US, CANADA, AUSTRALIA) or custom URL
            timeout: Request timeout in seconds (default: 30)
            debug: Enable debug logging (default: False)
            user_agent: Custom User-Agent header (default includes package version)
        """
        self.token: str = token
        self.database: str = database
        self.timeout: int = timeout
        self.debug: bool = debug
        self.user_agent: str = (
            user_agent
            or f"python-tmo-api/{__version__} (https://inntran.github.io/tmo-api-python/)"
        )

        # Handle environment parameter
        if isinstance(environment, str):
            # If string, treat as custom URL
            self.base_url: str = environment
        else:
            # If Environment enum, use its value
            self.base_url = environment.value

        self.session: requests.Session = requests.Session()

        # Set default headers
        self.session.headers.update(
            {
                "Token": self.token,
                "Database": self.database,
                "Content-Type": "application/json",
                "User-Agent": self.user_agent,
            }
        )

        # Import PoolType here to avoid circular imports
        from .resources.pools import PoolType

        # Initialize Shares resources
        self.shares_pools: PoolsResource = PoolsResource(self, PoolType.SHARES)
        self.shares_partners: PartnersResource = PartnersResource(self, PoolType.SHARES)
        self.shares_distributions: DistributionsResource = DistributionsResource(
            self, PoolType.SHARES
        )
        self.shares_certificates: CertificatesResource = CertificatesResource(self, PoolType.SHARES)
        self.shares_history: HistoryResource = HistoryResource(self, PoolType.SHARES)

        # Initialize Capital resources
        self.capital_pools: PoolsResource = PoolsResource(self, PoolType.CAPITAL)
        self.capital_partners: PartnersResource = PartnersResource(self, PoolType.CAPITAL)
        self.capital_distributions: DistributionsResource = DistributionsResource(
            self, PoolType.CAPITAL
        )
        self.capital_history: HistoryResource = HistoryResource(self, PoolType.CAPITAL)

    def _debug_log(self, message: str) -> None:
        """Log debug message to stderr if debug mode is enabled."""
        if self.debug:
            print(f"DEBUG: {message}", file=sys.stderr)

    def _debug_log_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log request details if debug mode is enabled."""
        if not self.debug:
            return

        print("DEBUG: === REQUEST ===", file=sys.stderr)
        print(f"DEBUG: {method} {url}", file=sys.stderr)
        print("DEBUG: Headers:", file=sys.stderr)
        for key, value in headers.items():
            # Mask sensitive headers
            if key.lower() in ["token", "authorization"]:
                masked_value = (
                    "*" * min(len(value), 8) + value[-4:] if len(value) > 4 else "*" * len(value)
                )
                print(f"DEBUG:   {key}: {masked_value}", file=sys.stderr)
            else:
                print(f"DEBUG:   {key}: {value}", file=sys.stderr)

        if params:
            print("DEBUG: Query Parameters:", file=sys.stderr)
            for key, value in params.items():
                print(f"DEBUG:   {key}: {value}", file=sys.stderr)

        if json_data:
            print("DEBUG: Request Body:", file=sys.stderr)
            print(f"DEBUG: {json.dumps(json_data, indent=2)}", file=sys.stderr)

    def _debug_log_response(
        self, response: requests.Response, response_data: Dict[str, Any]
    ) -> None:
        """Log response details if debug mode is enabled."""
        if not self.debug:
            return

        print("DEBUG: === RESPONSE ===", file=sys.stderr)
        print(f"DEBUG: Status: {response.status_code}", file=sys.stderr)
        print("DEBUG: Response Headers:", file=sys.stderr)
        for key, value in response.headers.items():
            print(f"DEBUG:   {key}: {value}", file=sys.stderr)

        print("DEBUG: Response Body:", file=sys.stderr)
        print(
            f"DEBUG: {json.dumps(response_data, indent=2, default=str)}",
            file=sys.stderr,
        )
        print("DEBUG: ==================", file=sys.stderr)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests

        Returns:
            API response data

        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API returns an error
            NetworkError: If a network error occurs
        """
        url: str = urljoin(self.base_url + "/", endpoint)

        # Log request details if debug mode is enabled
        self._debug_log_request(
            method=method,
            url=url,
            headers={k: str(v) for k, v in self.session.headers.items()},
            params=kwargs.get("params"),
            json_data=kwargs.get("json"),
        )

        try:
            response = self.session.request(method=method, url=url, timeout=self.timeout, **kwargs)
            response.raise_for_status()

        except requests.exceptions.Timeout:
            self._debug_log("Request timed out")
            raise NetworkError("Request timed out")
        except requests.exceptions.ConnectionError:
            self._debug_log("Connection error occurred")
            raise NetworkError("Connection error occurred")
        except requests.exceptions.HTTPError as e:
            self._debug_log(f"HTTP error: {response.status_code}")
            if response.status_code == 401:
                raise AuthenticationError("Invalid token or database")
            elif response.status_code == 403:
                raise AuthenticationError("Access denied")
            else:
                raise NetworkError(f"HTTP {response.status_code}: {str(e)}")
        except requests.exceptions.RequestException as e:
            self._debug_log(f"Request exception: {str(e)}")
            raise NetworkError(f"Request failed: {str(e)}")

        try:
            data: Dict[str, Any] = response.json()
        except ValueError:
            self._debug_log("Failed to parse JSON response")
            raise APIError("Invalid JSON response from API")

        # Log response details if debug mode is enabled
        self._debug_log_response(response, data)

        # Check for API-level errors
        if data.get("Status") != 0:
            error_message: str = data.get("ErrorMessage", "Unknown API error")
            error_number: Optional[int] = data.get("ErrorNumber")
            self._debug_log(f"API error: {error_message} (Number: {error_number})")
            raise APIError(error_message, error_number)

        return data

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            API response data
        """
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request.

        Args:
            endpoint: API endpoint path
            json: JSON data to send

        Returns:
            API response data
        """
        return self._make_request("POST", endpoint, json=json)

    def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request.

        Args:
            endpoint: API endpoint path
            json: JSON data to send

        Returns:
            API response data
        """
        return self._make_request("PUT", endpoint, json=json)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request.

        Args:
            endpoint: API endpoint path

        Returns:
            API response data
        """
        return self._make_request("DELETE", endpoint)
