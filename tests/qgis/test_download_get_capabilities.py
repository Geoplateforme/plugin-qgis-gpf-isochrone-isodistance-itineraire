# standard
import json
from unittest.mock import MagicMock, Mock, patch

import pytest

# PyQGIS
from qgis.PyQt.QtNetwork import QNetworkRequest

# Project
from gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser import (
    download_getcapabilities,
)
from gpf_isochrone_isodistance_itineraire.toolbelt.preferences import PlgOptionsManager


@pytest.fixture(autouse=True)
def setup_blocking_request(monkeypatch):
    """Fixture to patch QgsBlockingNetworkRequest and prepare mocks."""

    patcher = patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.QgsBlockingNetworkRequest"
    )
    mock_class = patcher.start()
    mock_instance = MagicMock()

    url_configs = {}
    call_count = {"count": 0}

    def mock_get(request: QNetworkRequest, forceRefresh: bool = False) -> int:
        """Side effect for QgsBlockingNetworkRequest call

        :param request: request
        :type request: QNetworkRequest
        :param forceRefresh: force refresh, defaults to False
        :type forceRefresh: bool, optional
        :return: error code
        :rtype: int
        """

        call_count["count"] += 1
        url_requested = request.url().toString()
        for base_url, config in url_configs.items():
            if base_url in url_requested:
                mock_instance.errorMessage.return_value = config["error_message"]
                if config["response_data"] is not None:
                    mock_reply = MagicMock()
                    mock_reply.content.return_value = json.dumps(
                        config["response_data"]
                    ).encode("UTF-8")
                    mock_instance.reply.return_value = mock_reply
                return config["error_code"]
        return 0

    mock_instance.get.side_effect = mock_get
    mock_class.return_value = mock_instance

    mock_error_code = Mock()
    mock_error_code.NoError = 0
    mock_class.ErrorCode = mock_error_code

    yield {
        "mock_class": mock_class,
        "mock_instance": mock_instance,
        "url_configs": url_configs,
        "call_count": call_count,
    }

    patcher.stop()


def test_different_urls_different_responses(setup_blocking_request):
    """Test that different URLs get different responses."""

    setup_blocking_request["url_configs"]["success.example.com"] = {
        "response_data": {"capabilities": "success"},
        "error_code": 0,
        "error_message": "",
    }
    setup_blocking_request["url_configs"]["error.example.com"] = {
        "response_data": None,
        "error_code": 1,
        "error_message": "Network timeout",
    }
    setup_blocking_request["url_configs"]["custom.example.com"] = {
        "response_data": {"capabilities": "custom", "version": "1.0"},
        "error_code": 0,
        "error_message": "",
    }

    result_success = download_getcapabilities("https://success.example.com/service")
    assert result_success == {"capabilities": "success"}

    result_error = download_getcapabilities("https://error.example.com/service")
    assert result_error is None

    result_custom = download_getcapabilities("https://custom.example.com/service")
    assert result_custom == {"capabilities": "custom", "version": "1.0"}


def test_download_with_default_url(setup_blocking_request):
    """Test downloading capabilities using the default URL from plugin settings."""

    plg_settings = PlgOptionsManager().get_plg_settings()
    default_url = plg_settings.url_service

    setup_blocking_request["url_configs"][default_url] = {
        "response_data": {"capabilities": "default_settings"},
        "error_code": 0,
        "error_message": "",
    }

    result = download_getcapabilities()
    assert result == {"capabilities": "default_settings"}


def test_multiple_calls_to_same_url(setup_blocking_request):
    """Test multiple calls to the same URL with caching."""

    setup_blocking_request["url_configs"]["repeat.example.com"] = {
        "response_data": {"capabilities": "repeated"},
        "error_code": 0,
        "error_message": "",
    }

    url = "https://repeat.example.com/service"
    result1 = download_getcapabilities(url)
    result2 = download_getcapabilities(url)
    result3 = download_getcapabilities(url)

    assert result1 == result2 == result3

    # Une seule requête devrait suffire grâce au cache
    assert setup_blocking_request["call_count"]["count"] == 1

    # Tester une URL différente
    setup_blocking_request["url_configs"]["repeat.example.com/different-service"] = {
        "response_data": {"capabilities": "different"},
        "error_code": 0,
        "error_message": "",
    }

    _ = download_getcapabilities("https://repeat.example.com/different-service")
    assert setup_blocking_request["call_count"]["count"] == 2
