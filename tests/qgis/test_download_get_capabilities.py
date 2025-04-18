# external
import pytest_httpserver

# Project
from gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser import (
    download_getcapabilities,
)


def test_different_urls_different_responses(httpserver: pytest_httpserver.HTTPServer):
    """Test that different URLs get different responses."""

    # pytest HTTPServer url
    server_url = httpserver.url_for("")

    # First request
    httpserver.expect_oneshot_request("/getcapabilities").respond_with_json(
        {"capabilities": "success"}
    )
    result_success = download_getcapabilities(server_url, forceRefresh=True)
    assert result_success == {"capabilities": "success"}

    # Second request
    httpserver.expect_oneshot_request("/getcapabilities").respond_with_json(
        {"capabilities": "custom", "version": "1.0"}
    )
    result_custom = download_getcapabilities(server_url, forceRefresh=True)
    assert result_custom == {"capabilities": "custom", "version": "1.0"}

    # Unavailable service
    result_error = download_getcapabilities("https://unavailable_service.data.gouv.fr")
    assert result_error is None


def test_multiple_calls_to_same_url(httpserver: pytest_httpserver.HTTPServer):
    """Test multiple calls to the same URL with caching."""

    # pytest HTTPServer url
    server_url = httpserver.url_for("")

    # First request, oneshot to be sure that second request won't use HTTPServer
    httpserver.expect_oneshot_request("/getcapabilities").respond_with_json(
        {"capabilities": "success"}
    )

    result_1 = download_getcapabilities(server_url, forceRefresh=True)
    assert result_1 == {"capabilities": "success"}

    # Even if HTTPServer is not returning a value, cache is used because forceRefresh is False
    result_2 = download_getcapabilities(server_url, forceRefresh=False)
    assert result_2 == result_1

    # Force refresh : None value returned
    result_error = download_getcapabilities(server_url, forceRefresh=True)
    assert result_error is None
