"""
Permission Test Template — Python / pytest / requests
=====================================================

This is a REFERENCE implementation showing how permission tests can be structured.
The AI agent should adapt this template to match the target project's technology
stack, conventions, and existing infrastructure.

If the target project uses:
- Java/JUnit → generate JUnit test classes instead
- JavaScript/Jest → generate Jest test files instead
- Go → generate Go test files instead
- Different HTTP client → use the project's existing client

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


# =============================================================================
# Token Manager
# =============================================================================


class TokenManager:
    """
    Manages authentication tokens for test roles.

    - Acquires tokens once per role at session start
    - Caches tokens for reuse across all tests
    - Handles token refresh on 401 responses
    """

    def __init__(self):
        self._tokens: dict[str, str] = {}

    def get_token(self, role: str) -> str:
        """Get a cached token for the given role, acquiring if necessary."""
        if role not in self._tokens:
            self._tokens[role] = self._acquire_token(role)
        return self._tokens[role]

    def _acquire_token(self, role: str) -> str:
        """Authenticate as a user with the given role and extract the token."""
        user = self._find_user_by_role(role)
        if not user:
            pytest.skip(f"No user configured for role: {role}")

        url = f"{BASE_URL}{AUTH_CONFIG['endpoint']}"
        body = {
            AUTH_CONFIG["username_field"]: os.path.expandvars(user["username"]),
            AUTH_CONFIG["password_field"]: os.path.expandvars(user["password"]),
        }

        response = requests.request(
            method=AUTH_CONFIG["method"],
            url=url,
            json=body if AUTH_CONFIG["body_format"] == "json" else None,
            data=body if AUTH_CONFIG["body_format"] == "form" else None,
        )
        response.raise_for_status()

        data = response.json()
        token = self._extract_nested(data, AUTH_CONFIG["token_field"])
        return token

    def _find_user_by_role(self, role: str) -> dict | None:
        """Find the first user configured for the given role."""
        for user in users_config["users"]:
            if user["role"] == role:
                return user
        return None

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

    - Injects the correct token for the specified role
    - Supports all HTTP methods
    - Can send requests without authentication (for auth tests)
    """

    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager

    def request(
        self,
        method: str,
        path: str,
        role: str | None = None,
        json: dict | None = None,
        params: dict | None = None,
        no_auth: bool = False,
        token_override: str | None = None,
    ) -> requests.Response:
        """Send an HTTP request with the appropriate authentication."""
        url = f"{BASE_URL}{path}"
        headers = {}

        if not no_auth:
            token = token_override or self.token_manager.get_token(role)
            header_name = AUTH_CONFIG.get("token_header_name", "Authorization")
            header_prefix = AUTH_CONFIG.get("token_header_prefix", "Bearer")
            headers[header_name] = f"{header_prefix} {token}"

        return requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json,
            params=params,
        )

    def get(self, path, role=None, **kwargs):
        return self.request("GET", path, role=role, **kwargs)

    def post(self, path, role=None, json=None, **kwargs):
        return self.request("POST", path, role=role, json=json, **kwargs)

    def put(self, path, role=None, json=None, **kwargs):
        return self.request("PUT", path, role=role, json=json, **kwargs)

    def delete(self, path, role=None, **kwargs):
        return self.request("DELETE", path, role=role, **kwargs)


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
# Test Data
# =============================================================================
# The following variables should be populated from your YAML configuration.
# They are shown here as examples — the AI should generate actual values
# based on the target project's permission_matrix.yaml.

# Example resource IDs for testing (replace with actual test data setup)
OWN_RESOURCE_ID = "<own_resource_id>"
OTHER_RESOURCE_ID = "<other_user_resource_id>"
OTHER_DEPARTMENT_ID = "<other_department_id>"


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
        response = client.get("/api/<resources>", role="admin")
        assert response.status_code == 200

    def test_admin_can_create(self, client):
        response = client.post("/api/<resources>", role="admin", json={})
        assert response.status_code in (200, 201)

    def test_manager_can_query(self, client):
        response = client.get("/api/<resources>", role="manager")
        assert response.status_code == 200

    # --- Negative tests (should deny) ---

    def test_manager_cannot_delete(self, client):
        """Manager should not be able to delete — admin-only operation."""
        response = client.delete(f"/api/<resources>/{OWN_RESOURCE_ID}", role="manager")
        assert response.status_code == 403

    def test_user_cannot_create(self, client):
        """Regular user should not be able to create resources."""
        response = client.post("/api/<resources>", role="user", json={})
        assert response.status_code == 403

    def test_user_cannot_delete(self, client):
        """Regular user should not be able to delete resources."""
        response = client.delete(f"/api/<resources>/{OWN_RESOURCE_ID}", role="user")
        assert response.status_code == 403


# =============================================================================
# Data Permission Tests
# =============================================================================


class TestDataPermission:
    """Verify that data scope filtering works correctly."""

    def test_manager_can_access_own_department_data(self, client):
        """Manager should access data within their department."""
        response = client.get(f"/api/<resources>/{OWN_RESOURCE_ID}", role="manager")
        assert response.status_code == 200

    def test_manager_cannot_access_other_department_data(self, client):
        """Manager should NOT access data from another department."""
        response = client.get(
            f"/api/<resources>?departmentId={OTHER_DEPARTMENT_ID}",
            role="manager",
        )
        assert response.status_code == 403 or response.json().get("data") == []

    def test_user_can_access_own_data(self, client):
        """User should access their own data."""
        response = client.get(f"/api/<resources>/{OWN_RESOURCE_ID}", role="user")
        assert response.status_code == 200

    def test_user_cannot_access_other_user_data(self, client):
        """User should NOT access another user's data."""
        response = client.get(f"/api/<resources>/{OTHER_RESOURCE_ID}", role="user")
        assert response.status_code == 403


# =============================================================================
# Horizontal Privilege Escalation Tests
# =============================================================================


class TestHorizontalEscalation:
    """Verify that users cannot access other users' resources by ID manipulation."""

    def test_user_cannot_access_other_user_resource_by_path(self, client):
        """IDOR: User A should not access User B's resource via path parameter."""
        response = client.get(f"/api/<resources>/{OTHER_RESOURCE_ID}", role="user")
        assert response.status_code == 403

    def test_user_cannot_modify_other_user_resource(self, client):
        """IDOR: User A should not modify User B's resource."""
        response = client.put(
            f"/api/<resources>/{OTHER_RESOURCE_ID}",
            role="user",
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
        response = client.delete(f"/api/<resources>/{OWN_RESOURCE_ID}", role="user")
        assert response.status_code == 403

    def test_manager_cannot_perform_admin_delete(self, client):
        """Manager should not be able to delete (admin-only)."""
        response = client.delete(f"/api/<resources>/{OWN_RESOURCE_ID}", role="manager")
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
            role="user",
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
            f"/api/<resources>?departmentId={OTHER_DEPARTMENT_ID}",
            role="manager",
        )
        assert response.status_code == 403 or response.json().get("data") == []

    def test_role_injection_in_update(self, client):
        """Injecting role field in update request should not elevate privileges."""
        response = client.put(
            "/api/users/<self_id>",
            role="user",
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
            role="user",
            json={"ids": [OWN_RESOURCE_ID, OTHER_RESOURCE_ID]},
        )
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            body = response.json()
            returned_ids = [item.get("id") for item in body.get("data", [])]
            assert OTHER_RESOURCE_ID not in returned_ids, (
                "Batch response included unauthorized resource — batch authorization bypass"
            )


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
