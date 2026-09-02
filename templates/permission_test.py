"""
Permission Test Template — Python / pytest / requests
=====================================================

This is a REFERENCE implementation showing how permission tests can be structured.
The AI agent should adapt this template to match the target project's technology
stack, conventions, and existing infrastructure.

If the target project uses:
- Java/JUnit -> generate JUnit test classes instead
- JavaScript/Jest -> generate Jest test files instead
- Go -> generate Go test files instead
- Different HTTP client -> use the project's existing client

This template assumes:
- Python 3.8+
- pytest
- requests
- PyYAML
- python-dotenv

The AI should check the target project FIRST and reuse existing infrastructure.
"""

import os
import pytest
import requests
import yaml
from pathlib import Path
from dotenv import load_dotenv

# =============================================================================
# Configuration Loading
# =============================================================================

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"  # Adjust path to where YAML files are located


def load_yaml(filename: str) -> dict:
    """Load a YAML configuration file."""
    filepath = DATA_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Load configuration
users_config = load_yaml("users.yaml")
permissions_config = load_yaml("permissions.yaml")
matrix_config = load_yaml("permission_matrix.yaml")

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
AUTH_CONFIG = users_config["auth"]
TEST_DATA = users_config.get("test_data", {})


# =============================================================================
# Token Manager
# =============================================================================


class TokenManager:
    """
    Manages authentication tokens indexed by user name.

    - Each user in users.yaml must have a unique "name" field.
    - Tokens are acquired once per user and cached for the session.
    - Use get_token(user="alice") to get Alice's token, regardless of her role.
    - This allows multiple users with the same role to be distinguished
      (e.g., alice and bob are both "employee" but need different tokens).
    """

    def __init__(self):
        self._tokens: dict[str, str] = {}

    def get_token(self, user: str) -> str:
        """Get a cached token for the given user name, acquiring if necessary."""
        if user not in self._tokens:
            self._tokens[user] = self._acquire_token(user)
        return self._tokens[user]

    def get_user(self, user: str) -> dict:
        """Get the full user config by name."""
        for u in users_config["users"]:
            if u["name"] == user:
                return u
        pytest.fail(f"No user configured with name: {user}")

    def _acquire_token(self, user: str) -> str:
        """Authenticate as the given user and extract the token."""
        user_cfg = self.get_user(user)

        url = f"{BASE_URL}{AUTH_CONFIG['endpoint']}"
        body = {
            AUTH_CONFIG["username_field"]: os.path.expandvars(user_cfg["username"]),
            AUTH_CONFIG["password_field"]: os.path.expandvars(user_cfg["password"]),
        }

        response = requests.request(
            method=AUTH_CONFIG["method"],
            url=url,
            json=body if AUTH_CONFIG["body_format"] == "json" else None,
            data=body if AUTH_CONFIG["body_format"] == "form" else None,
        )
        response.raise_for_status()

        data = response.json()
        return self._extract_nested(data, AUTH_CONFIG["token_field"])

    @staticmethod
    def _extract_nested(data: dict, path: str) -> str:
        """Extract a value from a nested dict using dot notation."""
        keys = path.split(".")
        for key in keys:
            data = data[key]
        return data

    def clear(self):
        """Clear all cached tokens."""
        self._tokens.clear()


# =============================================================================
# HTTP Client
# =============================================================================


class PermissionTestClient:
    """
    HTTP client for permission testing.

    - Requests are authenticated by user name: client.get(path, user="alice")
    - Supports unauthenticated requests via no_auth=True
    - Supports token overrides for auth edge-case tests
    - Bearer prefix is handled correctly: if the token already starts with
      the configured prefix, it won't be added again.
    """

    def __init__(self, token_manager: TokenManager):
        self.tm = token_manager

    def _build_headers(
        self,
        user: str | None = None,
        no_auth: bool = False,
        token_override: str | None = None,
    ) -> dict:
        """Build authentication headers."""
        if no_auth:
            return {}

        header_name = AUTH_CONFIG.get("token_header_name", "Authorization")
        header_prefix = AUTH_CONFIG.get("token_header_prefix", "Bearer")

        if token_override is not None:
            token = token_override
        elif user:
            token = self.tm.get_token(user)
        else:
            return {}

        # Avoid double-prefix: "Bearer Bearer xxx"
        if header_prefix and token.startswith(f"{header_prefix} "):
            return {header_name: token}

        return {header_name: f"{header_prefix} {token}"}

    def request(
        self,
        method: str,
        path: str,
        user: str | None = None,
        json: dict | None = None,
        params: dict | None = None,
        no_auth: bool = False,
        token_override: str | None = None,
    ) -> requests.Response:
        """Send an HTTP request with the appropriate authentication."""
        url = f"{BASE_URL}{path}"
        headers = self._build_headers(user=user, no_auth=no_auth, token_override=token_override)

        return requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json,
            params=params,
        )

    def get(self, path, user=None, **kwargs):
        return self.request("GET", path, user=user, **kwargs)

    def post(self, path, user=None, json=None, **kwargs):
        return self.request("POST", path, user=user, json=json, **kwargs)

    def put(self, path, user=None, json=None, **kwargs):
        return self.request("PUT", path, user=user, json=json, **kwargs)

    def delete(self, path, user=None, **kwargs):
        return self.request("DELETE", path, user=user, **kwargs)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def token_manager():
    """Session-scoped token manager — acquires tokens once for all tests."""
    manager = TokenManager()
    yield manager
    manager.clear()


@pytest.fixture(scope="session")
def client(token_manager):
    """Session-scoped HTTP client with token injection."""
    return PermissionTestClient(token_manager)


# =============================================================================
# Test Data Helpers
# =============================================================================
# Load test data references from users.yaml so tests don't hardcode IDs.
# Adapt these to match your project's test_data structure.

# Example:
# OWN_RESOURCE_ID = TEST_DATA.get("own_resource_id", "<own_resource_id>")
# OTHER_RESOURCE_ID = TEST_DATA.get("other_resource_id", "<other_resource_id>")


# =============================================================================
# Authentication Tests
# =============================================================================


class TestAuthentication:
    """Verify that protected APIs require valid authentication."""

    def test_no_token_returns_401(self, client):
        """Request without any token should be rejected."""
        response = client.get("/api/<resources>", no_auth=True)
        assert response.status_code == 401

    def test_invalid_token_returns_401(self, client):
        """Request with malformed token should be rejected."""
        response = client.get(
            "/api/<resources>",
            token_override="invalid_token_value",
        )
        assert response.status_code == 401

    def test_expired_token_returns_401(self, client):
        """Request with expired token should be rejected."""
        response = client.get(
            "/api/<resources>",
            token_override="<expired_token_value>",
        )
        assert response.status_code == 401


# =============================================================================
# Role Permission Tests (Vertical)
# =============================================================================


class TestRolePermission:
    """Verify that each role can only perform its authorized operations."""

    # --- Positive tests (should allow) ---

    def test_admin_can_query(self, client):
        response = client.get("/api/<resources>", user="admin_user")
        assert response.status_code == 200

    def test_admin_can_create(self, client):
        response = client.post("/api/<resources>", user="admin_user", json={})
        assert response.status_code in (200, 201)

    def test_manager_can_query(self, client):
        response = client.get("/api/<resources>", user="manager_user")
        assert response.status_code == 200

    # --- Negative tests (should deny) ---

    def test_manager_cannot_delete(self, client):
        """Manager should not be able to delete — admin-only operation."""
        response = client.delete(f"/api/<resources>/<own_resource_id>", user="manager_user")
        assert response.status_code == 403

    def test_user_cannot_create(self, client):
        """Regular user should not be able to create resources."""
        response = client.post("/api/<resources>", user="user_a", json={})
        assert response.status_code == 403

    def test_user_cannot_delete(self, client):
        """Regular user should not be able to delete resources."""
        response = client.delete(f"/api/<resources>/<own_resource_id>", user="user_a")
        assert response.status_code == 403


# =============================================================================
# Data Permission Tests
# =============================================================================


class TestDataPermission:
    """Verify that data scope filtering works correctly."""

    def test_manager_can_access_own_department_data(self, client):
        """Manager should access data within their department."""
        response = client.get(f"/api/<resources>/<own_resource_id>", user="manager_user")
        assert response.status_code == 200

    def test_manager_cannot_access_other_department_data(self, client):
        """Manager should NOT access data from another department."""
        response = client.get(
            f"/api/<resources>?departmentId=<other_department_id>",
            user="manager_user",
        )
        assert response.status_code == 403 or response.json().get("data") == []

    def test_user_can_access_own_data(self, client):
        """User should access their own data."""
        response = client.get(f"/api/<resources>/<own_resource_id>", user="user_a")
        assert response.status_code == 200

    def test_user_cannot_access_other_user_data(self, client):
        """User should NOT access another user's data."""
        response = client.get(f"/api/<resources>/<other_resource_id>", user="user_a")
        assert response.status_code == 403


# =============================================================================
# Horizontal Privilege Escalation Tests
# =============================================================================


class TestHorizontalEscalation:
    """Verify that users cannot access other users' resources by ID manipulation."""

    def test_user_cannot_access_other_user_resource_by_path(self, client):
        """IDOR: User A should not access User B's resource via path parameter."""
        response = client.get(f"/api/<resources>/<other_resource_id>", user="user_a")
        assert response.status_code == 403

    def test_user_cannot_modify_other_user_resource(self, client):
        """IDOR: User A should not modify User B's resource."""
        response = client.put(
            f"/api/<resources>/<other_resource_id>",
            user="user_a",
            json={"name": "tampered"},
        )
        assert response.status_code == 403


# =============================================================================
# Vertical Privilege Escalation Tests
# =============================================================================


class TestVerticalEscalation:
    """Verify that lower roles cannot perform higher-role operations."""

    def test_user_cannot_perform_admin_delete(self, client):
        """Regular user should not be able to delete (admin-only)."""
        response = client.delete(f"/api/<resources>/<own_resource_id>", user="user_a")
        assert response.status_code == 403

    def test_manager_cannot_perform_admin_delete(self, client):
        """Manager should not be able to delete (admin-only)."""
        response = client.delete(f"/api/<resources>/<own_resource_id>", user="manager_user")
        assert response.status_code == 403


# =============================================================================
# Parameter Tampering Tests
# =============================================================================


class TestParameterTampering:
    """Verify that modifying identity/scope parameters does not bypass permissions."""

    def test_owner_id_injection(self, client):
        """Injecting another user's ownerId should not grant access."""
        response = client.post(
            "/api/<resources>",
            user="user_a",
            json={"name": "test", "ownerId": "<another_user_id>"},
        )
        assert response.status_code in (403, 200)
        if response.status_code == 200:
            body = response.json()
            assert body.get("ownerId") != "<another_user_id>", (
                "ownerId was accepted from request body — mass assignment vulnerability"
            )

    def test_department_id_injection(self, client):
        """Injecting another department's departmentId should not grant access."""
        response = client.get(
            f"/api/<resources>?departmentId=<other_department_id>",
            user="manager_user",
        )
        assert response.status_code == 403 or response.json().get("data") == []

    def test_role_injection_in_update(self, client):
        """Injecting role field in update request should not elevate privileges."""
        response = client.put(
            "/api/users/<self_id>",
            user="user_a",
            json={"role": "admin"},
        )
        assert response.status_code in (403, 200)
        if response.status_code == 200:
            body = response.json()
            assert body.get("role") != "admin", (
                "Role was accepted from request body — role injection vulnerability"
            )


# =============================================================================
# Batch Authorization Tests
# =============================================================================


class TestBatchAuthorization:
    """Verify that batch operations enforce per-item permission checks."""

    def test_batch_with_mixed_authorization(self, client):
        """Batch request should not return unauthorized resources."""
        response = client.post(
            "/api/<resources>/batch",
            user="user_a",
            json={"ids": ["<own_resource_id>", "<other_resource_id>"]},
        )
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            body = response.json()
            returned_ids = [item.get("id") for item in body.get("data", [])]
            assert "<other_resource_id>" not in returned_ids, (
                "Batch response included unauthorized resource — batch authorization bypass"
            )


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
