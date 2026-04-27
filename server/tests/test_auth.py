import os
import unittest
from unittest.mock import MagicMock, patch

from server import create_app
from server.config import DEFAULTS
from server.tests.utils import TEST_CONFIG, make_db, saved_config


class AuthStatusTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TEST_CONFIG)
        self.client = self.app.test_client()

    def test_returns_false_when_not_authenticated(self):
        res = self.client.get("/api/auth/status")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.get_json()["authenticated"])

    def test_returns_true_when_authenticated(self):
        with self.client.session_transaction() as sess:
            sess["authenticated"] = True
        res = self.client.get("/api/auth/status")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["authenticated"])


class RequireAuthTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TEST_CONFIG)
        self.client = self.app.test_client()

    def test_protected_route_rejects_unauthenticated(self):
        res = self.client.get("/api/state")
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.get_json()["ok"])

    def test_protected_route_allows_authenticated(self):
        with self.client.session_transaction() as sess:
            sess["authenticated"] = True
        with patch("server.db.load", return_value=make_db()):
            res = self.client.get("/api/state")
        self.assertEqual(res.status_code, 200)


class OAuthStartTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TEST_CONFIG)
        self.client = self.app.test_client()

    def test_returns_google_consent_url(self):
        mock_flow = MagicMock()
        mock_flow.authorization_url.return_value = ("https://accounts.google.com/consent", "state-abc")

        with (
            patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "cid", "GOOGLE_CLIENT_SECRET": "csec"}),
            patch("server.api.Flow") as MockFlow,
        ):
            MockFlow.from_client_config.return_value = mock_flow
            res = self.client.get("/api/oauth/start")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["url"], "https://accounts.google.com/consent")

    def test_stores_state_in_session(self):
        mock_flow = MagicMock()
        mock_flow.authorization_url.return_value = ("https://accounts.google.com/consent", "state-xyz")

        with (
            patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "cid", "GOOGLE_CLIENT_SECRET": "csec"}),
            patch("server.api.Flow") as MockFlow,
        ):
            MockFlow.from_client_config.return_value = mock_flow
            self.client.get("/api/oauth/start")

        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get("oauth_state"), "state-xyz")


class OAuthCallbackTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TEST_CONFIG)
        self.client = self.app.test_client()

    def _mock_flow(self, refresh_token="reftok"):
        mock_creds = MagicMock()
        mock_creds.refresh_token = refresh_token
        mock_flow = MagicMock()
        mock_flow.credentials = mock_creds
        return mock_flow

    def test_stores_refresh_token_and_email(self):
        with self.client.session_transaction() as sess:
            sess["oauth_state"] = "state-abc"

        mock_userinfo_svc = MagicMock()
        mock_userinfo_svc.userinfo().get().execute.return_value = {"email": "user@gmail.com"}

        with saved_config({**DEFAULTS}) as saved:
            with (
                patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "cid", "GOOGLE_CLIENT_SECRET": "csec"}),
                patch("server.api.Flow") as MockFlow,
                patch("server.api.build", return_value=mock_userinfo_svc),
            ):
                MockFlow.from_client_config.return_value = self._mock_flow()
                self.client.get("/api/oauth/callback?code=authcode&state=state-abc")

        self.assertEqual(saved.get("googleRefreshToken"), "reftok")
        self.assertEqual(saved.get("googleEmail"), "user@gmail.com")

    def test_redirects_to_root(self):
        with self.client.session_transaction() as sess:
            sess["oauth_state"] = "state-abc"

        with saved_config({**DEFAULTS}):
            with (
                patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "cid", "GOOGLE_CLIENT_SECRET": "csec"}),
                patch("server.api.Flow") as MockFlow,
                patch("server.api.build", return_value=MagicMock()),
            ):
                MockFlow.from_client_config.return_value = self._mock_flow()
                res = self.client.get("/api/oauth/callback?code=authcode&state=state-abc")

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.headers["Location"], "/")

    def test_sets_authenticated_in_session(self):
        with self.client.session_transaction() as sess:
            sess["oauth_state"] = "state-abc"

        with saved_config({**DEFAULTS}):
            with (
                patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "cid", "GOOGLE_CLIENT_SECRET": "csec"}),
                patch("server.api.Flow") as MockFlow,
                patch("server.api.build", return_value=MagicMock()),
            ):
                MockFlow.from_client_config.return_value = self._mock_flow()
                self.client.get("/api/oauth/callback?code=authcode&state=state-abc")

        res = self.client.get("/api/auth/status")
        self.assertTrue(res.get_json()["authenticated"])


class LogoutTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TEST_CONFIG)
        self.client = self.app.test_client()

    def test_logout_clears_session(self):
        with self.client.session_transaction() as sess:
            sess["authenticated"] = True

        res = self.client.post("/api/logout")
        self.assertEqual(res.status_code, 200)

        status = self.client.get("/api/auth/status")
        self.assertFalse(status.get_json()["authenticated"])


class ConfigCalendarFetchTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TEST_CONFIG)
        self.client = self.app.test_client()
        with self.client.session_transaction() as sess:
            sess["authenticated"] = True

    def test_fetches_user_calendars_when_refresh_token_present(self):
        cfg = {**DEFAULTS, "googleRefreshToken": "reftok"}
        mock_svc = MagicMock()
        mock_svc.calendarList().list().execute.return_value = {
            "items": [{"id": "a@gmail.com", "summary": "Personal"}]
        }

        with (
            patch("server.config.load", return_value=cfg),
            patch("server.api.Credentials"),
            patch("server.api.build", return_value=mock_svc),
        ):
            res = self.client.get("/api/config")

        self.assertEqual(res.status_code, 200)
        user_cals = res.get_json()["userCalendars"]
        self.assertEqual(len(user_cals), 1)
        self.assertEqual(user_cals[0]["id"], "a@gmail.com")
        self.assertEqual(user_cals[0]["summary"], "Personal")

    def test_returns_empty_user_calendars_without_refresh_token(self):
        with patch("server.config.load", return_value={**DEFAULTS}):
            res = self.client.get("/api/config")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["userCalendars"], [])

    def test_returns_empty_user_calendars_on_api_error(self):
        cfg = {**DEFAULTS, "googleRefreshToken": "reftok"}
        mock_svc = MagicMock()
        mock_svc.calendarList().list().execute.side_effect = Exception("API error")

        with (
            patch("server.config.load", return_value=cfg),
            patch("server.api.Credentials"),
            patch("server.api.build", return_value=mock_svc),
        ):
            res = self.client.get("/api/config")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["userCalendars"], [])


if __name__ == "__main__":
    unittest.main()
