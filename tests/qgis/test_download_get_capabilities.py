# standard
import json
import unittest
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock, patch

# pyQGIS
from qgis.core import QgsApplication
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser import (
    download_getcapabilities,
)
from gpf_isochrone_isodistance_itineraire.toolbelt.preferences import PlgOptionsManager


class TestDownloadGetCapabilities(unittest.TestCase):
    """Test cases for download_getcapabilities function."""

    @classmethod
    def setUpClass(cls):
        cls.qgs = QgsApplication([], False)
        cls.qgs.initQgis()

    @classmethod
    def tearDownClass(cls):
        cls.qgs.exitQgis()

    def setUp(self):
        """Set up test environment before each test."""

        # Add patch for QgsBlockingNetworkRequest return
        self.blocking_request_patcher = patch(
            "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.QgsBlockingNetworkRequest"
        )

        # Launch mock
        self.mock_blocking_request_class = self.blocking_request_patcher.start()

        # Mock return value for QgsBlockingNetworkRequest
        self.mock_blocking_instance = MagicMock()

        # Define side_effect to return wanted value
        self.mock_blocking_instance.get.side_effect = self._mock_get_with_count
        self.mock_blocking_request_class.return_value = self.mock_blocking_instance

        # Mock error code for QgsBlockingNetworkRequest
        mock_error_code = Mock()
        mock_error_code.NoError = 0
        self.mock_blocking_request_class.ErrorCode = mock_error_code

        # Store return value for url
        self.url_configs = {}

        self.call_count = 0

    def tearDown(self):
        """Stop mock after test"""
        self.blocking_request_patcher.stop()

    def configure_url_response(
        self,
        url: str,
        response_data: Optional[Dict[str, Any]] = None,
        error_code: int = 0,
        error_message: str = "",
    ):
        """Configure mock for an url response

        :param url: url
        :type url: str
        :param response_data: response for url, defaults to None
        :type response_data: Optional[Dict[str, Any]], optional
        :param error_code: error code for url, defaults to 0
        :type error_code: int, optional
        :param error_message: error message for url, defaults to ""
        :type error_message: str, optional
        """
        self.url_configs[url] = {
            "response_data": response_data,
            "error_code": error_code,
            "error_message": error_message,
        }

    def _mock_get_with_count(
        self, request: QNetworkRequest, forceRefresh: bool = False
    ) -> int:
        """Side effect for QgsBlockingNetworkRequest call
        Define returned data for a get request

        :param request: request
        :type request: QNetworkRequest
        :param forceRefresh: force refresh, defaults to False
        :type forceRefresh: bool, optional
        :return: error code
        :rtype: int
        """

        # Add call count for cache check
        self.call_count += 1

        # Check if url defined in current url configs
        url_requested = request.url().toString()

        for base_url, config in self.url_configs.items():
            if base_url in url_requested:
                self.mock_blocking_instance.errorMessage.return_value = config[
                    "error_message"
                ]
                if config["response_data"] is not None:
                    mock_reply = MagicMock()
                    mock_reply.content.return_value = json.dumps(
                        config["response_data"]
                    ).encode("UTF-8")
                    self.mock_blocking_instance.reply.return_value = mock_reply
                return config["error_code"]

        # Return no error by default
        return 0

    def test_different_urls_different_responses(self):
        """Test that different URLs get different responses."""
        self.configure_url_response(
            "success.example.com", response_data={"capabilities": "success"}
        )
        self.configure_url_response(
            "error.example.com", error_code=1, error_message="Network timeout"
        )
        self.configure_url_response(
            "custom.example.com",
            response_data={"capabilities": "custom", "version": "1.0"},
        )

        result_success = download_getcapabilities("https://success.example.com/service")
        self.assertEqual(result_success, {"capabilities": "success"})

        result_error = download_getcapabilities("https://error.example.com/service")
        self.assertIsNone(result_error)

        result_custom = download_getcapabilities("https://custom.example.com/service")
        self.assertEqual(result_custom, {"capabilities": "custom", "version": "1.0"})

    def test_download_with_default_url(self):
        """Test downloading capabilities using the default URL from plugin settings."""
        plg_settings = PlgOptionsManager().get_plg_settings()
        default_url = plg_settings.url_service

        self.configure_url_response(
            default_url, response_data={"capabilities": "default_settings"}
        )

        result = download_getcapabilities()
        self.assertEqual(result, {"capabilities": "default_settings"})

    def test_multiple_calls_to_same_url(self):
        """Test multiple calls to the same URL with caching."""
        self.configure_url_response(
            "repeat.example.com", response_data={"capabilities": "repeated"}
        )

        url = "https://repeat.example.com/service"
        result1 = download_getcapabilities(url)
        result2 = download_getcapabilities(url)
        result3 = download_getcapabilities(url)

        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)

        # Grâce au cache, une seule requête devrait suffire
        self.assertEqual(self.call_count, 1)

        # Tester une autre URL
        self.configure_url_response(
            "repeat.example.com/different-service",
            response_data={"capabilities": "different"},
        )

        _ = download_getcapabilities("https://repeat.example.com/different-service")
        self.assertEqual(self.call_count, 2)


if __name__ == "__main__":
    unittest.main()
