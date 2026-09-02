"""
Permission Tests — Demo: Employee Management API
=================================================

FICTIONAL EXAMPLE — This file demonstrates how the Permission Automation Testing
Skill generates test code. All endpoints, users, and data are completely fabricated.

Technology stack: Python 3.8+ / pytest / requests / PyYAML / python-dotenv
"""

import os
import pytest
import requests
import yaml
from pathlib import Path
from dotenv import load_dotenv

# =============================================================================
# Configuration
# =============================================================================

load_dotenv()

DEMO_DIR = Path(__file__).parent.parent
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")


def load_yaml(filename: str) -> dict:
    with open(DEMO_DIR / filename, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


users_config = load_yaml("users.yaml")
permissions_config = load_yaml("permissions.yaml")
matrix_config = load_yaml("permission_matrix.yaml")

AUTH_CONFIG = users_config["auth"]
TEST_DATA = users_config.get("test_data", {})


# =============================================================================
# Test Data Helpers — read from YAML, no hardcoded IDs
# =============================================================================


def _employee_id(user_name: str) -> int:
    """Look up employee_id by user name from test_data."""
    for emp in TEST_DATA.get("employees", []):
        if emp.get("user") == user_name:
            return emp["id"]
    pytest.fail(f"No employee_id found for user: {user_name}")


def _department_id(dept_name: str) -> str:
    """Look up department id by name from test_data."""
    for dept in TEST_DATA.get("departments", []):
        if dept["name"] == dept_name:
            return dept["id"]
    pytest.fail(f"No department found for: {dept_name}")


# =============================================================================
# Token Manager
# =============================================================================


class TokenManager:
    """
    Manages authentication tokens indexed by user name.

    - Each user in users.yaml has a unique "name" field.
    - Tokens are acquired once per user and cached for the session.
    - get_token(user="alice") gets Alice's token regardless of her role.
    """

    def __init__(self):
        self._tokens: dict[str, str] = {}

    def get_token(self, user: str) -> str:
        if user not in self._tokens:
            self._tokens[user] = self._acquire_token(user)
        return self._tokens[user]

    def get_user(self, user: str) -> dict:
        for u in users_config["users"]:
            if u["name"] == user:
                return u
        pytest.fail(f"No user configured with name: {user}")

    def _acquire_token(self, user: str) -> str:
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
        for key in AUTH_CONFIG["token_field"].split("."):
            data = data[key]
        return data

    def clear(self):
        self._tokens.clear()


# =============================================================================
# HTTP Client
# =============================================================================


class PermissionTestClient:
    """
    HTTP client for permission testing.

    - Requests authenticated by user name: client.get(path, user="alice")
    - Bearer prefix handled correctly (no double-prefix)
    - Supports no_auth=True and token_override for auth edge-case tests
    """

    def __init__(self, token_manager: TokenManager):
        self.tm = token_manager

    def _build_headers(
        self,
        user: str | None = None,
        no_auth: bool = False,
        token_override: str | None = None,
    ) -> dict:
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
def tm():
    token_manager = TokenManager()
    yield token_manager
    token_manager.clear()


@pytest.fixture(scope="session")
def client(tm):
    return PermissionTestClient(tm)


# =============================================================================
# 1. Authentication Tests
# =============================================================================


class TestAuthentication:
    """Verify that all protected APIs reject unauthenticated requests."""

    def test_no_token_list_employees(self, client):
        """GET /api/employees without token -> 401"""
        resp = client.get("/api/employees", no_auth=True)
        assert resp.status_code == 401

    def test_no_token_get_employee(self, client):
        """GET /api/employees/{id} without token -> 401"""
        emp_id = _employee_id("alice")
        resp = client.get(f"/api/employees/{emp_id}", no_auth=True)
        assert resp.status_code == 401

    def test_no_token_create_employee(self, client):
        """POST /api/employees without token -> 401"""
        resp = client.post("/api/employees", json={"name": "Test"}, no_auth=True)
        assert resp.status_code == 401

    def test_no_token_delete_employee(self, client):
        """DELETE /api/employees/{id} without token -> 401"""
        emp_id = _employee_id("alice")
        resp = client.delete(f"/api/employees/{emp_id}", no_auth=True)
        assert resp.status_code == 401

    def test_invalid_token(self, client):
        """GET /api/employees with invalid token -> 401"""
        resp = client.get("/api/employees", token_override="not_a_valid_token")
        assert resp.status_code == 401

    def test_malformed_bearer(self, client):
        """GET /api/employees with malformed Bearer -> 401"""
        resp = client.get("/api/employees", token_override="Bearer ")
        assert resp.status_code == 401

    def test_expired_token(self, client):
        """GET /api/employees with expired token -> 401"""
        expired = os.getenv("EXPIRED_TOKEN", "expired.jwt.token")
        resp = client.get("/api/employees", token_override=expired)
        assert resp.status_code == 401


# =============================================================================
# 2. Role Permission Tests — Admin (all should allow)
# =============================================================================


class TestAdminPermissions:
    """Admin has full access to all operations and all data."""

    def test_admin_can_list_employees(self, client):
        resp = client.get("/api/employees", user="admin_user")
        assert resp.status_code == 200

    def test_admin_can_get_any_employee(self, client):
        emp_id = _employee_id("alice")
        resp = client.get(f"/api/employees/{emp_id}", user="admin_user")
        assert resp.status_code == 200

    def test_admin_can_get_cross_department_employee(self, client):
        """Admin can access employees from any department."""
        emp_id = _employee_id("charlie")
        resp = client.get(f"/api/employees/{emp_id}", user="admin_user")
        assert resp.status_code == 200

    def test_admin_can_create_employee(self, client):
        dept = _department_id("Engineering")
        resp = client.post("/api/employees", user="admin_user", json={
            "name": "New Employee",
            "department": dept,
        })
        assert resp.status_code in (200, 201)

    def test_admin_can_update_any_employee(self, client):
        emp_id = _employee_id("alice")
        resp = client.put(f"/api/employees/{emp_id}", user="admin_user", json={
            "name": "Updated Name",
        })
        assert resp.status_code == 200

    def test_admin_can_delete_employee(self, client):
        emp_id = _employee_id("bob")
        resp = client.delete(f"/api/employees/{emp_id}", user="admin_user")
        assert resp.status_code == 200


# =============================================================================
# 3. Role Permission Tests — Manager (positive)
# =============================================================================


class TestManagerPositivePermissions:
    """Manager can query, create, update within department scope."""

    def test_manager_can_list_department_employees(self, client):
        resp = client.get("/api/employees", user="manager_a")
        assert resp.status_code == 200

    def test_manager_can_get_department_employee(self, client):
        """Manager A (Engineering) can access Alice (Engineering)."""
        emp_id = _employee_id("alice")
        resp = client.get(f"/api/employees/{emp_id}", user="manager_a")
        assert resp.status_code == 200

    def test_manager_can_create_employee(self, client):
        dept = _department_id("Engineering")
        resp = client.post("/api/employees", user="manager_a", json={
            "name": "New Engineer",
            "department": dept,
        })
        assert resp.status_code in (200, 201)

    def test_manager_can_update_department_employee(self, client):
        emp_id = _employee_id("alice")
        resp = client.put(f"/api/employees/{emp_id}", user="manager_a", json={
            "name": "Updated by Manager",
        })
        assert resp.status_code == 200


# =============================================================================
# 4. Role Permission Tests — Manager (negative: cannot delete)
# =============================================================================


class TestManagerNegativePermissions:
    """Manager cannot delete — this is admin-only."""

    def test_manager_cannot_delete_employee(self, client):
        """Vertical privilege escalation: manager -> delete -> 403"""
        emp_id = _employee_id("alice")
        resp = client.delete(f"/api/employees/{emp_id}", user="manager_a")
        assert resp.status_code == 403

    def test_manager_cannot_delete_any_employee(self, client):
        emp_id = _employee_id("bob")
        resp = client.delete(f"/api/employees/{emp_id}", user="manager_a")
        assert resp.status_code == 403


# =============================================================================
# 5. Role Permission Tests — Employee (negative)
# =============================================================================


class TestEmployeeNegativePermissions:
    """Employee cannot list, create, or delete."""

    def test_employee_cannot_list_all_employees(self, client):
        resp = client.get("/api/employees", user="alice")
        assert resp.status_code == 403

    def test_employee_cannot_create_employee(self, client):
        resp = client.post("/api/employees", user="alice", json={
            "name": "Unauthorized",
        })
        assert resp.status_code == 403

    def test_employee_cannot_delete_any_employee(self, client):
        emp_id = _employee_id("alice")
        resp = client.delete(f"/api/employees/{emp_id}", user="alice")
        assert resp.status_code == 403


# =============================================================================
# 6. Role Permission Tests — Employee (positive: self only)
# =============================================================================


class TestEmployeeSelfPermissions:
    """Employee can only view and update their own record."""

    def test_employee_can_view_own_record(self, client):
        """Alice can view her own employee record."""
        emp_id = _employee_id("alice")
        resp = client.get(f"/api/employees/{emp_id}", user="alice")
        assert resp.status_code == 200

    def test_employee_can_update_own_record(self, client):
        """Alice can update her own employee record."""
        emp_id = _employee_id("alice")
        resp = client.put(f"/api/employees/{emp_id}", user="alice", json={
            "phone": "555-0101",
        })
        assert resp.status_code == 200


# =============================================================================
# 7. Data Permission Tests
# =============================================================================


class TestDataPermissions:
    """Verify data scope filtering per role."""

    def test_manager_a_can_access_engineering_employee(self, client):
        """Manager A (dept-1) can access Alice (dept-1)."""
        emp_id = _employee_id("alice")
        resp = client.get(f"/api/employees/{emp_id}", user="manager_a")
        assert resp.status_code == 200

    def test_manager_a_cannot_access_marketing_employee(self, client):
        """Manager A (dept-1) CANNOT access Charlie (dept-2)."""
        emp_id = _employee_id("charlie")
        resp = client.get(f"/api/employees/{emp_id}", user="manager_a")
        assert resp.status_code == 403

    def test_manager_a_cannot_list_marketing_department(self, client):
        """Manager A (dept-1) CANNOT list Marketing department employees."""
        dept = _department_id("Marketing")
        resp = client.get(f"/api/departments/{dept}/employees", user="manager_a")
        assert resp.status_code == 403

    def test_manager_b_cannot_access_engineering_employee(self, client):
        """Manager B (dept-2) CANNOT access Alice (dept-1)."""
        emp_id = _employee_id("alice")
        resp = client.get(f"/api/employees/{emp_id}", user="manager_b")
        assert resp.status_code == 403

    def test_admin_can_access_all_departments(self, client):
        """Admin has no data scope restriction."""
        emp_alice = _employee_id("alice")
        emp_charlie = _employee_id("charlie")
        resp_eng = client.get(f"/api/employees/{emp_alice}", user="admin_user")
        resp_mkt = client.get(f"/api/employees/{emp_charlie}", user="admin_user")
        assert resp_eng.status_code == 200
        assert resp_mkt.status_code == 200


# =============================================================================
# 8. Horizontal Privilege Escalation Tests
# =============================================================================


class TestHorizontalEscalation:
    """Verify employees cannot access other employees' records."""

    def test_alice_cannot_view_bob(self, client):
        """Alice (101) CANNOT view Bob's record (102) — same department."""
        emp_id = _employee_id("bob")
        resp = client.get(f"/api/employees/{emp_id}", user="alice")
        assert resp.status_code == 403

    def test_alice_cannot_update_bob(self, client):
        """Alice (101) CANNOT update Bob's record (102)."""
        emp_id = _employee_id("bob")
        resp = client.put(f"/api/employees/{emp_id}", user="alice", json={
            "name": "Hacked by Alice",
        })
        assert resp.status_code == 403

    def test_alice_cannot_view_charlie(self, client):
        """Alice (101) CANNOT view Charlie's record (201) — different department."""
        emp_id = _employee_id("charlie")
        resp = client.get(f"/api/employees/{emp_id}", user="alice")
        assert resp.status_code == 403

    def test_alice_cannot_delete_bob(self, client):
        """Alice (101) CANNOT delete Bob's record (102)."""
        emp_id = _employee_id("bob")
        resp = client.delete(f"/api/employees/{emp_id}", user="alice")
        assert resp.status_code == 403

    def test_bob_cannot_view_alice(self, client):
        """Bob (102) CANNOT view Alice's record (101) — reverse direction."""
        emp_id = _employee_id("alice")
        resp = client.get(f"/api/employees/{emp_id}", user="bob")
        assert resp.status_code == 403


# =============================================================================
# 9. Vertical Privilege Escalation Tests
# =============================================================================


class TestVerticalEscalation:
    """Verify lower roles cannot perform higher-role operations."""

    def test_employee_cannot_admin_delete(self, client):
        """Employee -> DELETE (admin-only) -> 403"""
        emp_id = _employee_id("alice")
        resp = client.delete(f"/api/employees/{emp_id}", user="alice")
        assert resp.status_code == 403

    def test_manager_cannot_admin_delete(self, client):
        """Manager -> DELETE (admin-only) -> 403"""
        emp_id = _employee_id("alice")
        resp = client.delete(f"/api/employees/{emp_id}", user="manager_a")
        assert resp.status_code == 403

    def test_employee_cannot_create(self, client):
        """Employee -> CREATE (manager+only) -> 403"""
        resp = client.post("/api/employees", user="alice", json={
            "name": "Unauthorized Create",
        })
        assert resp.status_code == 403

    def test_employee_cannot_list_all(self, client):
        """Employee -> LIST (manager+only) -> 403"""
        resp = client.get("/api/employees", user="alice")
        assert resp.status_code == 403


# =============================================================================
# 10. Parameter Tampering Tests
# =============================================================================


class TestParameterTampering:
    """Verify that modifying identity/scope parameters does not bypass permissions."""

    def test_employee_tampers_department_in_update(self, client):
        """Alice tries to change her department to Marketing via self-update."""
        emp_id = _employee_id("alice")
        other_dept = _department_id("Marketing")
        resp = client.put(f"/api/employees/{emp_id}", user="alice", json={
            "departmentId": other_dept,
        })
        if resp.status_code == 200:
            body = resp.json()
            assert body.get("departmentId") != other_dept or body.get("department") != other_dept, (
                "VULNERABILITY: departmentId was accepted from employee self-update"
            )

    def test_employee_tampers_role_in_update(self, client):
        """Alice tries to elevate her role to admin via self-update."""
        emp_id = _employee_id("alice")
        resp = client.put(f"/api/employees/{emp_id}", user="alice", json={
            "role": "admin",
        })
        if resp.status_code == 200:
            body = resp.json()
            assert body.get("role") != "admin", (
                "VULNERABILITY: role was accepted from employee self-update — role injection"
            )

    def test_employee_tampers_employee_id_in_create(self, client):
        """Employee tries to create with a specific employeeId and role."""
        resp = client.post("/api/employees", user="alice", json={
            "name": "Fake Admin",
            "employeeId": 999,
            "role": "manager",
        })
        assert resp.status_code == 403, (
            "Employee should not be able to create employees at all"
        )

    def test_manager_tampers_department_query(self, client):
        """Manager A tries to query Marketing department via query parameter."""
        other_dept = _department_id("Marketing")
        resp = client.get(
            "/api/employees",
            user="manager_a",
            params={"departmentId": other_dept},
        )
        if resp.status_code == 200:
            body = resp.json()
            employees = body.get("data", body.get("employees", []))
            for emp in employees:
                assert emp.get("department") != other_dept, (
                    f"VULNERABILITY: Manager A received Marketing employee: {emp}"
                )

    def test_manager_tampers_department_in_create(self, client):
        """Manager A tries to create employee in Marketing department."""
        other_dept = _department_id("Marketing")
        resp = client.post("/api/employees", user="manager_a", json={
            "name": "Planted Employee",
            "department": other_dept,
        })
        if resp.status_code in (200, 201):
            body = resp.json()
            assert body.get("department") != other_dept or body.get("departmentId") != other_dept, (
                "VULNERABILITY: Manager created employee in another department"
            )


# =============================================================================
# 11. Batch Authorization Tests
# =============================================================================


class TestBatchAuthorization:
    """Verify batch operations enforce per-item permission checks."""

    def test_employee_batch_with_own_and_other_id(self, client):
        """Alice batch queries with own ID + Bob's ID."""
        own_id = _employee_id("alice")
        other_id = _employee_id("bob")
        resp = client.post("/api/employees/batch", user="alice", json={
            "ids": [own_id, other_id],
        })
        assert resp.status_code in (200, 403)
        if resp.status_code == 200:
            body = resp.json()
            returned_ids = [e.get("id") for e in body.get("data", [])]
            assert other_id not in returned_ids, (
                "VULNERABILITY: Batch returned unauthorized employee"
            )

    def test_employee_batch_with_all_unauthorized_ids(self, client):
        """Alice batch queries with only unauthorized IDs."""
        other_id = _employee_id("bob")
        cross_dept_id = _employee_id("charlie")
        resp = client.post("/api/employees/batch", user="alice", json={
            "ids": [other_id, cross_dept_id],
        })
        assert resp.status_code in (200, 403)
        if resp.status_code == 200:
            body = resp.json()
            data = body.get("data", [])
            assert len(data) == 0, (
                "VULNERABILITY: Batch returned data for all-unauthorized IDs"
            )

    def test_manager_batch_with_own_dept_and_other_dept(self, client):
        """Manager A batch queries with own-dept + other-dept IDs."""
        own_dept_id = _employee_id("alice")
        other_dept_id = _employee_id("charlie")
        resp = client.post("/api/employees/batch", user="manager_a", json={
            "ids": [own_dept_id, other_dept_id],
        })
        assert resp.status_code in (200, 403)
        if resp.status_code == 200:
            body = resp.json()
            returned_ids = [e.get("id") for e in body.get("data", [])]
            assert other_dept_id not in returned_ids, (
                "VULNERABILITY: Batch returned employee from other department"
            )


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
