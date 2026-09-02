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

# Employee IDs from test data
ALICE_ID = 101
BOB_ID = 102
CHARLIE_ID = 201
MANAGER_A_ID = 100
MANAGER_B_ID = 200

DEPT_1 = "dept-1"  # Engineering
DEPT_2 = "dept-2"  # Marketing


# =============================================================================
# Token Manager
# =============================================================================


class TokenManager:
    """Acquires and caches JWT tokens per role."""

    def __init__(self):
        self._tokens: dict[str, str] = {}

    def get_token(self, role: str) -> str:
        if role not in self._tokens:
            self._tokens[role] = self._acquire_token(role)
        return self._tokens[role]

    def get_user(self, role: str) -> dict:
        for user in users_config["users"]:
            if user["role"] == role:
                return user
        raise ValueError(f"No user configured for role: {role}")

    def get_user_by_description(self, keyword: str) -> dict:
        for user in users_config["users"]:
            if keyword.lower() in user.get("description", "").lower():
                return user
        raise ValueError(f"No user found matching: {keyword}")

    def _acquire_token(self, role: str) -> str:
        user = self.get_user(role)
        url = f"{BASE_URL}{AUTH_CONFIG['endpoint']}"
        body = {
            AUTH_CONFIG["username_field"]: os.path.expandvars(user["username"]),
            AUTH_CONFIG["password_field"]: os.path.expandvars(user["password"]),
        }
        response = requests.post(url, json=body)
        response.raise_for_status()
        data = response.json()
        token_path = AUTH_CONFIG["token_field"]
        for key in token_path.split("."):
            data = data[key]
        return data

    def clear(self):
        self._tokens.clear()


# =============================================================================
# HTTP Client
# =============================================================================


class TestClient:
    """HTTP client with role-based token injection."""

    def __init__(self, token_manager: TokenManager):
        self.tm = token_manager

    def _headers(self, role: str | None, token_override: str | None) -> dict:
        if token_override:
            token = token_override
        elif role:
            token = self.tm.get_token(role)
        else:
            return {}
        header_name = AUTH_CONFIG.get("token_header_name", "Authorization")
        prefix = AUTH_CONFIG.get("token_header_prefix", "Bearer")
        return {header_name: f"{prefix} {token}"}

    def get(self, path, role=None, token_override=None, params=None):
        return requests.get(
            f"{BASE_URL}{path}",
            headers=self._headers(role, token_override),
            params=params,
        )

    def post(self, path, role=None, token_override=None, json=None):
        return requests.post(
            f"{BASE_URL}{path}",
            headers=self._headers(role, token_override),
            json=json,
        )

    def put(self, path, role=None, token_override=None, json=None):
        return requests.put(
            f"{BASE_URL}{path}",
            headers=self._headers(role, token_override),
            json=json,
        )

    def delete(self, path, role=None, token_override=None):
        return requests.delete(
            f"{BASE_URL}{path}",
            headers=self._headers(role, token_override),
        )


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
    return TestClient(tm)


# =============================================================================
# 1. Authentication Tests
# =============================================================================


class TestAuthentication:
    """Verify that all protected APIs reject unauthenticated requests."""

    def test_no_token_list_employees(self, client):
        """GET /api/employees without token → 401"""
        resp = client.get("/api/employees")
        assert resp.status_code == 401

    def test_no_token_get_employee(self, client):
        """GET /api/employees/{id} without token → 401"""
        resp = client.get(f"/api/employees/{ALICE_ID}")
        assert resp.status_code == 401

    def test_no_token_create_employee(self, client):
        """POST /api/employees without token → 401"""
        resp = client.post("/api/employees", json={"name": "Test"})
        assert resp.status_code == 401

    def test_no_token_delete_employee(self, client):
        """DELETE /api/employees/{id} without token → 401"""
        resp = client.delete(f"/api/employees/{ALICE_ID}")
        assert resp.status_code == 401

    def test_invalid_token(self, client):
        """GET /api/employees with invalid token → 401"""
        resp = client.get("/api/employees", token_override="not_a_valid_token")
        assert resp.status_code == 401

    def test_malformed_bearer(self, client):
        """GET /api/employees with malformed Bearer → 401"""
        resp = client.get("/api/employees", token_override="Bearer ")
        assert resp.status_code == 401

    def test_expired_token(self, client):
        """GET /api/employees with expired token → 401"""
        expired = os.getenv("EXPIRED_TOKEN", "expired.jwt.token")
        resp = client.get("/api/employees", token_override=expired)
        assert resp.status_code == 401


# =============================================================================
# 2. Role Permission Tests — Admin (all should allow)
# =============================================================================


class TestAdminPermissions:
    """Admin has full access to all operations and all data."""

    def test_admin_can_list_employees(self, client):
        resp = client.get("/api/employees", role="admin")
        assert resp.status_code == 200

    def test_admin_can_get_any_employee(self, client):
        resp = client.get(f"/api/employees/{ALICE_ID}", role="admin")
        assert resp.status_code == 200

    def test_admin_can_get_cross_department_employee(self, client):
        """Admin can access employees from any department."""
        resp = client.get(f"/api/employees/{CHARLIE_ID}", role="admin")
        assert resp.status_code == 200

    def test_admin_can_create_employee(self, client):
        resp = client.post("/api/employees", role="admin", json={
            "name": "New Employee",
            "department": DEPT_1,
        })
        assert resp.status_code in (200, 201)

    def test_admin_can_update_any_employee(self, client):
        resp = client.put(f"/api/employees/{ALICE_ID}", role="admin", json={
            "name": "Updated Name",
        })
        assert resp.status_code == 200

    def test_admin_can_delete_employee(self, client):
        resp = client.delete(f"/api/employees/{BOB_ID}", role="admin")
        assert resp.status_code == 200


# =============================================================================
# 3. Role Permission Tests — Manager (positive)
# =============================================================================


class TestManagerPositivePermissions:
    """Manager can query, create, update within department scope."""

    def test_manager_can_list_department_employees(self, client):
        resp = client.get("/api/employees", role="manager")
        assert resp.status_code == 200

    def test_manager_can_get_department_employee(self, client):
        """Manager A (Engineering) can access Alice (Engineering)."""
        resp = client.get(f"/api/employees/{ALICE_ID}", role="manager")
        assert resp.status_code == 200

    def test_manager_can_create_employee(self, client):
        resp = client.post("/api/employees", role="manager", json={
            "name": "New Engineer",
            "department": DEPT_1,
        })
        assert resp.status_code in (200, 201)

    def test_manager_can_update_department_employee(self, client):
        resp = client.put(f"/api/employees/{ALICE_ID}", role="manager", json={
            "name": "Updated by Manager",
        })
        assert resp.status_code == 200


# =============================================================================
# 4. Role Permission Tests — Manager (negative: cannot delete)
# =============================================================================


class TestManagerNegativePermissions:
    """Manager cannot delete — this is admin-only."""

    def test_manager_cannot_delete_employee(self, client):
        """Vertical privilege escalation: manager → delete → 403"""
        resp = client.delete(f"/api/employees/{ALICE_ID}", role="manager")
        assert resp.status_code == 403

    def test_manager_cannot_delete_any_employee(self, client):
        resp = client.delete(f"/api/employees/{BOB_ID}", role="manager")
        assert resp.status_code == 403


# =============================================================================
# 5. Role Permission Tests — Employee (negative)
# =============================================================================


class TestEmployeeNegativePermissions:
    """Employee cannot list, create, or delete."""

    def test_employee_cannot_list_all_employees(self, client):
        resp = client.get("/api/employees", role="employee")
        assert resp.status_code == 403

    def test_employee_cannot_create_employee(self, client):
        resp = client.post("/api/employees", role="employee", json={
            "name": "Unauthorized",
        })
        assert resp.status_code == 403

    def test_employee_cannot_delete_any_employee(self, client):
        resp = client.delete(f"/api/employees/{ALICE_ID}", role="employee")
        assert resp.status_code == 403


# =============================================================================
# 6. Role Permission Tests — Employee (positive: self only)
# =============================================================================


class TestEmployeeSelfPermissions:
    """Employee can only view and update their own record."""

    def test_employee_can_view_own_record(self, client):
        """Alice can view her own employee record."""
        resp = client.get(f"/api/employees/{ALICE_ID}", role="employee")
        assert resp.status_code == 200

    def test_employee_can_update_own_record(self, client):
        """Alice can update her own employee record."""
        resp = client.put(f"/api/employees/{ALICE_ID}", role="employee", json={
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
        resp = client.get(f"/api/employees/{ALICE_ID}", role="manager")
        assert resp.status_code == 200

    def test_manager_a_cannot_access_marketing_employee(self, client):
        """Manager A (dept-1) CANNOT access Charlie (dept-2)."""
        resp = client.get(f"/api/employees/{CHARLIE_ID}", role="manager")
        assert resp.status_code == 403

    def test_manager_a_cannot_list_marketing_department(self, client):
        """Manager A (dept-1) CANNOT list Marketing department employees."""
        resp = client.get(f"/api/departments/{DEPT_2}/employees", role="manager")
        assert resp.status_code == 403

    def test_manager_b_cannot_access_engineering_employee(self, client):
        """Manager B (dept-2) CANNOT access Alice (dept-1)."""
        resp = client.get(f"/api/employees/{ALICE_ID}", role="manager")
        assert resp.status_code == 403

    def test_admin_can_access_all_departments(self, client):
        """Admin has no data scope restriction."""
        resp_eng = client.get(f"/api/employees/{ALICE_ID}", role="admin")
        resp_mkt = client.get(f"/api/employees/{CHARLIE_ID}", role="admin")
        assert resp_eng.status_code == 200
        assert resp_mkt.status_code == 200


# =============================================================================
# 8. Horizontal Privilege Escalation Tests
# =============================================================================


class TestHorizontalEscalation:
    """Verify employees cannot access other employees' records."""

    def test_alice_cannot_view_bob(self, client):
        """Alice (101) CANNOT view Bob's record (102) — same department."""
        resp = client.get(f"/api/employees/{BOB_ID}", role="employee")
        assert resp.status_code == 403

    def test_alice_cannot_update_bob(self, client):
        """Alice (101) CANNOT update Bob's record (102)."""
        resp = client.put(f"/api/employees/{BOB_ID}", role="employee", json={
            "name": "Hacked by Alice",
        })
        assert resp.status_code == 403

    def test_alice_cannot_view_charlie(self, client):
        """Alice (101) CANNOT view Charlie's record (201) — different department."""
        resp = client.get(f"/api/employees/{CHARLIE_ID}", role="employee")
        assert resp.status_code == 403

    def test_alice_cannot_delete_bob(self, client):
        """Alice (101) CANNOT delete Bob's record (102)."""
        resp = client.delete(f"/api/employees/{BOB_ID}", role="employee")
        assert resp.status_code == 403

    def test_bob_cannot_view_alice(self, client):
        """Bob (102) CANNOT view Alice's record (101) — reverse direction."""
        resp = client.get(f"/api/employees/{ALICE_ID}", role="employee")
        assert resp.status_code == 403


# =============================================================================
# 9. Vertical Privilege Escalation Tests
# =============================================================================


class TestVerticalEscalation:
    """Verify lower roles cannot perform higher-role operations."""

    def test_employee_cannot_admin_delete(self, client):
        """Employee → DELETE (admin-only) → 403"""
        resp = client.delete(f"/api/employees/{ALICE_ID}", role="employee")
        assert resp.status_code == 403

    def test_manager_cannot_admin_delete(self, client):
        """Manager → DELETE (admin-only) → 403"""
        resp = client.delete(f"/api/employees/{ALICE_ID}", role="manager")
        assert resp.status_code == 403

    def test_employee_cannot_create(self, client):
        """Employee → CREATE (manager+only) → 403"""
        resp = client.post("/api/employees", role="employee", json={
            "name": "Unauthorized Create",
        })
        assert resp.status_code == 403

    def test_employee_cannot_list_all(self, client):
        """Employee → LIST (manager+only) → 403"""
        resp = client.get("/api/employees", role="employee")
        assert resp.status_code == 403


# =============================================================================
# 10. Parameter Tampering Tests
# =============================================================================


class TestParameterTampering:
    """Verify that modifying identity/scope parameters does not bypass permissions."""

    def test_employee_tampers_department_in_update(self, client):
        """Alice tries to change her department to Marketing via self-update."""
        resp = client.put(f"/api/employees/{ALICE_ID}", role="employee", json={
            "departmentId": DEPT_2,
        })
        if resp.status_code == 200:
            body = resp.json()
            assert body.get("departmentId") != DEPT_2 or body.get("department") != DEPT_2, (
                "VULNERABILITY: departmentId was accepted from employee self-update"
            )

    def test_employee_tampers_role_in_update(self, client):
        """Alice tries to elevate her role to admin via self-update."""
        resp = client.put(f"/api/employees/{ALICE_ID}", role="employee", json={
            "role": "admin",
        })
        if resp.status_code == 200:
            body = resp.json()
            assert body.get("role") != "admin", (
                "VULNERABILITY: role was accepted from employee self-update — role injection"
            )

    def test_employee_tampers_employee_id_in_create(self, client):
        """Employee tries to create with a specific employeeId and role."""
        resp = client.post("/api/employees", role="employee", json={
            "name": "Fake Admin",
            "employeeId": 999,
            "role": "manager",
        })
        assert resp.status_code == 403, (
            "Employee should not be able to create employees at all"
        )

    def test_manager_tampers_department_query(self, client):
        """Manager A tries to query Marketing department via query parameter."""
        resp = client.get(
            "/api/employees",
            role="manager",
            params={"departmentId": DEPT_2},
        )
        if resp.status_code == 200:
            body = resp.json()
            employees = body.get("data", body.get("employees", []))
            for emp in employees:
                assert emp.get("department") != DEPT_2 and emp.get("departmentId") != DEPT_2, (
                    "VULNERABILITY: Manager accessed other department data via parameter tampering"
                )

    def test_employee_tampers_owner_id_in_update(self, client):
        """Alice tries to update Bob's record by changing the path ID."""
        resp = client.put(f"/api/employees/{BOB_ID}", role="employee", json={
            "name": "Tampered by Alice",
            "ownerId": BOB_ID,
        })
        assert resp.status_code == 403


# =============================================================================
# 11. Batch Authorization Tests
# =============================================================================


class TestBatchAuthorization:
    """Verify batch operations enforce per-item permission checks."""

    def test_employee_batch_own_and_other(self, client):
        """Alice batch queries [101, 102] — should only get 101."""
        resp = client.post("/api/employees/batch", role="employee", json={
            "ids": [ALICE_ID, BOB_ID],
        })
        assert resp.status_code in (200, 403)
        if resp.status_code == 200:
            body = resp.json()
            results = body.get("data", body.get("results", []))
            returned_ids = [item.get("id") or item.get("employeeId") for item in results]
            assert BOB_ID not in returned_ids, (
                f"VULNERABILITY: Batch returned unauthorized employee {BOB_ID}"
            )

    def test_employee_batch_all_unauthorized(self, client):
        """Alice batch queries [102, 201] — should get nothing."""
        resp = client.post("/api/employees/batch", role="employee", json={
            "ids": [BOB_ID, CHARLIE_ID],
        })
        if resp.status_code == 200:
            body = resp.json()
            results = body.get("data", body.get("results", []))
            assert len(results) == 0, (
                "VULNERABILITY: Batch returned data for all-unauthorized IDs"
            )

    def test_manager_batch_own_dept_and_other_dept(self, client):
        """Manager A batch queries [101 (dept-1), 201 (dept-2)] — should only get 101."""
        resp = client.post("/api/employees/batch", role="manager", json={
            "ids": [ALICE_ID, CHARLIE_ID],
        })
        assert resp.status_code in (200, 403)
        if resp.status_code == 200:
            body = resp.json()
            results = body.get("data", body.get("results", []))
            returned_ids = [item.get("id") or item.get("employeeId") for item in results]
            assert CHARLIE_ID not in returned_ids, (
                f"VULNERABILITY: Batch returned out-of-scope employee {CHARLIE_ID}"
            )


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
