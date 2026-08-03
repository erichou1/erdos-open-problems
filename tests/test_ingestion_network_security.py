import unittest
from unittest import mock

import erdos_ingest
import fetch_categories
import fetch_erdos
import sync_problem_catalog


class _RequestsResponse:
    def __init__(self, payload: bytes = b"[]", *, url: str) -> None:
        self.url = url
        self.text = payload.decode("utf-8")
        self.headers: dict[str, str] = {}
        self.history: list[object] = []
        self.status_code = 200
        self._chunks = [payload]
        self.closed = False

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size: int):
        del chunk_size
        return iter(self._chunks)

    def close(self) -> None:
        self.closed = True


class _URLResponse:
    def __init__(self, payload: bytes = b"[]", *, url: str) -> None:
        self._payload = payload
        self._url = url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        return self._payload if size < 0 else self._payload[:size]

    def geturl(self) -> str:
        return self._url


class IngestionNetworkSecurityTests(unittest.TestCase):
    def test_all_remote_entry_points_reject_non_https_before_transport(self):
        with (
            mock.patch(
                "requests.sessions.Session.request",
                side_effect=AssertionError("requests transport was reached"),
            ) as requests_transport,
            mock.patch(
                "urllib.request.OpenerDirector.open",
                side_effect=AssertionError("urllib transport was reached"),
            ) as urllib_transport,
            mock.patch.object(fetch_erdos, "YAML_URL", "http://example.test/a"),
            mock.patch.object(fetch_erdos, "BASE_URL", "file:///tmp/source"),
            mock.patch.object(fetch_categories, "YAML_URL", "ftp://example.test/a"),
            mock.patch.object(fetch_categories, "BASE_URL", "http://example.test"),
        ):
            calls = (
                fetch_erdos.download_yaml,
                lambda: fetch_erdos.fetch_latex_source(1),
                fetch_categories.download_yaml,
                lambda: fetch_categories.fetch_latex_source(1),
                lambda: erdos_ingest.fetch_url("file:///etc/passwd"),
                lambda: sync_problem_catalog.fetch_source("data:text/plain,unsafe"),
            )
            for call in calls:
                with self.subTest(call=call):
                    with self.assertRaises(ValueError):
                        call()

        requests_transport.assert_not_called()
        urllib_transport.assert_not_called()

    def test_requests_preserve_default_certificate_verification(self):
        calls = (
            fetch_erdos.download_yaml,
            lambda: fetch_erdos.fetch_latex_source(1),
            fetch_categories.download_yaml,
            lambda: fetch_categories.fetch_latex_source(1),
            lambda: erdos_ingest.fetch_url("https://example.test/source"),
            lambda: sync_problem_catalog.fetch_source(
                "https://example.test/catalog"
            ),
        )
        for call in calls:
            with self.subTest(call=call):
                response = _RequestsResponse(url="https://example.test/final")
                with (
                    mock.patch(
                        "requests.sessions.Session.request",
                        return_value=response,
                    ) as transport,
                    mock.patch(
                        "urllib.request.OpenerDirector.open",
                        return_value=_URLResponse(
                            url="https://example.test/final"
                        ),
                    ),
                ):
                    call()
                self.assertTrue(transport.called)
                self.assertNotIn("verify", transport.call_args.kwargs)

    def test_all_remote_entry_points_reject_non_https_final_url(self):
        calls = (
            fetch_erdos.download_yaml,
            lambda: fetch_erdos.fetch_latex_source(1),
            fetch_categories.download_yaml,
            lambda: fetch_categories.fetch_latex_source(1),
            lambda: erdos_ingest.fetch_url("https://example.test/source"),
            lambda: sync_problem_catalog.fetch_source(
                "https://example.test/catalog"
            ),
        )
        for call in calls:
            with self.subTest(call=call):
                response = _RequestsResponse(url="http://example.test/downgrade")
                with (
                    mock.patch(
                        "requests.sessions.Session.request",
                        return_value=response,
                    ),
                    mock.patch(
                        "urllib.request.OpenerDirector.open",
                        return_value=_URLResponse(
                            url="http://example.test/downgrade"
                        ),
                    ),
                ):
                    with self.assertRaises(ValueError):
                        call()

    def test_fetch_url_enforces_response_size_and_closes_response(self):
        response = _RequestsResponse(url="https://example.test/source")
        response._chunks = [b"123", b"45"]
        with mock.patch(
            "requests.sessions.Session.request", return_value=response
        ):
            with self.assertRaisesRegex(ValueError, "size limit"):
                erdos_ingest.fetch_url(
                    "https://example.test/source", max_bytes=4
                )
        self.assertTrue(response.closed)

    def test_fetch_url_rejects_https_to_http_redirect_before_following_it(self):
        response = _RequestsResponse(url="https://example.test/source")
        response.status_code = 302
        response.headers["Location"] = "http://example.test/downgrade"
        with mock.patch(
            "requests.sessions.Session.request", return_value=response
        ) as transport:
            with self.assertRaises(ValueError):
                erdos_ingest.fetch_url("https://example.test/source")
        self.assertEqual(transport.call_count, 1)
        self.assertTrue(response.closed)


if __name__ == "__main__":
    unittest.main()
